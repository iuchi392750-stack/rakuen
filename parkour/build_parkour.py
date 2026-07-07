# -*- coding: utf-8 -*-
"""
build_parkour.py — Mixamo FBX から 30 秒のパルクール・シーンを自動構築する Blender スクリプト

使い方:
    blender -b -P build_parkour.py -- --anims ./anims --out ./out
    blender -b -P build_parkour.py -- --anims ./anims --out ./out --render

処理内容:
  1. anims/ フォルダの FBX をファイル名順に読み込む(最初の 1 本が With Skin、以降は Without Skin 推奨)
  2. すべてのアクションを 1 体のアーマチュアにまとめ、NLA でブレンドしながら順番に再生
  3. 各クリップの腰(Hips)の移動量・向きを解析し、キャラクターが同じ場所にワープして
     戻らないようにワールド位置と向きを自動でオフセット(ルートモーションの連結)
  4. ファイル名のキーワード(vault / slide / climb)から障害物ブロックを自動配置
  5. 腰を滑らかに追いかけるハンドヘルド風カメラを作成
  6. 30fps / 1280x720 / MP4 のプレビュー出力を設定し、.blend を保存(--render で即レンダリング)

出来上がったプレビュー動画を Seedance 2.0 の video_reference に渡すことを想定しています。
"""

import bpy
import math
import os
import re
import sys
from mathutils import Euler, Matrix, Vector

# ---------------------------------------------------------------- 設定 --

FPS = 30                 # Mixamo の FBX は 30fps なので合わせる
TARGET_SECONDS = 30      # 目標尺。足りない分はループ可能なクリップの繰り返しで自動的に埋める
DEFAULT_BLEND = 12       # クリップの繋ぎ目でブレンドするフレーム数
LOOP_BLEND = 4           # 同じクリップを繰り返すときのブレンドフレーム数
LOOP_KEYWORD = "running" # この文字列を含むクリップは尺埋めの繰り返しに使ってよい
CAMERA_OFFSET = Vector((-3.5, -5.5, 2.0))   # 腰から見たカメラの位置(ワールド)
CAMERA_BAKE_STEP = 4     # カメラ追従ターゲットのキーを打つ間隔(大きいほど滑らか)
RESOLUTION = (1280, 720)

# ファイル名ごとの上書き設定(任意)。キーはファイル名(拡張子なし)。
#   blend      : このクリップへ入るときのブレンドフレーム数
#   yaw_extra  : 追加で回転させる角度(度)。曲がるコースにしたいときに使う
#   obstacle   : "box" / "bar" / "wall" / None  (自動判定を上書き)
#   repeat     : このクリップをその場で何回連続再生するか
#   loop       : True なら尺埋めの自動繰り返しに使ってよい(既定は名前に running を含むもの)
CLIP_OVERRIDES = {
    # "02_vault": {"blend": 15, "yaw_extra": 0, "obstacle": "box"},
}

# ファイル名キーワード → 障害物の自動判定
OBSTACLE_KEYWORDS = {
    "vault": "box",
    "slide": "bar",
    "climb": "wall",
}

HIPS_CANDIDATES = ["mixamorig:Hips", "mixamorig_Hips", "Hips", "hips"]


# ------------------------------------------------------------ ユーティリティ --

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--anims", default="./anims", help="Mixamo FBX を入れたフォルダ")
    p.add_argument("--out", default="./out", help="出力フォルダ(.blend と動画)")
    p.add_argument("--render", action="store_true", help="構築後にそのままレンダリングする")
    p.add_argument("--fps", type=int, default=FPS)
    p.add_argument("--engine", choices=["eevee", "workbench", "cycles"], default="eevee",
                   help="レンダリングエンジン。GPU の無いサーバーでは workbench を推奨")
    p.add_argument("--seconds", type=float, default=TARGET_SECONDS,
                   help="目標の尺(秒)。足りない分は走りクリップの繰り返しで埋める")
    return p.parse_args(argv)


def find_hips(arm_obj):
    for name in HIPS_CANDIDATES:
        if name in arm_obj.pose.bones:
            return arm_obj.pose.bones[name]
    # 見つからなければ「親のないボーン」をルートとみなす
    for pb in arm_obj.pose.bones:
        if pb.parent is None:
            return pb
    raise RuntimeError("Hips ボーンが見つかりません: " + arm_obj.name)


