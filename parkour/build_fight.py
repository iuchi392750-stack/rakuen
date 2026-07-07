# -*- coding: utf-8 -*-
"""
build_fight.py — Mixamo を使わず、2 体のブロック人形の対戦シーンを一から構築する

使い方:
    blender -b -P build_fight.py -- --out ./out_fight --render

参考画像(Blender Reference)と同じ構成:
  - 赤と青のブロック人形が向かい合ってスパーリング(ジャブ・ブロック・ダッキング・キック)
  - 薄いグレーの床に黄色/グレーのブロックが散らばる環境
  - スタジオライト+影付きの Workbench レンダリング(GPU 不要で高速)

アニメーションはすべて Python によるキーフレームの手付け。
出来上がった動画を Seedance 2.0 の video_reference に渡して実写化する。
"""

import bpy
import math
import os
import random
import sys
from mathutils import Euler, Vector

FPS = 30
SECONDS = 15
RES = (1280, 720)

D = math.radians  # 度→ラジアン


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="./out_fight")
    p.add_argument("--render", action="store_true")
    return p.parse_args(argv)


# ------------------------------------------------------------ リグとメッシュ --

# name: (head, tail, parent)  — +Y が正面
BONES = {
    "hips":       ((0, 0, 1.02), (0, 0, 1.22), None),
    "torso":      ((0, 0, 1.22), (0, 0, 1.52), "hips"),
    "head":       ((0, 0, 1.52), (0, 0, 1.80), "torso"),
    "upperarm.L": ((0.24, 0, 1.46), (0.55, 0, 1.46), "torso"),
    "forearm.L":  ((0.55, 0, 1.46), (0.85, 0, 1.46), "upperarm.L"),
    "upperarm.R": ((-0.24, 0, 1.46), (-0.55, 0, 1.46), "torso"),
    "forearm.R":  ((-0.55, 0, 1.46), (-0.85, 0, 1.46), "upperarm.R"),
    "thigh.L":    ((0.12, 0, 1.02), (0.12, 0, 0.55), "hips"),
    "shin.L":     ((0.12, 0, 0.55), (0.12, 0, 0.10), "thigh.L"),
    "foot.L":     ((0.12, 0, 0.10), (0.12, 0.22, 0.06), "shin.L"),
    "thigh.R":    ((-0.12, 0, 1.02), (-0.12, 0, 0.55), "hips"),
    "shin.R":     ((-0.12, 0, 0.55), (-0.12, 0, 0.10), "thigh.R"),
    "foot.R":     ((-0.12, 0, 0.10), (-0.12, 0.22, 0.06), "shin.R"),
}

# ボーンごとの直方体の断面サイズ (幅 x, 奥行 y)
BOX = {
    "hips": (0.34, 0.22), "torso": (0.40, 0.24), "head": (0.24, 0.26),
    "upperarm.L": (0.11, 0.11), "forearm.L": (0.10, 0.10),
    "upperarm.R": (0.11, 0.11), "forearm.R": (0.10, 0.10),
    "thigh.L": (0.14, 0.15), "shin.L": (0.12, 0.13), "foot.L": (0.11, 0.10),
    "thigh.R": (0.14, 0.15), "shin.R": (0.12, 0.13), "foot.R": (0.11, 0.10),
}


def make_material(name, color, roughness=0.6):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = (*color, 1.0)  # Workbench の MATERIAL 表示用
    return mat


