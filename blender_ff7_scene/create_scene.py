"""
FF7風スチームパンク都市シーン自動生成スクリプト
Blender 4.x 対応

使い方:
  blender --background --python create_scene.py

注意: assetsフォルダに flower_girl_fall.fbx と passerby_walk.fbx を配置してから実行してください。
"""

import bpy
import math
import os
import sys
import json
from pathlib import Path
from mathutils import Vector, Euler

# -----------------------------------------------------------------------
# パス解決
# -----------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "config.json"
ASSETS_DIR  = SCRIPT_DIR / "assets"
OUTPUT_DIR  = SCRIPT_DIR / "output"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------------------------------------------
# 前処理
# -----------------------------------------------------------------------
def check_assets(cfg: dict) -> bool:
    """assetsフォルダ・モデルの存在確認。不足があれば案内を出してFalseを返す。"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    missing = []
    for key, model in cfg["models"].items():
        p = SCRIPT_DIR / model["file"]
        if not p.exists():
            missing.append(str(p.relative_to(SCRIPT_DIR)))

    if missing:
        print("\n" + "=" * 60)
        print("【エラー】必要なモデルファイルが見つかりません")
        print("=" * 60)
        for m in missing:
            print(f"  ✗ {m}")
        print()
        print("以下の構成でファイルを配置してください：")
        print()
        print("  blender_ff7_scene/")
        print("  └── assets/")
        print("      ├── flower_girl_fall.fbx   ← 少女（転倒アニメ付きリグ）")
        print("      └── passerby_walk.fbx      ← 通行人男（歩行アニメ付きリグ）")
        print()
        print("推奨入手先: https://www.mixamo.com/")
        print("  - flower_girl_fall.fbx : キャラ選択 → Anim: 'Falling Back' or 'Stumble Backwards'")
        print("  - passerby_walk.fbx    : キャラ選択 → Anim: 'Walking'")
        print("  ※ Download設定: Format=FBX, Skin=With Skin, FPS=24")
        print("=" * 60 + "\n")
        return False
    return True


def reset_scene():
    """シーン全削除（メッシュ・アーマチュア・カメラ・ライト・コレクション）"""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # 残留メッシュデータを削除
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.armatures):
        bpy.data.armatures.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
    for block in list(bpy.data.cameras):
        bpy.data.cameras.remove(block)
    for block in list(bpy.data.lights):
        bpy.data.lights.remove(block)

    # World
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")


# -----------------------------------------------------------------------
# マテリアル
# -----------------------------------------------------------------------
def make_material(name: str, color: tuple, roughness: float = 0.8,
                  emission: tuple = None, emission_strength: float = 1.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness

    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


# -----------------------------------------------------------------------
# 道路・歩道・地面
# -----------------------------------------------------------------------
def create_road(cfg: dict):
    sc = cfg["scene"]
    road_w = sc["road_width"]
    road_l = sc["road_length"]
    sw      = sc["sidewalk_width"]

    def plane(name, w, d, loc, mat):
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (w, d, 1)
        bpy.ops.object.transform_apply(scale=True)
        obj.data.materials.append(mat)
        return obj

    road_mat  = make_material("RoadMat",      (0.08, 0.08, 0.08), roughness=0.9)
    side_mat  = make_material("SidewalkMat",  (0.55, 0.50, 0.45), roughness=0.85)
    ground_mat = make_material("GroundMat",   (0.12, 0.10, 0.08), roughness=0.95)

    # 大地
    plane("Ground", road_l * 2, road_l * 2, (0, 0, -0.01), ground_mat)
    # 車道
    plane("Road",   road_w, road_l, (0, -road_w * 0.0, 0), road_mat)
    # 歩道（右側 = +X）
    plane("Sidewalk_R", sw, road_l, (road_w / 2 + sw / 2, 0, 0.03), side_mat)
    # 歩道（左側 = -X）
    plane("Sidewalk_L", sw, road_l, (-road_w / 2 - sw / 2, 0, 0.03), side_mat)

    # 車道の白線
    line_mat = make_material("LineMat", (0.9, 0.9, 0.7), roughness=0.6)
    for i in range(-4, 5):
        lx = i * 1.5
        bpy.ops.mesh.primitive_plane_add(size=1, location=(lx, 0, 0.005))
        ln = bpy.context.active_object
        ln.name = f"Line_{i}"
        ln.scale = (0.08, 2.5, 1)
        bpy.ops.object.transform_apply(scale=True)
        ln.data.materials.append(line_mat)


# -----------------------------------------------------------------------
# スチームパンク建物
# -----------------------------------------------------------------------
def create_buildings(cfg: dict):
    sc  = cfg["scene"]
    n   = sc["building_count"]
    rl  = sc["road_length"]
    sw  = sc["sidewalk_width"]
    rw  = sc["road_width"]

    dark_mat   = make_material("BldDark",   (0.15, 0.12, 0.10), roughness=0.7)
    brick_mat  = make_material("BldBrick",  (0.45, 0.28, 0.18), roughness=0.85)
    metal_mat  = make_material("BldMetal",  (0.25, 0.30, 0.35), roughness=0.4)
    window_mat = make_material("BldWindow", (0.6, 0.55, 0.3), roughness=0.1,
                               emission=(0.9, 0.75, 0.4), emission_strength=2.5)

    def box(name, loc, dims, mat):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = dims
        bpy.ops.object.transform_apply(scale=True)
        obj.data.materials.append(mat)
        return obj

    spacing = rl / (n / 2)
    for side in [1, -1]:
        base_x = side * (rw / 2 + sw + 1.5)
        for i in range(n // 2):
            h = 8 + (i * 3 % 14)
            w = 3 + (i % 3)
            d = 3 + ((i + 1) % 3)
            y = -rl / 2 + spacing * i + spacing / 2
            z = h / 2

            mats = [dark_mat, brick_mat, metal_mat]
            mat  = mats[i % 3]
            bld  = box(f"Building_{side}_{i}", (base_x, y, z), (w, d, h), mat)

            # 窓（簡易：エミッションプレーン）
            for wl in range(2, int(h) - 1, 3):
                for wc in range(-1, 2):
                    wx = base_x + side * (w / 2 + 0.01)
                    wy = y + wc * 1.0
                    wz = wl + 0.5
                    bpy.ops.mesh.primitive_plane_add(size=0.7, location=(wx, wy, wz))
                    win = bpy.context.active_object
                    win.name = f"Win_{side}_{i}_{wl}_{wc}"
                    win.rotation_euler = (0, math.radians(90), 0)
                    win.data.materials.append(window_mat)

    # 煙突・パイプ（装飾）
    pipe_mat = make_material("PipeMat", (0.3, 0.3, 0.3), roughness=0.5)
    for k in range(6):
        px = (k % 3 - 1) * 4.0
        py = -10 + k * 5.0
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=4, location=(px + 6, py, 12))
        cyl = bpy.context.active_object
        cyl.name = f"Chimney_{k}"
        cyl.data.materials.append(pipe_mat)


# -----------------------------------------------------------------------
# 花（落下・踏まれ）
# -----------------------------------------------------------------------
def create_flowers(cfg: dict, girl_pos: list) -> bpy.types.Object:
    anim   = cfg["animation"]
    drop_f = anim["flower_drop_frame"]
    stomp_s = anim["flower_stomp_start_frame"]
    stomp_e = anim["flower_stomp_end_frame"]

    flower_mat = make_material("FlowerMat", (0.9, 0.2, 0.3), roughness=0.6,
                               emission=(1.0, 0.3, 0.4), emission_strength=0.3)
    stem_mat   = make_material("StemMat",   (0.15, 0.6, 0.15), roughness=0.8)

    # 花束コレクション用エンプティ
    bpy.ops.object.empty_add(type="PLAIN_AXES",
                             location=(girl_pos[0] - 0.3, girl_pos[1] + 0.2, 0.0))
    bunch = bpy.context.active_object
    bunch.name = "FlowerBunch"

    child_objects = []

    # 花びら 5輪
    for i in range(5):
        angle = i * (math.tau / 5)
        fx = bunch.location.x + math.cos(angle) * 0.25
        fy = bunch.location.y + math.sin(angle) * 0.25
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(fx, fy, 0.12),
                                             segments=8, ring_count=6)
        petal = bpy.context.active_object
        petal.name = f"Flower_{i}"
        petal.parent = bunch
        petal.data.materials.append(flower_mat)
        child_objects.append(petal)

        # 茎
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.3,
                                            location=(fx, fy, 0.0))
        stem = bpy.context.active_object
        stem.name = f"Stem_{i}"
        stem.parent = bunch
        stem.data.materials.append(stem_mat)
        child_objects.append(stem)

    # 花束＋子オブジェクト全部を drop_frame まで非表示
    all_flower_objs = [bunch] + child_objects
    for obj in all_flower_objs:
        obj.hide_viewport = True
        obj.hide_render   = True
        obj.keyframe_insert("hide_viewport", frame=1)
        obj.keyframe_insert("hide_render",   frame=1)
        obj.hide_viewport = False
        obj.hide_render   = False
        obj.keyframe_insert("hide_viewport", frame=drop_f)
        obj.keyframe_insert("hide_render",   frame=drop_f)

    # 踏まれてZ方向に潰れる
    bunch.scale = (1, 1, 1)
    bunch.keyframe_insert("scale", frame=stomp_s)
    bunch.scale = (1.4, 1.4, 0.05)
    bunch.keyframe_insert("scale", frame=stomp_e)

    return bunch


# -----------------------------------------------------------------------
# 車
# -----------------------------------------------------------------------
def create_cars(cfg: dict):
    car_body_default = make_material("CarBody", (0.5, 0.1, 0.1), roughness=0.3)
    glass_mat        = make_material("CarGlass", (0.3, 0.5, 0.8), roughness=0.05)
    wheel_mat        = make_material("WheelMat", (0.05, 0.05, 0.05), roughness=0.9)

    for idx, car_cfg in enumerate(cfg["cars"]):
        start = Vector(car_cfg["start"])
        end   = Vector(car_cfg["end"])
        fs    = car_cfg["frame_start"]
        fe    = car_cfg["frame_end"]
        color = car_cfg.get("color", [0.5, 0.1, 0.1])

        body_mat = make_material(f"CarBody_{idx}", color, roughness=0.3)

        # ボディ
        bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(start))
        body = bpy.context.active_object
        body.name = f"Car_{idx}"
        body.scale = (1.8, 4.0, 0.9)
        bpy.ops.object.transform_apply(scale=True)
        body.data.materials.append(body_mat)
        body.location.z = 0.45

        # ルーフ
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.9))
        roof = bpy.context.active_object
        roof.name = f"CarRoof_{idx}"
        roof.scale = (1.4, 2.2, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        roof.data.materials.append(body_mat)
        roof.parent = body

        # ガラス（フロント）
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.1, 0.4))
        glass = bpy.context.active_object
        glass.name = f"CarGlass_{idx}"
        glass.scale = (1.3, 0.05, 0.5)
        bpy.ops.object.transform_apply(scale=True)
        glass.data.materials.append(glass_mat)
        glass.parent = body

        # ホイール 4個
        for wi, (wx, wy) in enumerate([(-0.9, 1.2), (0.9, 1.2), (-0.9, -1.2), (0.9, -1.2)]):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.25,
                                                location=(wx, wy, -0.35))
            whl = bpy.context.active_object
            whl.name = f"Wheel_{idx}_{wi}"
            whl.rotation_euler = (math.radians(90), 0, 0)
            whl.data.materials.append(wheel_mat)
            whl.parent = body

        # 走行アニメーション
        body.location = start.copy()
        body.location.z = 0.45
        body.keyframe_insert("location", frame=fs)

        body.location = end.copy()
        body.location.z = 0.45
        body.keyframe_insert("location", frame=fe)

        # 向きを進行方向に合わせる
        direction = end - start
        angle = math.atan2(direction.x, direction.y)
        body.rotation_euler = (0, 0, angle)


# -----------------------------------------------------------------------
# ライト
# -----------------------------------------------------------------------
def create_lights(cfg: dict):
    # 太陽光（強め）
    bpy.ops.object.light_add(type="SUN", location=(5, -10, 20))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))
    sun.data.energy = 8.0
    sun.data.color  = (1.0, 0.85, 0.65)

    # アンビエント補助（エリアライト・強め）
    bpy.ops.object.light_add(type="AREA", location=(0, 0, 18))
    amb = bpy.context.active_object
    amb.name = "Ambient"
    amb.data.energy = 200.0
    amb.data.size   = 30.0
    amb.data.color  = (0.6, 0.65, 0.9)

    # 追加エリアライト（正面から）
    bpy.ops.object.light_add(type="AREA", location=(0, -15, 10))
    front = bpy.context.active_object
    front.name = "FrontLight"
    front.rotation_euler = (math.radians(60), 0, 0)
    front.data.energy = 150.0
    front.data.size   = 20.0
    front.data.color  = (1.0, 0.95, 0.9)

    # 街灯 x3
    pole_mat   = make_material("PoleMat",  (0.3, 0.3, 0.3), roughness=0.5)
    light_mat  = make_material("LampMat",  (1.0, 0.9, 0.6), roughness=0.1,
                               emission=(1.0, 0.9, 0.6), emission_strength=5.0)
    for i, lx in enumerate([-8, 0, 8]):
        # ポール（歩道脇・カメラの邪魔にならない位置）
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=6.0, location=(lx, 7.0, 3.0))
        pole = bpy.context.active_object
        pole.name = f"LampPole_{i}"
        pole.data.materials.append(pole_mat)

        # ランプヘッド
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(lx, 7.0, 6.1), segments=8, ring_count=6)
        head = bpy.context.active_object
        head.name = f"LampHead_{i}"
        head.data.materials.append(light_mat)

        # ポイントライト
        bpy.ops.object.light_add(type="POINT", location=(lx, 7.0, 6.0))
        lgt = bpy.context.active_object
        lgt.name = f"StreetLight_{i}"
        lgt.data.energy = 400.0
        lgt.data.color  = (1.0, 0.88, 0.6)
        lgt.data.shadow_soft_size = 0.5


# -----------------------------------------------------------------------
# 霧（ボリューム）
# -----------------------------------------------------------------------
def create_fog(cfg: dict):
    density = cfg["scene"]["fog_density"]
    world = bpy.context.scene.world
    world.use_nodes = True
    wn = world.node_tree.nodes
    wn.clear()

    bg = wn.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value    = (0.4, 0.45, 0.6, 1.0)
    bg.inputs["Strength"].default_value = 2.0

    # ボリュームノード名はBlenderバージョンによって異なる
    vol = None
    for node_type in ("ShaderNodeVolumePrincipled", "ShaderNodeVolumePrincipaled", "ShaderNodeVolumeScatter"):
        try:
            vol = wn.new(node_type)
            break
        except RuntimeError:
            continue

    out = wn.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(bg.outputs["Background"], out.inputs["Surface"])
    if vol is not None:
        try:
            vol.inputs["Density"].default_value    = density
            vol.inputs["Anisotropy"].default_value = 0.2
        except KeyError:
            pass
        world.node_tree.links.new(vol.outputs["Volume"], out.inputs["Volume"])


# -----------------------------------------------------------------------
# カメラ（4段階シネマティック降下）
# -----------------------------------------------------------------------
def create_camera(cfg: dict) -> bpy.types.Object:
    """
    カメラパス設計：
    F1   : 上空から街全体を見下ろす（俯瞰）
    F90  : 斜め降下しながら通りが見える（車・男・少女が全員見える）
    F180 : 男が少女に近づく瞬間を横から捉える
    F250 : 衝突・転倒・花が落ちるシーンを寄りで捉える
    F360 : 倒れた少女・踏まれた花・去る男の後ろ姿
    """
    total = cfg["animation"]["total_frames"]

    bpy.ops.object.camera_add(location=(0, -3, 38))
    cam = bpy.context.active_object
    cam.name = "MainCamera"
    bpy.context.scene.camera = cam
    cam.data.lens = 28
    try:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = 5.6
    except Exception:
        pass

    def kf(loc, rot_deg, frame):
        cam.location = loc
        cam.rotation_euler = tuple(math.radians(r) for r in rot_deg)
        cam.keyframe_insert("location",       frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)

    # F1: 真上から街を見下ろす
    kf((0.0,  -3.0, 38.0), (8,  0, 0),   1)

    # F90: 斜め降下・通り全体が見える（男が左から歩いてくるのが見える）
    kf((-4.0, -10.0, 18.0), (48, 0, 0),  90)

    # F180: 男が少女に近づく（やや横からのアングル）
    kf((-2.0, -7.0,  8.0),  (58, 0, 5), 180)

    # F250: 衝突・転倒シーン（低いアングル、少女と男の両方が見える）
    kf((1.0,  -5.0,  4.0),  (65, 0, 8), 250)

    # F360: 倒れた少女・花・去る男（最終ショット）
    kf((2.5,  -4.0,  2.5),  (70, 0, 12), 360)

    # BEZIER補間
    if cam.animation_data and cam.animation_data.action:
        try:
            for fc in cam.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type  = "AUTO_CLAMPED"
                    kp.handle_right_type = "AUTO_CLAMPED"
        except (AttributeError, TypeError):
            pass

    return cam


# -----------------------------------------------------------------------
# モデル読み込み
# -----------------------------------------------------------------------
def import_fbx(filepath: str, name_hint: str) -> bpy.types.Object:
    """FBXを読み込み、最上位オブジェクト（アーマチュア or メッシュ）を返す"""
    before = set(bpy.data.objects.keys())

    bpy.ops.import_scene.fbx(
        filepath=filepath,
        use_anim=True,
        automatic_bone_orientation=True,
        force_connect_children=False,
        ignore_leaf_bones=False,
        use_image_search=True,
    )

    new_objs = [bpy.data.objects[k] for k in bpy.data.objects.keys() if k not in before]

    # アーマチュアを最優先で選ぶ
    root = None
    for obj in new_objs:
        if obj.type == "ARMATURE" and obj.parent is None:
            root = obj
            break
    if root is None:
        for obj in new_objs:
            if obj.parent is None:
                root = obj
                break
    if root is None and new_objs:
        root = new_objs[0]

    if root:
        root.name = name_hint

    # NLAトラックを有効化してアニメーションを再生状態にする
    for obj in new_objs:
        if obj.animation_data:
            # アクションを直接再生
            if obj.animation_data.action:
                obj.animation_data.action.use_fake_user = True
            # NLAトラックを有効化
            for track in obj.animation_data.nla_tracks:
                track.mute = False
                for strip in track.strips:
                    strip.mute = False

    return root


def place_model(obj: bpy.types.Object, model_cfg: dict):
    """モデルをconfigの位置・スケール・回転に設定"""
    if obj is None:
        return
    # positionがない場合はwalk_routeの最初の点を使う
    if "position" in model_cfg:
        obj.location = model_cfg["position"]
    elif "walk_route" in model_cfg:
        obj.location = model_cfg["walk_route"][0]
    obj.scale    = model_cfg["scale"]
    rx, ry, rz   = model_cfg["rotation_euler_deg"]
    obj.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))


def set_keyframe(obj, frame, location=None, rotation_deg=None, scale=None):
    """オブジェクトにキーフレームをセットするヘルパー"""
    bpy.context.scene.frame_set(frame)
    if location is not None:
        obj.location = location
        obj.keyframe_insert("location", frame=frame)
    if rotation_deg is not None:
        obj.rotation_euler = tuple(math.radians(r) for r in rotation_deg)
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def animate_passerby(obj: bpy.types.Object, cfg: dict):
    """
    通行人の動きをすべてキーフレームで制御。
    FBXアニメーションに依存しない。
    歩行：X軸方向に移動（上下ボブで歩行感を出す）
    衝突：少女の位置で一瞬止まり前傾
    立ち去り：そのまま歩き続ける
    """
    if obj is None:
        return

    anim = cfg["animation"]
    coll = anim["collision_frame"]
    total = anim["total_frames"]
    sc = cfg["models"]["passerby"]["scale"]
    rx = cfg["models"]["passerby"]["rotation_euler_deg"][0]

    # 初期スケール・向き
    girl_x = cfg["models"]["flower_girl"]["position"][0]

    # 歩行ボブ（上下0.05mの揺れ）
    def bob(f):
        return math.sin(f * 0.4) * 0.05

    # F1: 画面左端に登場
    set_keyframe(obj, 1,
        location=(-13.0, 0.5, 0.0),
        rotation_deg=(rx, 0, 90))  # X軸正方向を向く

    # F1〜collision: 歩行移動（ボブあり）
    steps = 12
    for i in range(1, steps + 1):
        f = int(1 + (coll - 10 - 1) * i / steps)
        x = -13.0 + (girl_x - 0.3 - (-13.0)) * i / steps
        z = bob(f)
        set_keyframe(obj, f, location=(x, 0.5, z))

    # collision-5: 少女の直前（衝突直前）
    set_keyframe(obj, coll - 5,
        location=(girl_x - 0.5, 0.5, 0.0))

    # collision: 衝突・前傾姿勢
    set_keyframe(obj, coll,
        location=(girl_x + 0.2, 0.5, 0.0),
        rotation_deg=(rx, 0, 90))

    # collision+10: 衝突後もそのまま歩く
    set_keyframe(obj, coll + 10,
        location=(girl_x + 1.5, 0.5, 0.0))

    # 花を踏むフレーム
    stomp_s = anim["flower_stomp_start_frame"]
    stomp_e = anim["flower_stomp_end_frame"]
    flower_x = cfg["models"]["flower_girl"]["position"][0] - 0.3

    set_keyframe(obj, stomp_s - 5,
        location=(flower_x - 0.5, 0.5, 0.0))
    set_keyframe(obj, stomp_s,
        location=(flower_x, 0.5, 0.0))
    set_keyframe(obj, stomp_e,
        location=(flower_x + 0.5, 0.5, 0.0))

    # 最終: 画面右端へ退場
    set_keyframe(obj, total,
        location=(14.0, 0.5, 0.0))

    print("[Anim] Passerby walk animated (programmatic)")


def animate_girl_fall(obj: bpy.types.Object, cfg: dict):
    """
    花売り少女の動きをキーフレームで制御。
    立っている → 衝突でよろける → 倒れる
    """
    if obj is None:
        return

    anim = cfg["animation"]
    fall_f = anim["fall_start_frame"]
    coll   = anim["collision_frame"]
    total  = anim["total_frames"]
    pos    = cfg["models"]["flower_girl"]["position"]
    sc     = cfg["models"]["flower_girl"]["scale"]
    rx     = cfg["models"]["flower_girl"]["rotation_euler_deg"][0]

    # F1〜fall_start: 直立して立っている
    set_keyframe(obj, 1,
        location=(pos[0], pos[1], pos[2]),
        rotation_deg=(rx, 0, 180),
        scale=sc)

    set_keyframe(obj, fall_f - 1,
        location=(pos[0], pos[1], pos[2]),
        rotation_deg=(rx, 0, 180))

    # fall_start〜collision: よろける（後ろに傾く）
    set_keyframe(obj, fall_f,
        location=(pos[0], pos[1] + 0.1, pos[2]),
        rotation_deg=(rx - 10, 0, 180))

    set_keyframe(obj, coll,
        location=(pos[0] + 0.3, pos[1] + 0.3, pos[2]),
        rotation_deg=(rx - 30, 0, 175))

    # collision後: 地面に倒れる
    set_keyframe(obj, coll + 15,
        location=(pos[0] + 0.5, pos[1] + 0.8, pos[2]),
        rotation_deg=(rx - 70, 0, 170))

    set_keyframe(obj, coll + 25,
        location=(pos[0] + 0.6, pos[1] + 1.2, 0.0),
        rotation_deg=(0, 0, 170))  # 地面に横たわる

    # 倒れたまま静止
    set_keyframe(obj, total,
        location=(pos[0] + 0.6, pos[1] + 1.2, 0.0),
        rotation_deg=(0, 0, 170))

    print("[Anim] Girl fall animated (programmatic)")


def set_animation_range(cfg: dict):
    scene = bpy.context.scene
    anim  = cfg["animation"]
    scene.frame_start = 1
    scene.frame_end   = anim["total_frames"]
    scene.render.fps  = anim["fps"]


# -----------------------------------------------------------------------
# レンダー設定
# -----------------------------------------------------------------------
def configure_render(cfg: dict):
    rc    = cfg["render"]
    scene = bpy.context.scene
    scene.render.resolution_x           = rc["resolution_x"]
    scene.render.resolution_y           = rc["resolution_y"]
    scene.render.resolution_percentage  = 100
    scene.render.fps                    = rc["fps"]
    scene.render.filepath = str(SCRIPT_DIR / "output" / "flower_scene_reference")

    # MP4出力を試みる。Blender 5.xではFFMPEGが使えない場合はPNG連番にフォールバック
    try:
        scene.render.image_settings.file_format  = "FFMPEG"
        scene.render.ffmpeg.format               = "MPEG4"
        scene.render.ffmpeg.codec                = "H264"
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scene.render.ffmpeg.ffmpeg_preset        = "GOOD"
        print("[Render] Output: MP4 (H.264)")
    except TypeError:
        scene.render.image_settings.file_format = "PNG"
        frames_dir = SCRIPT_DIR / "output" / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(frames_dir / "frame_")
        print("[Render] FFMPEG unavailable - using PNG sequence")
        print(f"[Render] Frames: {frames_dir}")

    # レンダーエンジン選択（Blender 5.x: WorkbenchはPNG連番でも確実に明るく出力）
    for engine in ("BLENDER_WORKBENCH", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            print(f"[Render] Engine: {engine}")
            break
        except TypeError:
            continue

    # Workbench設定（明るく・カラー表示）
    if scene.render.engine == "BLENDER_WORKBENCH":
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        print("[Render] Workbench: STUDIO lighting with MATERIAL colors")

    if scene.render.engine.startswith("BLENDER_EEVEE") and hasattr(scene, "eevee"):
        eevee = scene.eevee
        if hasattr(eevee, "use_bloom"):
            eevee.use_bloom       = True
            eevee.bloom_intensity = 0.3
        if hasattr(eevee, "use_gtao"):
            eevee.use_gtao       = True
            eevee.gtao_distance  = 0.5


# -----------------------------------------------------------------------
# メイン
# -----------------------------------------------------------------------
def main():
    print("\n" + "=" * 60)
    print("FF7風シーン自動生成スクリプト 開始")
    print("=" * 60)

    cfg = load_config()

    if not check_assets(cfg):
        sys.exit(1)

    print("[1/9] シーンをリセット中...")
    reset_scene()

    print("[2/9] アニメーション・レンダー設定...")
    set_animation_range(cfg)
    configure_render(cfg)

    print("[3/9] 道路・歩道を生成中...")
    create_road(cfg)

    print("[4/9] 建物を生成中...")
    create_buildings(cfg)

    print("[5/9] 車を生成中...")
    create_cars(cfg)

    print("[6/9] ライト・霧を設定中...")
    create_lights(cfg)
    create_fog(cfg)

    print("[7/9] カメラを配置中...")
    create_camera(cfg)

    print("[8/9] キャラクターモデルを読み込み中...")
    girl_cfg      = cfg["models"]["flower_girl"]
    passerby_cfg  = cfg["models"]["passerby"]

    girl_path     = str(SCRIPT_DIR / girl_cfg["file"])
    passerby_path = str(SCRIPT_DIR / passerby_cfg["file"])

    girl_obj     = import_fbx(girl_path,     "FlowerGirl")
    passerby_obj = import_fbx(passerby_path, "Passerby")

    place_model(girl_obj,     girl_cfg)
    place_model(passerby_obj, passerby_cfg)

    # キャラクターのアニメーションをすべてコードで制御
    print("[8b] 通行人の歩行アニメーションを生成中...")
    animate_passerby(passerby_obj, cfg)

    print("[8c] 少女の転倒アニメーションを生成中...")
    animate_girl_fall(girl_obj, cfg)

    print("[9/9] 花を生成中...")
    create_flowers(cfg, girl_cfg["position"])

    # .blend保存（任意）
    blend_out = str(SCRIPT_DIR / "output" / "ff7_scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)

    print("\n" + "=" * 60)
    print("シーン生成完了！")
    print(f"  Blendファイル: {blend_out}")
    print(f"  次のステップ : render_viewport.py を実行してMP4を書き出す")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