def wrap_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def set_linear(fcurve, frames):
    for kp in fcurve.keyframe_points:
        if round(kp.co.x) in frames:
            kp.interpolation = "LINEAR"


# ------------------------------------------------------------ FBX の取り込み --

def import_clips(anim_dir):
    """FBX をファイル名順に読み込み、(ベースのアーマチュア, [(クリップ名, アクション), ...]) を返す"""
    files = sorted(
        f for f in os.listdir(anim_dir)
        if f.lower().endswith(".fbx")
    )
    if not files:
        raise RuntimeError("FBX が見つかりません: " + anim_dir)

    base_arm = None
    clips = []

    for i, fname in enumerate(files):
        path = os.path.join(anim_dir, fname)
        stem = os.path.splitext(fname)[0]
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        imported = [o for o in bpy.data.objects if o not in before]
        arms = [o for o in imported if o.type == "ARMATURE"]
        if not arms:
            print("警告: アーマチュアが無いのでスキップ:", fname)
            continue
        arm = arms[0]
        act = arm.animation_data.action if arm.animation_data else None
        if act is None:
            print("警告: アニメーションが無いのでスキップ:", fname)
        else:
            act.name = stem
            act.use_fake_user = True
            clips.append((stem, act))
            print(f"読み込み: {fname}  ({act.frame_range[0]:.0f}-{act.frame_range[1]:.0f}f)")

        if base_arm is None:
            base_arm = arm  # 1 本目(With Skin)は本体として残す
        else:
            for o in imported:  # 2 本目以降はアクションだけ貰って削除
                bpy.data.objects.remove(o, do_unlink=True)

    if base_arm is None:
        raise RuntimeError("使えるアーマチュアがありませんでした")
    if base_arm.animation_data is None:
        base_arm.animation_data_create()
    return base_arm, clips


# ------------------------------------------------ クリップの移動量・向きの解析 --

