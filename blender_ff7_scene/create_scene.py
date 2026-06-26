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

        # 茎
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.3,
                                            location=(fx, fy, 0.0))
        stem = bpy.context.active_object
        stem.name = f"Stem_{i}"
        stem.parent = bunch
        stem.data.materials.append(stem_mat)

    # 花束は drop_frame まで非表示
    bunch.hide_viewport = True
    bunch.hide_render   = True
    bunch.keyframe_insert("hide_viewport", frame=1)
    bunch.keyframe_insert("hide_render",   frame=1)

    bunch.hide_viewport = False
    bunch.hide_render   = False
    bunch.keyframe_insert("hide_viewport", frame=drop_f)
    bunch.keyframe_insert("hide_render",   frame=drop_f)

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
    # 太陽光（薄い夕方オレンジ）
    bpy.ops.object.light_add(type="SUN", location=(5, -10, 20))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))
    sun.data.energy = 2.0
    sun.data.color  = (1.0, 0.85, 0.65)

    # アンビエント補助（エリアライト）
    bpy.ops.object.light_add(type="AREA", location=(0, 0, 18))
    amb = bpy.context.active_object
    amb.name = "Ambient"
    amb.data.energy = 30.0
    amb.data.size   = 20.0
    amb.data.color  = (0.5, 0.55, 0.8)

    # 街灯 x3
    pole_mat   = make_material("PoleMat",  (0.3, 0.3, 0.3), roughness=0.5)
    light_mat  = make_material("LampMat",  (1.0, 0.9, 0.6), roughness=0.1,
                               emission=(1.0, 0.9, 0.6), emission_strength=5.0)
    for i, lx in enumerate([-8, 0, 8]):
        # ポール
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=6.0, location=(lx, 5.5, 3.0))
        pole = bpy.context.active_object
        pole.name = f"LampPole_{i}"
        pole.data.materials.append(pole_mat)

        # ランプヘッド
        bpy.ops.mesh.primitive_sphere_add(radius=0.3, location=(lx, 5.5, 6.1))
        head = bpy.context.active_object
        head.name = f"LampHead_{i}"
        head.data.materials.append(light_mat)

        # ポイントライト
        bpy.ops.object.light_add(type="POINT", location=(lx, 5.5, 6.0))
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
    bg.inputs["Color"].default_value    = (0.25, 0.22, 0.30, 1.0)
    bg.inputs["Strength"].default_value = 0.8

    vol = wn.new("ShaderNodeVolumePrincipaled")
    vol.inputs["Density"].default_value    = density
    vol.inputs["Anisotropy"].default_value = 0.2

    out = wn.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(bg.outputs["Background"],  out.inputs["Surface"])
    world.node_tree.links.new(vol.outputs["Volume"],     out.inputs["Volume"])


# -----------------------------------------------------------------------
# カメラ
# -----------------------------------------------------------------------
def create_camera(cfg: dict) -> bpy.types.Object:
    cam_cfg = cfg["camera"]
    total   = cfg["animation"]["total_frames"]

    bpy.ops.object.camera_add(location=cam_cfg["start_location"])
    cam = bpy.context.active_object
    cam.name = "MainCamera"

    bpy.context.scene.camera = cam

    cam.data.lens = 35
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 4.0

    def deg2rad3(d):
        return tuple(math.radians(x) for x in d)

    # キーフレーム: 開始
    cam.location = cam_cfg["start_location"]
    cam.rotation_euler = deg2rad3(cam_cfg["start_rotation_euler_deg"])
    cam.keyframe_insert("location",       frame=1)
    cam.keyframe_insert("rotation_euler", frame=1)

    # 中間（下降中）
    mid_f = total // 2
    cam.location = cam_cfg["mid_location"]
    cam.rotation_euler = deg2rad3(cam_cfg["mid_rotation_euler_deg"])
    cam.keyframe_insert("location",       frame=mid_f)
    cam.keyframe_insert("rotation_euler", frame=mid_f)

    # 終了（少女の近く）
    cam.location = cam_cfg["end_location"]
    cam.rotation_euler = deg2rad3(cam_cfg["end_rotation_euler_deg"])
    cam.keyframe_insert("location",       frame=total)
    cam.keyframe_insert("rotation_euler", frame=total)

    # イージング：BEZIER補間
    if cam.animation_data and cam.animation_data.action:
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type  = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"

    return cam