def build_fighter(name, color):
    """ブロック人形 1 体(アーマチュア+ボーンごとの直方体メッシュ)を作る"""
    arm_data = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    ebs = {}
    for bname, (head, tail, parent) in BONES.items():
        eb = arm_data.edit_bones.new(bname)
        eb.head, eb.tail = Vector(head), Vector(tail)
        if parent:
            eb.parent = ebs[parent]
        ebs[bname] = eb
    bpy.ops.object.mode_set(mode="OBJECT")

    verts, faces, groups = [], [], {}
    for bname, (head, tail, _) in BONES.items():
        h, t = Vector(head), Vector(tail)
        axis = t - h
        w, d = BOX[bname]
        # ボーン軸に沿った直方体(縦ボーンは z、足など前向きボーンは軸方向に伸ばす)
        base = len(verts)
        n = axis.normalized()
        up = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((0, 1, 0))
        side = n.cross(up).normalized()
        up2 = side.cross(n).normalized()
        c = (h + t) / 2
        half_len = axis.length / 2 * 0.94
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                for s3 in (-1, 1):
                    verts.append(c + n * (s1 * half_len)
                                 + side * (s2 * w / 2) + up2 * (s3 * d / 2))
        cube_faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                      (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        faces += [tuple(base + i for i in f) for f in cube_faces]
        groups[bname] = list(range(base, base + 8))

    mesh = bpy.data.meshes.new(name + "_body")
    mesh.from_pydata(verts, [], faces)
    body = bpy.data.objects.new(name + "_body", mesh)
    bpy.context.scene.collection.objects.link(body)
    for bname, idxs in groups.items():
        vg = body.vertex_groups.new(name=bname)
        vg.add(idxs, 1.0, "REPLACE")
    body.parent = arm
    body.modifiers.new("Armature", "ARMATURE").object = arm

    mat = make_material(name + "_mat", color)
    body.data.materials.append(mat)

    arm.animation_data_create()
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return arm


# ------------------------------------------------------------------ ポーズ --
#
# ポーズは「ボーンをフィギュア空間でどの方向に向けるか」で指定する。
# フィギュア空間: +Y = 正面, +X = 左手側, +Z = 上。
# 回転はエイム先の方向から逆算するので、パンチは必ず相手の方向に出る。

GUARD = {
    "torso": (0, 0.15, 0.99), "head": (0, 0.05, 1.0),
    "upperarm.L": (0.30, 0.75, -0.55), "forearm.L": (0.05, 0.55, 0.85),
    "upperarm.R": (-0.30, 0.75, -0.55), "forearm.R": (-0.05, 0.55, 0.85),
    "thigh.L": (0.10, 0.30, -0.95), "shin.L": (0.08, -0.10, -0.99),
    "thigh.R": (-0.10, -0.25, -0.95), "shin.R": (-0.08, -0.05, -0.99),
}


def pose(base, **over):
    p = dict(base)
    p.update({k.replace("_", "."): v for k, v in over.items()})
    return p


JAB_L = pose(GUARD, **{"upperarm.L": (0.05, 0.99, 0.10), "forearm.L": (0.0, 0.99, 0.06),
                       "torso": (0, 0.30, 0.95)})
JAB_R = pose(GUARD, **{"upperarm.R": (-0.05, 0.99, 0.10), "forearm.R": (0.0, 0.99, 0.06),
                       "torso": (0, 0.30, 0.95)})
BLOCK = pose(GUARD, **{"upperarm.L": (0.40, 0.60, -0.30), "forearm.L": (0.10, 0.25, 0.96),
                       "upperarm.R": (-0.40, 0.60, -0.30), "forearm.R": (-0.10, 0.25, 0.96),
                       "torso": (0, 0.22, 0.97)})
LEAN_BACK = pose(GUARD, **{"torso": (0, -0.45, 0.89), "head": (0, -0.35, 0.94),
                           "thigh.L": (0.10, 0.45, -0.89)})
DUCK = pose(GUARD, **{"torso": (0, 0.75, 0.66), "head": (0, 0.70, 0.70),
                      "thigh.L": (0.10, 0.45, -0.89), "shin.L": (0.0, -0.50, -0.86),
                      "thigh.R": (-0.10, 0.40, -0.91), "shin.R": (0.0, -0.55, -0.83)})
KICK_R = pose(GUARD, **{"thigh.R": (-0.05, 0.85, 0.30), "shin.R": (-0.05, 0.98, -0.10),
                        "torso": (0, -0.25, 0.97),
                        "upperarm.L": (0.60, 0.30, -0.35), "upperarm.R": (-0.60, 0.10, -0.45)})
BODY_HIT = pose(GUARD, **{"torso": (0, 0.55, 0.83), "head": (0, 0.50, 0.85),
                          "upperarm.L": (0.50, 0.30, -0.80), "forearm.L": (0.20, 0.60, 0.50),
                          "upperarm.R": (-0.50, 0.30, -0.80), "forearm.R": (-0.20, 0.60, 0.50)})

# 親→子の順に向きを決める必要がある
BONE_ORDER = ["torso", "head",
              "upperarm.L", "forearm.L", "upperarm.R", "forearm.R",
              "thigh.L", "shin.L", "thigh.R", "shin.R"]

_last_quat = {}  # (アーマチュア名, ボーン名) → 前回のクォータニオン(符号の連続性用)


def aim_bone(arm, pb, target, frame):
    """ボーンの軸(ローカル +Y)がアーマチュア空間で target を向くように回転させてキーを打つ"""
    bpy.context.view_layer.update()
    P = pb.matrix.to_3x3()                    # 現在のポーズ行列(アーマチュア空間)
    cur = P @ Vector((0, 1, 0))
    R = cur.rotation_difference(Vector(target).normalized()).to_matrix()
    basis = pb.matrix_basis.to_3x3()
    q = (basis @ (P.inverted() @ R @ P)).to_quaternion()
    key = (arm.name, pb.name)
    if key in _last_quat and _last_quat[key].dot(q) < 0:
        q = -q  # 補間が最短経路になるよう符号を揃える
    _last_quat[key] = q.copy()
    pb.rotation_quaternion = q
    pb.keyframe_insert("rotation_quaternion", frame=frame)


def key_pose(arm, frame, p, loc=None, yaw=None, crouch=0.0):
    """1 フレームにポーズ・立ち位置・向き・沈み込みをまとめてキーフレーム"""
    hips = arm.pose.bones["hips"]
    hips.location = (0, 0, -crouch)
    hips.keyframe_insert("location", frame=frame)
    for bname in BONE_ORDER:
        if bname in p:
            aim_bone(arm, arm.pose.bones[bname], p[bname], frame)
    if loc is not None:
        arm.location = (loc[0], loc[1], 0)
        arm.keyframe_insert("location", frame=frame)
    if yaw is not None:
        arm.rotation_euler = (0, 0, D(yaw))
        arm.keyframe_insert("rotation_euler", frame=frame)


def add_bounce(arm):
    """待機中の細かい揺れをノイズモディファイアで足す(生きている感じを出す)"""
    act = arm.animation_data.action
    for fc in act.fcurves:
        if fc.data_path == 'pose.bones["hips"].location' and fc.array_index == 2:
            mod = fc.modifiers.new("NOISE")
            mod.scale = 9.0
            mod.strength = 0.035
        if fc.data_path.startswith('pose.bones["torso"]'):
            mod = fc.modifiers.new("NOISE")
            mod.scale = 14.0
            mod.strength = 0.02
            mod.phase = fc.array_index * 11.0


# ------------------------------------------------------------ 振り付け --

def sec(t):
    return int(t * FPS) + 1


def choreograph(red, blue):
    """15 秒のスパーリング。R=赤 B=青。向かい合って時計回りに回りながら攻防"""
    def place(t, ang_deg, dist=1.9, crouch_r=0.05, crouch_b=0.05,
              pr=GUARD, pb=GUARD, dr=0.0, db=0.0):
        """ang_deg: 2 人の対峙軸の回転。dr/db: 各自の前後ステップ(+で前へ)"""
        a = D(ang_deg)
        axis = Vector((math.sin(a), math.cos(a), 0))
        c = Vector((0, 0, 0))
        r_pos = c - axis * (dist / 2 - dr)
        b_pos = c + axis * (dist / 2 - db)
        key_pose(red, sec(t), pr, loc=(r_pos.x, r_pos.y),
                 yaw=-ang_deg, crouch=crouch_r)
        key_pose(blue, sec(t), pb, loc=(b_pos.x, b_pos.y),
                 yaw=180 - ang_deg, crouch=crouch_b)

    # --- タイムライン(秒, 対峙角度, 各ポーズ) ---
    place(0.0, 0, pr=GUARD, pb=GUARD)
    place(1.0, 10)                                   # 様子見で回り込み
    place(2.0, 20)
    place(2.6, 22, pr=JAB_L, dr=0.25)                # 赤: 左ジャブ
    place(2.9, 22, pb=LEAN_BACK, pr=JAB_L, dr=0.25)  # 青: 仰け反ってかわす
    place(3.3, 24, pr=GUARD, pb=GUARD)
    place(4.0, 28, pb=JAB_R, db=0.3)                 # 青: 右の反撃
    place(4.3, 28, pr=BLOCK, pb=JAB_R, db=0.3)       # 赤: ブロック
    place(4.8, 30, pr=GUARD, pb=GUARD)
    place(5.6, 24)                                   # 距離を取り直す
    place(6.2, 18, pr=JAB_R, dr=0.3)                 # 赤: 右ストレート
    place(6.5, 18, pb=DUCK, pr=JAB_R, dr=0.3, crouch_b=0.28)  # 青: ダッキング
    place(6.9, 16, pb=pose(BODY_HIT), db=0.35, crouch_b=0.12) # 青: ボディ打ち
    place(7.2, 16, pr=BODY_HIT)                      # 赤: 打たれて怯む
    place(7.8, 12, pr=GUARD, pb=GUARD, dist=2.3)     # 離れる
    place(8.8, 0, dist=2.4)                          # 逆回りで仕切り直し
    place(9.8, -12, dist=2.2)
    place(10.6, -18, pb=KICK_R, db=0.3, dist=2.0)    # 青: ミドルキック
    place(11.0, -18, pr=pose(BLOCK, torso=(0, 0.30, 0.95)), pb=KICK_R, db=0.3)
    place(11.5, -20, pr=GUARD, pb=GUARD, dist=2.1)
    place(12.3, -28, pr=JAB_L, dr=0.35)              # 赤: 踏み込んで左
    place(12.6, -28, pb=LEAN_BACK, pr=JAB_L, dr=0.35)
    place(13.0, -30, pr=JAB_R, dr=0.45)              # 赤: 返しの右
    place(13.3, -30, pb=pose(BODY_HIT, head=(0.20, 0.55, 0.80)), pr=JAB_R, dr=0.45)
    place(13.8, -32, pb=pose(GUARD, torso=(0, 0.35, 0.94)), dist=2.4)  # 青: 下がる
    place(14.8, -38, pr=GUARD, pb=GUARD, dist=2.2)   # ガードに戻して終わり

    add_bounce(red)
    add_bounce(blue)


# ------------------------------------------------------------------ 環境 --

def build_environment():
    floor_mat = make_material("floor", (0.62, 0.62, 0.63), roughness=0.9)
    yellow = make_material("block_y", (0.83, 0.62, 0.18))
    gray = make_material("block_g", (0.45, 0.45, 0.47))

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "Floor"
    floor.data.materials.append(floor_mat)

    rng = random.Random(7)
    for i in range(14):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(3.5, 9.0)
        s = rng.uniform(0.25, 1.1)
        h = s * rng.uniform(0.6, 2.2)
        bpy.ops.mesh.primitive_cube_add(
            location=(math.cos(ang) * dist, math.sin(ang) * dist, h / 2))
        cube = bpy.context.object
        cube.scale = (s, s, h / 2)
        cube.rotation_euler = (0, 0, rng.uniform(0, math.pi))
        cube.data.materials.append(yellow if rng.random() < 0.5 else gray)

    bpy.ops.object.light_add(type="SUN", location=(6, -6, 12))
    sun = bpy.context.object
    sun.data.energy = 3.5
    sun.data.angle = D(20)  # 柔らかい影
    sun.rotation_euler = (D(45), 0, D(35))

    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.75, 0.76, 0.78, 1.0)
        bg.inputs[1].default_value = 1.0