def analyze_clip(scene, arm, act):
    """アクション単体を再生して Hips のワールド位置と進行方向(先頭/末尾)を測る"""
    hips = find_hips(arm)
    arm.animation_data.action = act
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    f0 = max(f0, 1)

    def hips_at(f):
        scene.frame_set(f)
        return (arm.matrix_world @ hips.head).copy()

    p_start = hips_at(f0)
    p_start2 = hips_at(min(f0 + 5, f1))
    p_end2 = hips_at(max(f1 - 5, f0))
    p_end = hips_at(f1)
    p_mid = hips_at((f0 + f1) // 2)

    def heading(a, b):
        d = (b - a).xy
        return math.atan2(d.y, d.x) if d.length > 0.05 else None

    arm.animation_data.action = None
    return {
        "f0": f0, "f1": f1, "length": f1 - f0,
        "start": p_start, "end": p_end, "mid": p_mid,
        "h_start": heading(p_start, p_start2),
        "h_end": heading(p_end2, p_end),
    }


# ------------------------------------------------------------- NLA の組み立て --

def compute_blends(instances):
    """各繋ぎ目のブレンド幅を決める。

    - 同じクリップの繰り返しの間は LOOP_BLEND(ループは端の姿勢がほぼ同じなので短くてよい)
    - NLA はストリップを 2 本のトラックに交互に置くため、隣り合うブレンド区間が
      1 つのクリップの中で重なると同一トラック上で衝突する。
      そのため b[i] <= 前クリップの長さ - b[i-1] - 1 に必ずクランプする。
    """
    blends = [0]
    for i in range(1, len(instances)):
        cur, prev = instances[i], instances[i - 1]
        if cur["act"] is prev["act"]:
            b = LOOP_BLEND
        else:
            b = int(CLIP_OVERRIDES.get(cur["name"], {}).get("blend", DEFAULT_BLEND))
        b = min(b, prev["length"] - blends[i - 1] - 1, cur["length"] - 1)
        blends.append(max(b, 1))
    return blends


def total_frames(instances):
    return 1 + sum(inst["length"] for inst in instances) - sum(compute_blends(instances))


def build_plan(infos, fps):
    """クリップ列を組み立てる。repeat 指定を展開し、目標尺に足りなければ
    ループ可能なクリップ(名前に running を含む、または loop: True)を繰り返して埋める"""
    instances = []
    for info in infos:
        rep = max(1, int(CLIP_OVERRIDES.get(info["name"], {}).get("repeat", 1)))
        instances.extend([dict(info)] * rep)

    def loopable(inst):
        ov = CLIP_OVERRIDES.get(inst["name"], {})
        return bool(ov.get("loop", LOOP_KEYWORD in inst["name"].lower()))

    # 連続する同じクリップを (クリップ, 回数) のグループにまとめ、
    # ループ可能なグループへ順繰りに +1 して均等に尺を伸ばす
    groups = []
    for inst in instances:
        if groups and groups[-1][0]["act"] is inst["act"]:
            groups[-1][1] += 1
        else:
            groups.append([inst, 1])
    loop_groups = [g for g in groups if loopable(g[0])]

    def expand():
        out = []
        for info, count in groups:
            out.extend([dict(info)] * count)
        return out

    # 目標尺を超えない範囲まで繰り返しを足す(Seedance の 15 秒上限を超えないため)
    target = TARGET_SECONDS * fps
    added = 0
    while loop_groups and added <= 2000:
        gi = loop_groups[added % len(loop_groups)]
        gi[1] += 1
        if total_frames(expand()) > target:
            gi[1] -= 1
            break
        added += 1
    if not loop_groups and total_frames(expand()) < target:
        print("注意: ループ可能なクリップが無いため目標尺まで埋められません")
    if added:
        print(f"目標 {TARGET_SECONDS} 秒に合わせて走りクリップを {added} 回繰り返しました")
    return expand()


def key_influence(strip, points):
    """ストリップの影響度を直線補間でキーフレームする(クロスフェード用)"""
    strip.use_animated_influence = True
    fc = strip.fcurves.find("influence")
    for f, v in points:
        kp = fc.keyframe_points.insert(f, v)
        kp.interpolation = "LINEAR"


def build_nla(scene, arm, clips, fps):
    """クリップを NLA に並べ、ワープしないように delta_location/rotation をキーで補正する

    繋ぎ目の処理:
      - 奇数番目のクリップは上のトラック(B)に置き、影響度を 0→1(入り)/ 1→0(抜け)で
        直線的にクロスフェードする。NLA の自動ブレンドは両側が同時にフェードして
        レストポーズが混ざる(繋ぎ目でキャラが原点方向に引っ張られる)ため使わない。
      - 同じ区間で delta_location / delta_rotation も直線で切り替えるので、
        位置のオフセットとポーズのフェードが打ち消し合って腰の軌道が滑らかになる。
    """
    ad = arm.animation_data
    ad.action = None
    tracks = [ad.nla_tracks.new(), ad.nla_tracks.new()]  # 交互に使うとオーバーラップできる
    tracks[0].name, tracks[1].name = "parkour_A", "parkour_B"

    infos = []
    for name, act in clips:
        info = analyze_clip(scene, arm, act)
        info["name"], info["act"] = name, act
        infos.append(info)

    instances = build_plan(infos, fps)
    blends = compute_blends(instances)

    acc_loc = Vector((0.0, 0.0, 0.0))
    acc_yaw = 0.0
    cursor = 1
    ramp_frames = set()
    obstacles = []
    prev = None

    for i, info in enumerate(instances):
        ov = CLIP_OVERRIDES.get(info["name"], {})
        blend = blends[i]
        yaw_extra = math.radians(float(ov.get("yaw_extra", 0.0)))
        if prev is not None and prev["act"] is info["act"]:
            yaw_extra = 0.0  # 繰り返し中はコースが螺旋にならないよう追加回転しない

        if prev is not None:
            # 前クリップ末尾と今クリップ先頭の位置・向きが一致するようオフセットを更新
            d_yaw = 0.0
            if prev["h_end"] is not None and info["h_start"] is not None:
                d_yaw = wrap_angle(prev["h_end"] - info["h_start"])
            new_yaw = acc_yaw + d_yaw + yaw_extra
            prev_end_w = Matrix.Rotation(acc_yaw, 3, "Z") @ prev["end"] + acc_loc
            start_local_w = Matrix.Rotation(new_yaw, 3, "Z") @ info["start"]
            new_loc = prev_end_w - start_local_w
            new_loc.z = 0.0

            strip_start = cursor - blend
            # ブレンド区間の間にオフセットを線形に切り替える
            arm.delta_location = acc_loc
            arm.delta_rotation_euler = Euler((0, 0, acc_yaw))
            arm.keyframe_insert("delta_location", frame=strip_start)
            arm.keyframe_insert("delta_rotation_euler", frame=strip_start)
            arm.delta_location = new_loc
            arm.delta_rotation_euler = Euler((0, 0, new_yaw))
            arm.keyframe_insert("delta_location", frame=cursor)
            arm.keyframe_insert("delta_rotation_euler", frame=cursor)
            ramp_frames.update({strip_start, cursor})

            acc_loc, acc_yaw = new_loc, new_yaw
        else:
            arm.delta_location = acc_loc
            arm.delta_rotation_euler = Euler((0, 0, 0))
            arm.keyframe_insert("delta_location", frame=1)
            arm.keyframe_insert("delta_rotation_euler", frame=1)
            blend = 0

        strip_start = cursor - blend if prev is not None else 1
        track = tracks[i % 2]
        strip = track.strips.new(info["name"], int(strip_start), info["act"])
        strip.use_auto_blend = False
        strip.extrapolation = "NOTHING"
        strip_end = strip_start + info["length"]

        # クロスフェード: 上のトラック(奇数番)のストリップだけ影響度を直線で上げ下げする。
        # 入りは自分のフェードイン、抜けは次クリップとの重なりで自分をフェードアウト。
        if i % 2 == 1:
            key_influence(strip, [(strip_start, 0.0), (strip_start + blend, 1.0)])
        elif i > 0:
            prev_strip = tracks[1].strips[-1]  # 直前の上トラックのストリップ
            key_influence(prev_strip, [(strip_start, 1.0), (strip_start + blend, 0.0)])

        # 障害物の位置(クリップ中盤の腰位置の真下)を記録
        obs_kind = ov.get("obstacle")
        if obs_kind is None:
            for kw, kind in OBSTACLE_KEYWORDS.items():
                if kw in info["name"].lower():
                    obs_kind = kind
                    break
        if obs_kind:
            pos = Matrix.Rotation(acc_yaw, 3, "Z") @ info["mid"] + acc_loc
            obstacles.append((obs_kind, Vector((pos.x, pos.y, 0.0)), acc_yaw))

        cursor = strip_end
        prev = info

    # オフセットのキーを直線補間にする
    if arm.animation_data.action:
        for fc in arm.animation_data.action.fcurves:
            if fc.data_path.startswith("delta_"):
                set_linear(fc, ramp_frames | {1})

    scene.frame_start = 1
    scene.frame_end = int(cursor)
    total_sec = (cursor - 1) / fps
    print(f"合計: {int(cursor)} フレーム = {total_sec:.1f} 秒 (目標 {TARGET_SECONDS} 秒)")
    if total_sec < TARGET_SECONDS - 1:
        print("→ 足りない分はクリップを増やしてください(同じ FBX をコピーして"
              " 06_running2.fbx のように追加すれば繰り返せます)")
    return obstacles


# ------------------------------------------------------------------- 環境 --

def make_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    return mat


def paint_character(arm):
    """キャラクターを青一色にする。肌色のマネキンのままだと動画生成サービスの
    NSFW フィルターに誤検知されるため、参照動画では明確に人形と分かる色にする"""
    mat = make_material("pk_character", (0.05, 0.25, 0.85))
    for obj in arm.children_recursive:
        if obj.type == "MESH":
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            obj.color = (0.05, 0.25, 0.85, 1.0)


def build_environment(obstacles):
    ground_mat = make_material("pk_ground", (0.18, 0.18, 0.19))
    obs_mat = make_material("pk_obstacle", (0.55, 0.30, 0.12))

    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "Ground"
    ground.data.materials.append(ground_mat)
    ground.color = (0.18, 0.18, 0.19, 1.0)

    sizes = {
        "box":  (0.6, 1.4, 1.0),   # 跳び越え用ブロック
        "bar":  (0.15, 1.6, 1.1),  # スライディング用バー
        "wall": (0.4, 3.0, 3.0),   # 壁登り用の壁
    }
    for i, (kind, pos, yaw) in enumerate(obstacles):
        sx, sy, sz = sizes.get(kind, sizes["box"])
        bpy.ops.mesh.primitive_cube_add(location=(pos.x, pos.y, sz / 2))
        cube = bpy.context.object
        cube.name = f"Obstacle_{kind}_{i}"
        cube.scale = (sx / 2, sy / 2, sz / 2)
        cube.rotation_euler = (0, 0, yaw)
        cube.data.materials.append(obs_mat)
        cube.color = (0.75, 0.55, 0.15, 1.0)
        print(f"障害物 {kind} を配置: ({pos.x:.1f}, {pos.y:.1f}) — 位置は必要に応じて手で微調整してください")

    # ライティング
    bpy.ops.object.light_add(type="SUN", location=(10, -10, 20))
    sun = bpy.context.object
    sun.data.energy = 4.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.45, 0.55, 0.70, 1.0)  # 空っぽい色
        bg.inputs[1].default_value = 0.7