# -----------------------------------------------------------------------
# モデル読み込み
# -----------------------------------------------------------------------
def import_fbx(filepath: str, name_hint: str) -> bpy.types.Object:
    """FBXを読み込み、最上位オブジェクト（アーマチュア or メッシュ）を返す"""
    before = set(bpy.data.objects.keys())

    # Blender 4.x: bpy.ops.import_scene.fbx
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
    return root


def place_model(obj: bpy.types.Object, model_cfg: dict):
    """モデルをconfigの位置・スケール・回転に設定"""
    if obj is None:
        return
    obj.location = model_cfg["position"]
    obj.scale    = model_cfg["scale"]
    rx, ry, rz   = model_cfg["rotation_euler_deg"]
    obj.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))


def animate_passerby_walk(obj: bpy.types.Object, cfg: dict):
    """歩行ルートに沿って通行人を移動させる"""
    if obj is None:
        return

    route      = cfg["models"]["passerby"]["walk_route"]
    total      = cfg["animation"]["total_frames"]
    coll_frame = cfg["animation"]["collision_frame"]

    n_points = len(route)
    for i, pos in enumerate(route):
        f = int(1 + (coll_frame - 1) * i / (n_points - 1))
        obj.location = (pos[0], pos[1], pos[2])
        obj.keyframe_insert("location", frame=f)

    # 衝突後も少し進む
    last = route[-1]
    obj.location = (last[0], last[1], last[2])
    obj.keyframe_insert("location", frame=total)

    # 進行方向に向ける
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

    rx = cfg["models"]["passerby"]["rotation_euler_deg"][0]
    obj.rotation_euler.x = math.radians(rx)


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

    # FFMPEG対応確認（Blender 5.xでは利用不可の場合あり）
    available_formats = bpy.context.scene.render.image_settings.bl_rna.properties["file_format"].enum_items.keys()
    if "FFMPEG" in available_formats:
        scene.render.image_settings.file_format  = "FFMPEG"
        scene.render.ffmpeg.format               = "MPEG4"
        scene.render.ffmpeg.codec                = "H264"
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scene.render.ffmpeg.ffmpeg_preset        = "GOOD"
        print("[Render] 出力形式: MP4 (H.264)")
    else:
        # FFMPEGが使えない場合はPNGシーケンスで出力
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(SCRIPT_DIR / "output" / "frames" / "frame_")
        (SCRIPT_DIR / "output" / "frames").mkdir(parents=True, exist_ok=True)
        print("[Render] FFMPEG非対応のため PNG シーケンスで出力します")
        print(f"[Render] 出力先: {SCRIPT_DIR / 'output' / 'frames'}")
        print("[Render] レンダリング後、Blenderの Video Sequencer でMP4に変換してください")

    # レンダーエンジン選択（Blender 5.x対応）
    available_engines = [e.identifier for e in bpy.types.RenderEngine.__subclasses__()]
    if "BLENDER_EEVEE_NEXT" in bpy.context.preferences.addons.keys() or hasattr(scene, "eevee"):
        if "BLENDER_EEVEE_NEXT" in [e[0] for e in bpy.types.RenderEngine.bl_rna.properties.get("engine", {}).enum_items if hasattr(bpy.types.RenderEngine.bl_rna.properties.get("engine", {}), "enum_items")] if bpy.types.RenderEngine.bl_rna.properties.get("engine") else True:
            try:
                scene.render.engine = "BLENDER_EEVEE_NEXT"
            except TypeError:
                scene.render.engine = "BLENDER_EEVEE"

    print(f"[Render] エンジン: {scene.render.engine}")

    if scene.render.engine.startswith("BLENDER_EEVEE") and hasattr(scene, "eevee"):
        eevee = scene.eevee
        if hasattr(eevee, "use_bloom"):
            eevee.use_bloom       = True
            eevee.bloom_intensity = 0.3
        if hasattr(eevee, "use_gtao"):
            eevee.use_gtao       = True
            eevee.gtao_distance  = 0.5
        if hasattr(eevee, "use_volumetric_fog"):
            eevee.use_volumetric_fog = True


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

    # 通行人の歩行アニメーション（位置キーフレーム）
    animate_passerby_walk(passerby_obj, cfg)

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