def build_camera(scene):
    target = bpy.data.objects.new("CamTarget", None)
    target.location = (0, 0, 1.15)
    scene.collection.objects.link(target)

    cam_data = bpy.data.cameras.new("FightCam")
    cam_data.lens = 45
    cam = bpy.data.objects.new("FightCam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (5.4, 0.6, 1.55)  # 対峙軸に対して横から(2 人が左右に見える)
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    scene.camera = cam

    # ごく僅かな手持ち揺れ
    cam.keyframe_insert("location", frame=1)
    act = cam.animation_data.action
    for fc in act.fcurves:
        mod = fc.modifiers.new("NOISE")
        mod.scale = 40.0
        mod.strength = 0.05
        mod.phase = fc.array_index * 23.0


def setup_render(scene, out_dir):
    r = scene.render
    r.fps = FPS
    r.resolution_x, r.resolution_y = RES
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.filepath = os.path.join(out_dir, "fight_reference.mp4")
    r.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.color_type = "MATERIAL"
    sh.light = "STUDIO"
    sh.show_shadows = True
    sh.show_cavity = True
    scene.display.render_aa = "16"


def main():
    args = parse_args()
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = SECONDS * FPS

    red = build_fighter("Red", (0.85, 0.22, 0.12))
    blue = build_fighter("Blue", (0.15, 0.30, 0.85))
    choreograph(red, blue)
    build_environment()
    build_camera(scene)
    setup_render(scene, out_dir)

    blend = os.path.join(out_dir, "fight.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("保存しました:", blend)
    if args.render:
        bpy.ops.render.render(animation=True)
        print("完了:", scene.render.filepath)


if __name__ == "__main__":
    main()