# ------------------------------------------------------------------ カメラ --

def build_camera(scene, arm, fps):
    hips = find_hips(arm)

    target = bpy.data.objects.new("CamTarget", None)
    dolly = bpy.data.objects.new("CamDolly", None)
    scene.collection.objects.link(target)
    scene.collection.objects.link(dolly)

    # NLA を評価しながら腰の位置をベイク(まばらなキー + ベジェ補間で自然に平滑化)
    for f in range(scene.frame_start, scene.frame_end + 1, CAMERA_BAKE_STEP):
        scene.frame_set(f)
        pos = arm.matrix_world @ hips.head
        target.location = pos + Vector((0, 0, 0.2))
        target.keyframe_insert("location", frame=f)
        dolly.location = pos + CAMERA_OFFSET
        dolly.keyframe_insert("location", frame=f)

    # 手持ちカメラ風の揺れをノイズモディファイアで追加
    if dolly.animation_data and dolly.animation_data.action:
        for fc in dolly.animation_data.action.fcurves:
            mod = fc.modifiers.new("NOISE")
            mod.scale = 25.0
            mod.strength = 0.15
            mod.phase = fc.array_index * 37.0

    cam_data = bpy.data.cameras.new("ParkourCam")
    cam_data.lens = 32
    cam = bpy.data.objects.new("ParkourCam", cam_data)
    scene.collection.objects.link(cam)
    cam.parent = dolly
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    scene.camera = cam


# ------------------------------------------------------------- レンダー設定 --

def setup_render(scene, out_dir, fps, engine="eevee"):
    r = scene.render
    r.fps = fps
    r.resolution_x, r.resolution_y = RESOLUTION
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "MEDIUM"
    r.filepath = os.path.join(out_dir, "parkour_preview.mp4")

    if engine == "workbench":
        r.engine = "BLENDER_WORKBENCH"
        # テクスチャ(肌色)ではなくオブジェクトに設定した色で塗る
        scene.display.shading.color_type = "OBJECT"
        scene.display.render_aa = "8"
    elif engine == "cycles":
        r.engine = "CYCLES"
        scene.cycles.samples = 32
    else:
        # EEVEE は Blender 4.2 以降で名前が変わった
        try:
            r.engine = "BLENDER_EEVEE"
        except TypeError:
            r.engine = "BLENDER_EEVEE_NEXT"


# -------------------------------------------------------------------- main --

def main():
    global TARGET_SECONDS
    args = parse_args()
    TARGET_SECONDS = args.seconds
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = args.fps

    arm, clips = import_clips(os.path.abspath(args.anims))
    obstacles = build_nla(scene, arm, clips, args.fps)
    paint_character(arm)
    build_environment(obstacles)
    build_camera(scene, arm, args.fps)
    setup_render(scene, out_dir, args.fps, args.engine)

    blend_path = os.path.join(out_dir, "parkour.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("保存しました:", blend_path)

    if args.render:
        print("レンダリング開始…")
        bpy.ops.render.render(animation=True)
        out = scene.render.filepath
        # GPU の無い環境では EEVEE が空ファイルを出して静かに失敗することがある
        if os.path.getsize(out) < 10_000:
            print("出力が空です。Workbench エンジンで再試行します…")
            scene.render.engine = "BLENDER_WORKBENCH"
            bpy.ops.render.render(animation=True)
        print("完了:", out)


if __name__ == "__main__":
    main()
