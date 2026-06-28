"""
build_scene.py
================
ファミレス（家庭餐厅）の夜のボックス席で、男女のキャラクターが向かい合って
パフェを食べる／話すシーンを Blender 上に「自動生成」するスクリプトです。

- 男性キャラと女性キャラがはっきり区別できる（髪・体型・服の色）
- 男性が右手のスプーンを口へ運ぶ「食べる」アニメーション（ループ）
- カメラがゆっくり寄っていくドリーイン
- ファミレスの席・テーブル・パフェ・夜景の窓・暖色の照明

実行方法（どちらでも可）:
  1) Blender を開いて Scripting タブにこのファイルを読み込み「実行」
  2) コマンドライン:
       blender --background --python build_scene.py
     ※ --background だとレンダリングまで自動で行います（OUTPUT 参照）

対応バージョン: Blender 4.x / 5.x（入力名のフォールバック対応済み）

「できるだけリアル」にするための差し替えポイントは README.md を参照してください
（MakeHuman / Mixamo を使った実写風キャラへの置き換え手順）。
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
FPS = 24
DURATION_SEC = 15           # 元動画と同じ長さ
FRAME_START = 1
FRAME_END = FPS * DURATION_SEC
RENDER_SAMPLES = 64         # きれいにしたいなら 128〜256 へ
RES_X, RES_Y = 1280, 720
OUTPUT_PATH = "//render/famires_"   # .blend と同じ場所の render/ に出力

# ブルーム（街灯・照明の滲み）。Blender 4.x のコンポジタは安定なので自動で有効、
# 5.x はコンポジタAPI刷新の影響でまれに白飛びすることがあるため既定で無効。
# 5.x でも使いたい場合は FORCE_BLOOM=True にしてください。
FORCE_BLOOM = False

# 服・髪の色（元動画に合わせる）
COL_MALE_JACKET = (0.05, 0.05, 0.06)     # 黒っぽいジャケット
COL_MALE_SHIRT  = (0.85, 0.85, 0.82)     # 白T
COL_FEMALE_KNIT = (0.82, 0.74, 0.62)     # クリーム/ベージュのニット
COL_HAIR_DARK   = (0.03, 0.02, 0.02)     # 黒髪
COL_SKIN        = (0.86, 0.66, 0.55)


# ---------------------------------------------------------------------------
# 共通ヘルパ
# ---------------------------------------------------------------------------
def clear_scene():
    """既存オブジェクト・データを全消去（まっさらから組み立てる）。"""
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights,
                 bpy.data.cameras, bpy.data.armatures):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def _set_input(bsdf, names, value):
    """Blender バージョン差を吸収して Principled BSDF の入力を設定する。"""
    if isinstance(names, str):
        names = [names]
    for n in names:
        if n in bsdf.inputs:
            try:
                bsdf.inputs[n].default_value = value
                return True
            except Exception:
                pass
    return False


def make_material(name, color=(0.8, 0.8, 0.8), roughness=0.5, metallic=0.0,
                  emission=None, emission_strength=0.0,
                  transmission=0.0, ior=1.45, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    _set_input(bsdf, "Base Color", (*color, 1.0))
    _set_input(bsdf, "Roughness", roughness)
    _set_input(bsdf, "Metallic", metallic)
    _set_input(bsdf, ["Transmission Weight", "Transmission"], transmission)
    _set_input(bsdf, "IOR", ior)
    _set_input(bsdf, "Alpha", alpha)
    if alpha < 1.0:
        try:
            mat.blend_method = "BLEND"
        except Exception:
            pass
    if emission is not None:
        _set_input(bsdf, ["Emission Color", "Emission"], (*emission, 1.0))
        _set_input(bsdf, "Emission Strength", emission_strength)
    return mat


def add_mesh_primitive(kind, name, location=(0, 0, 0), scale=(1, 1, 1),
                       rotation=(0, 0, 0), material=None, **kw):
    op = {
        "cube": bpy.ops.mesh.primitive_cube_add,
        "cylinder": bpy.ops.mesh.primitive_cylinder_add,
        "cone": bpy.ops.mesh.primitive_cone_add,
        "uv_sphere": bpy.ops.mesh.primitive_uv_sphere_add,
        "ico_sphere": bpy.ops.mesh.primitive_ico_sphere_add,
        "plane": bpy.ops.mesh.primitive_plane_add,
        "torus": bpy.ops.mesh.primitive_torus_add,
    }[kind]
    op(location=location, **kw)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    o.rotation_euler = rotation
    if material:
        o.data.materials.append(material)
    return o


def shade_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True


def link_to_collection(obj, coll):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


# ---------------------------------------------------------------------------
# 環境（床・窓・夜景・照明・ボックス席・テーブル）
# ---------------------------------------------------------------------------
def build_room(coll, mats):
    # 床（木目）
    floor = add_mesh_primitive("plane", "Floor", location=(0, 0, 0),
                               scale=(8, 8, 1), material=mats["floor"])

    # 壁（奥＝窓側 +Y、左右）
    back = add_mesh_primitive("plane", "Wall_Back", location=(0, 5.0, 1.6),
                              rotation=(math.radians(90), 0, 0),
                              scale=(8, 2.2, 1), material=mats["wall"])
    left = add_mesh_primitive("plane", "Wall_Left", location=(-5.0, 0, 1.6),
                              rotation=(0, math.radians(90), 0),
                              scale=(2.2, 5, 1), material=mats["wall"])

    # 天井
    ceil = add_mesh_primitive("plane", "Ceiling", location=(0, 0, 3.2),
                              scale=(8, 8, 1), material=mats["wall"])

    # 窓ガラス（半透明）と夜景プレート（発光）
    glass = add_mesh_primitive("plane", "Window_Glass", location=(0, 4.95, 1.7),
                               rotation=(math.radians(90), 0, 0),
                               scale=(6, 1.6, 1), material=mats["glass"])
    city = build_city_lights(coll, mats)

    # 窓枠（木）
    for x in (-4, -2, 0, 2, 4):
        add_mesh_primitive("cube", f"Mullion_{x}", location=(x, 4.93, 1.7),
                           scale=(0.04, 0.03, 1.6), material=mats["wood_dark"])

    return floor


def build_city_lights(coll, mats):
    """窓の外の夜景。発光プレート＋たくさんの小さな発光キューブ（街の灯り）。"""
    # ベースの暗い夜空プレート
    sky = add_mesh_primitive("plane", "Night_Sky", location=(0, 8.0, 1.7),
                             rotation=(math.radians(90), 0, 0),
                             scale=(12, 4, 1), material=mats["nightsky"])

    # 街の灯り（ランダム配置の発光ブロック）
    import random
    random.seed(7)
    warm = mats["citywarm"]
    cool = mats["citycool"]
    lights_mesh_objs = []
    for i in range(220):
        x = random.uniform(-9, 9)
        z = random.uniform(0.1, 2.6)
        y = random.uniform(6.5, 7.6)
        s = random.uniform(0.02, 0.09)
        m = warm if random.random() < 0.7 else cool
        o = add_mesh_primitive("cube", f"CityLight_{i}", location=(x, y, z),
                               scale=(s, s * 0.4, s * random.uniform(1, 3)),
                               material=m)
        lights_mesh_objs.append(o)
    return sky


def build_pendant_lamps(coll, mats):
    """天井から下がる暖色のペンダント照明（ジオメトリ＋実ライト）。"""
    positions = [(-2.2, 0.4), (0.0, 1.2), (2.2, 0.4), (-1.2, -1.4), (1.2, -1.4)]
    for i, (x, y) in enumerate(positions):
        # コード
        add_mesh_primitive("cylinder", f"Cord_{i}", location=(x, y, 2.95),
                           scale=(0.01, 0.01, 0.25), material=mats["wood_dark"],
                           vertices=8)
        # 笠（コーン）
        shade = add_mesh_primitive("cone", f"Shade_{i}", location=(x, y, 2.62),
                                   radius1=0.16, radius2=0.05, depth=0.22,
                                   material=mats["lampshade"])
        shade_smooth(shade)
        # 実ライト（暖色ポイント）
        ldata = bpy.data.lights.new(f"Pendant_{i}", type="POINT")
        ldata.energy = 60
        ldata.color = (1.0, 0.78, 0.5)
        ldata.shadow_soft_size = 0.12
        lo = bpy.data.objects.new(f"Pendant_{i}", ldata)
        lo.location = (x, y, 2.5)
        coll.objects.link(lo)


def build_booth(coll, mats, y_center, name):
    """ボックス席（座面＋背もたれ）を2つ（手前・奥）作る。"""
    objs = []
    # 座面
    seat = add_mesh_primitive("cube", f"{name}_Seat",
                              location=(0, y_center, 0.42),
                              scale=(0.95, 0.32, 0.07), material=mats["seat"])
    # 背もたれ
    back_y = y_center + (0.30 if y_center > 0 else -0.30)
    back = add_mesh_primitive("cube", f"{name}_Back",
                              location=(0, back_y, 0.85),
                              scale=(0.95, 0.06, 0.42), material=mats["seat"])
    # 木の台座（座面下）
    base = add_mesh_primitive("cube", f"{name}_Base",
                              location=(0, y_center, 0.2),
                              scale=(0.9, 0.3, 0.2), material=mats["wood"])
    objs += [seat, back, base]
    for o in objs:
        bpy.ops.object.shade_flat()
    return objs


def build_table(coll, mats):
    top = add_mesh_primitive("cube", "Table_Top", location=(0, 0, 0.72),
                             scale=(0.62, 0.42, 0.03), material=mats["table"])
    # 角を少し丸める
    bev = top.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.02
    bev.segments = 3
    leg = add_mesh_primitive("cylinder", "Table_Leg", location=(0, 0, 0.36),
                             scale=(0.06, 0.06, 0.36), material=mats["metal"],
                             vertices=16)
    foot = add_mesh_primitive("cylinder", "Table_Foot", location=(0, 0, 0.02),
                              scale=(0.22, 0.22, 0.02), material=mats["metal"],
                              vertices=24)
    return top


# ---------------------------------------------------------------------------
# パフェ・食器
# ---------------------------------------------------------------------------
def build_parfait(coll, mats, location, cream_color=(0.98, 0.95, 0.9)):
    x, y, z = location
    glass = add_mesh_primitive("cone", "Parfait_Glass", location=(x, y, z + 0.06),
                               radius1=0.05, radius2=0.07, depth=0.16,
                               material=mats["glass"], vertices=24)
    shade_smooth(glass)
    stem = add_mesh_primitive("cylinder", "Parfait_Stem",
                              location=(x, y, z - 0.04),
                              scale=(0.012, 0.012, 0.04),
                              material=mats["glass"], vertices=12)
    foot = add_mesh_primitive("cylinder", "Parfait_Foot",
                              location=(x, y, z - 0.08),
                              scale=(0.04, 0.04, 0.01),
                              material=mats["glass"], vertices=16)
    cream = make_material("ParfaitCream", cream_color, roughness=0.45)
    swirl = add_mesh_primitive("cone", "Parfait_Cream",
                               location=(x, y, z + 0.18),
                               radius1=0.06, radius2=0.0, depth=0.12,
                               material=cream, vertices=24)
    shade_smooth(swirl)
    # フルーツ（オレンジ）
    fruit = add_mesh_primitive("ico_sphere", "Parfait_Fruit",
                               location=(x + 0.04, y, z + 0.16),
                               scale=(0.025, 0.025, 0.025),
                               material=mats["fruit"], subdivisions=2)
    # チェリー
    cherry = add_mesh_primitive("uv_sphere", "Parfait_Cherry",
                                location=(x, y, z + 0.25),
                                scale=(0.018, 0.018, 0.018),
                                material=mats["cherry"])
    return glass


def build_coffee(coll, mats, location):
    x, y, z = location
    cup = add_mesh_primitive("cylinder", "Coffee_Cup", location=(x, y, z + 0.03),
                             scale=(0.045, 0.045, 0.03),
                             material=mats["porcelain"], vertices=24)
    shade_smooth(cup)
    coffee = add_mesh_primitive("cylinder", "Coffee_Liquid",
                                location=(x, y, z + 0.05),
                                scale=(0.038, 0.038, 0.002),
                                material=mats["coffee"], vertices=24)
    saucer = add_mesh_primitive("cylinder", "Coffee_Saucer",
                                location=(x, y, z + 0.005),
                                scale=(0.07, 0.07, 0.004),
                                material=mats["porcelain"], vertices=24)
    shade_smooth(saucer)
    return cup


def build_plate_cake(coll, mats, location):
    x, y, z = location
    plate = add_mesh_primitive("cylinder", "Plate", location=(x, y, z + 0.004),
                               scale=(0.08, 0.08, 0.004),
                               material=mats["porcelain"], vertices=32)
    shade_smooth(plate)
    # ケーキ（三角）
    cake = add_mesh_primitive("cube", "Cake", location=(x, y, z + 0.03),
                              scale=(0.05, 0.03, 0.025),
                              material=mats["cake"])
    return plate


# ---------------------------------------------------------------------------
# 人物（スキンモディファイア＋サブサーフで滑らかな人型）
# ---------------------------------------------------------------------------
def _skin_body(name, joints, edges, radii, location, material, subsurf=2):
    """頂点スケルトン＋スキンモディファイアで有機的な人体を作る。"""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    verts = [bm.verts.new(j) for j in joints]
    bm.verts.ensure_lookup_table()
    for a, b in edges:
        bm.edges.new((verts[a], verts[b]))
    bm.to_mesh(mesh)
    bm.free()

    skin = obj.modifiers.new("Skin", "SKIN")
    obj.data.skin_vertices[0].data  # ensure skin layer exists
    sv = obj.data.skin_vertices[0].data
    for i, r in enumerate(radii):
        sv[i].radius = (r, r)
    # ルート頂点（腰）をマーク
    try:
        sv[0].use_root = True
    except Exception:
        pass
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = subsurf
    sub.render_levels = subsurf

    obj.location = location
    if material:
        obj.data.materials.append(material)
    shade_smooth(obj)
    return obj


def build_person(name, location, facing, mat_body, mat_top, mat_hair,
                 female=False, with_right_arm=True):
    """
    座った人物を作る。facing は向き（+1 で +Y を向く / -1 で -Y を向く）。
    female=True で肩幅を狭く・腰を広く・髪を長く。
    with_right_arm=False のとき右の前腕・手を省く（後で可動アームを付ける用）。
    """
    f = facing
    # ローカル座標（後で location でオフセット、Y は facing で前後）
    # 座標系: x=左右, y=前後(顔の向き), z=上下
    # --- 胴体スケルトン ---
    hip_z = 0.0
    chest_z = 0.45
    neck_z = 0.62
    head_z = 0.78
    sh = 0.18 if not female else 0.15      # 肩半幅
    hipw = 0.13 if not female else 0.16    # 腰半幅

    # 太もも前方向（座っているので前に出る）
    joints = [
        (0.0, 0.0, hip_z),            # 0 hip(root)
        (0.0, 0.0, chest_z),          # 1 chest
        (0.0, 0.0, neck_z),           # 2 neck
        (0.0, 0.02 * f, head_z),      # 3 head
        # 左腕（テーブルに向かって伸びる）
        (-sh, 0.0, chest_z + 0.02),   # 4 L shoulder
        (-sh - 0.02, 0.18 * f, chest_z - 0.05),  # 5 L elbow
        (-0.10, 0.34 * f, chest_z - 0.10),       # 6 L hand
        # 右腕
        (sh, 0.0, chest_z + 0.02),    # 7 R shoulder
        (sh + 0.02, 0.18 * f, chest_z - 0.05),   # 8 R elbow
        (0.10, 0.34 * f, chest_z - 0.10),        # 9 R hand
        # 脚（座位：太ももは前、すねは下）
        (-hipw, 0.0, hip_z),          # 10 L hip
        (-hipw, 0.28 * f, hip_z - 0.02),  # 11 L knee
        (-hipw, 0.30 * f, hip_z - 0.40),  # 12 L foot
        (hipw, 0.0, hip_z),           # 13 R hip
        (hipw, 0.28 * f, hip_z - 0.02),   # 14 R knee
        (hipw, 0.30 * f, hip_z - 0.40),   # 15 R foot
    ]
    edges = [(0, 1), (1, 2), (2, 3),
             (1, 4), (4, 5), (5, 6),
             (1, 7), (7, 8), (8, 9),
             (0, 10), (10, 11), (11, 12),
             (0, 13), (13, 14), (14, 15)]
    # スキン半径（部位の太さ）
    radii = [
        0.16 if not female else 0.15,  # hip
        0.17 if not female else 0.15,  # chest
        0.06,                          # neck
        0.11,                          # head
        0.07, 0.05, 0.045,             # L arm
        0.07, 0.05, 0.045,             # R arm
        0.08, 0.06, 0.05,              # L leg
        0.08, 0.06, 0.05,              # R leg
    ]

    if not with_right_arm:
        # 右肘・右手を省く（可動アームを別途付ける）
        keep = list(range(0, 8)) + list(range(10, 16))
        index_map = {old: new for new, old in enumerate(keep)}
        joints = [joints[i] for i in keep]
        radii = [radii[i] for i in keep]
        edges = [(index_map[a], index_map[b]) for a, b in edges
                 if a in index_map and b in index_map]

    body = _skin_body(name + "_Body", joints, edges, radii,
                      location, mat_body, subsurf=2)

    # --- 服（上半身を覆う少し大きい胴体） ---
    top = add_mesh_primitive("uv_sphere", name + "_Top",
                             location=(location[0],
                                       location[1] + 0.0 * f,
                                       location[2] + 0.30),
                             scale=(0.24 if not female else 0.21, 0.17, 0.22),
                             material=mat_top)
    shade_smooth(top)

    # --- 頭（しっかり球で上書き：肌） ---
    head = add_mesh_primitive("uv_sphere", name + "_Head",
                              location=(location[0],
                                        location[1] + 0.02 * f,
                                        location[2] + head_z),
                              scale=(0.085, 0.095, 0.105),
                              material=mat_body)
    shade_smooth(head)

    # --- 髪 ---
    if female:
        # ロングヘア（頭を覆う＋後ろに長い）
        hair = add_mesh_primitive("uv_sphere", name + "_Hair",
                                  location=(location[0],
                                            location[1] - 0.02 * f,
                                            location[2] + head_z + 0.02),
                                  scale=(0.10, 0.11, 0.12),
                                  material=mat_hair)
        shade_smooth(hair)
        long_hair = add_mesh_primitive("cube", name + "_HairLong",
                                       location=(location[0],
                                                 location[1] - 0.07 * f,
                                                 location[2] + head_z - 0.12),
                                       scale=(0.09, 0.04, 0.16),
                                       material=mat_hair)
        b = long_hair.modifiers.new("Bevel", "BEVEL")
        b.width = 0.03
        shade_smooth(long_hair)
    else:
        # ショートヘア（頭の上半分を覆う、少し乱れ）
        hair = add_mesh_primitive("uv_sphere", name + "_Hair",
                                  location=(location[0],
                                            location[1] - 0.005 * f,
                                            location[2] + head_z + 0.03),
                                  scale=(0.095, 0.10, 0.085),
                                  material=mat_hair)
        shade_smooth(hair)

    return {"body": body, "head": head, "top": top}


def build_animated_arm(name, shoulder_world, mats):
    """
    可動の右腕（上腕・前腕・手・スプーン）を作り、肘ピボットの Empty を返す。
    肘 Empty を回転キーフレームすると「食べる」動作になる。
    """
    sx, sy, sz = shoulder_world
    skin = mats["skin"]

    # 肩〜肘（固定の上腕）
    upper = add_mesh_primitive("uv_sphere", name + "_Upper",
                               location=(sx + 0.05, sy + 0.10, sz - 0.04),
                               scale=(0.055, 0.10, 0.055), material=skin)
    upper.rotation_euler = (math.radians(60), 0, 0)
    shade_smooth(upper)

    # 肘ピボット
    elbow = bpy.data.objects.new(name + "_ElbowPivot", None)
    elbow.empty_display_size = 0.05
    bpy.context.scene.collection.objects.link(elbow)
    elbow.location = (sx + 0.07, sy + 0.20, sz - 0.08)

    # 前腕（肘ピボットの子）
    fore = add_mesh_primitive("uv_sphere", name + "_Fore",
                              location=(sx + 0.07, sy + 0.30, sz - 0.05),
                              scale=(0.045, 0.10, 0.045), material=skin)
    fore.rotation_euler = (math.radians(-70), 0, 0)
    shade_smooth(fore)

    # 手
    hand = add_mesh_primitive("uv_sphere", name + "_Hand",
                              location=(sx + 0.07, sy + 0.40, sz + 0.0),
                              scale=(0.04, 0.05, 0.03), material=skin)
    shade_smooth(hand)

    # スプーン（柄＋すくい部）
    handle = add_mesh_primitive("cylinder", name + "_SpoonHandle",
                                location=(sx + 0.07, sy + 0.46, sz + 0.04),
                                scale=(0.005, 0.005, 0.05),
                                material=mats["metal"], vertices=10)
    handle.rotation_euler = (math.radians(60), 0, 0)
    bowl = add_mesh_primitive("uv_sphere", name + "_SpoonBowl",
                              location=(sx + 0.07, sy + 0.50, sz + 0.10),
                              scale=(0.018, 0.025, 0.008),
                              material=mats["metal"])
    shade_smooth(bowl)

    # 親子付け：肘ピボット -> 前腕・手・スプーン
    for child in (fore, hand, handle, bowl):
        child.parent = elbow
        child.matrix_parent_inverse = elbow.matrix_world.inverted()

    return elbow


# ---------------------------------------------------------------------------
# アニメーション
# ---------------------------------------------------------------------------
def animate_eating(elbow):
    """肘ピボットを上下に回転させて「すくって口へ運ぶ」動作をループさせる。"""
    scene = bpy.context.scene
    base = elbow.rotation_euler.copy()
    cycle = FPS * 3          # 3秒で1すくい
    n = (FRAME_END - FRAME_START) // cycle + 1
    for k in range(n + 1):
        f0 = FRAME_START + k * cycle
        # すくう（下）
        elbow.rotation_euler = (base.x + math.radians(5), base.y, base.z)
        elbow.keyframe_insert("rotation_euler", frame=f0)
        # 口へ（上げる）
        elbow.rotation_euler = (base.x + math.radians(-55), base.y, base.z)
        elbow.keyframe_insert("rotation_euler", frame=f0 + cycle // 2)
        # 戻す
        elbow.rotation_euler = (base.x + math.radians(5), base.y, base.z)
        elbow.keyframe_insert("rotation_euler", frame=f0 + cycle)
    # 補間をなめらかに
    if elbow.animation_data and elbow.animation_data.action:
        for fc in _action_fcurves(elbow.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"


def animate_idle_sway(obj, amp_deg=1.5, period=FPS * 4):
    """微妙な揺れ（呼吸・相づち）で生っぽさを足す。"""
    base = obj.rotation_euler.copy()
    n = (FRAME_END - FRAME_START) // period + 1
    for k in range(n + 1):
        f0 = FRAME_START + k * period
        obj.rotation_euler = (base.x, base.y, base.z + math.radians(amp_deg))
        obj.keyframe_insert("rotation_euler", frame=f0)
        obj.rotation_euler = (base.x, base.y, base.z - math.radians(amp_deg))
        obj.keyframe_insert("rotation_euler", frame=f0 + period // 2)
        obj.rotation_euler = (base.x, base.y, base.z + math.radians(amp_deg))
        obj.keyframe_insert("rotation_euler", frame=f0 + period)


def _action_fcurves(action):
    """Blender 4.4+ のスロット式 action / 旧 action 両対応で fcurves を返す。"""
    fcs = list(getattr(action, "fcurves", []))
    if fcs:
        return fcs
    try:
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    fcs.extend(cb.fcurves)
    except Exception:
        pass
    return fcs


def setup_camera():
    """カメラ＋注視ターゲット。ゆっくり寄っていくドリーイン。"""
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 35
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    target = bpy.data.objects.new("CamTarget", None)
    target.location = (0, 0, 0.95)
    bpy.context.scene.collection.objects.link(target)

    track = cam.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # ドリーイン（遠い→近い、少し下げる）
    cam.location = (0.2, -3.6, 1.7)
    cam.keyframe_insert("location", frame=FRAME_START)
    cam.location = (-0.1, -2.0, 1.35)
    cam.keyframe_insert("location", frame=FRAME_END)
    if cam.animation_data and cam.animation_data.action:
        for fc in _action_fcurves(cam.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "SINE"
    return cam


# ---------------------------------------------------------------------------
# マテリアル一式
# ---------------------------------------------------------------------------
def build_materials():
    m = {}
    m["floor"] = make_material("Floor", (0.18, 0.11, 0.06), roughness=0.35)
    m["wall"] = make_material("Wall", (0.30, 0.22, 0.14), roughness=0.7)
    m["wood"] = make_material("Wood", (0.32, 0.18, 0.09), roughness=0.45)
    m["wood_dark"] = make_material("WoodDark", (0.12, 0.07, 0.04), roughness=0.5)
    m["table"] = make_material("TableTop", (0.55, 0.36, 0.18), roughness=0.25)
    m["seat"] = make_material("Seat", (0.35, 0.22, 0.15), roughness=0.8)
    m["metal"] = make_material("Metal", (0.6, 0.6, 0.62), roughness=0.25,
                               metallic=1.0)
    m["glass"] = make_material("Glass", (0.9, 0.95, 1.0), roughness=0.05,
                               transmission=0.95, ior=1.45, alpha=0.25)
    m["porcelain"] = make_material("Porcelain", (0.95, 0.95, 0.93),
                                   roughness=0.2)
    m["coffee"] = make_material("Coffee", (0.07, 0.04, 0.02), roughness=0.15)
    m["cake"] = make_material("Cake", (0.5, 0.32, 0.2), roughness=0.5)
    m["fruit"] = make_material("Fruit", (0.95, 0.55, 0.1), roughness=0.4)
    m["cherry"] = make_material("Cherry", (0.6, 0.04, 0.06), roughness=0.3)
    m["lampshade"] = make_material("LampShade", (1.0, 0.85, 0.6),
                                   emission=(1.0, 0.8, 0.5),
                                   emission_strength=6.0)
    m["nightsky"] = make_material("NightSky", (0.01, 0.012, 0.03),
                                  emission=(0.01, 0.015, 0.04),
                                  emission_strength=0.4)
    m["citywarm"] = make_material("CityWarm", (1.0, 0.8, 0.4),
                                  emission=(1.0, 0.7, 0.3),
                                  emission_strength=12.0)
    m["citycool"] = make_material("CityCool", (0.6, 0.8, 1.0),
                                  emission=(0.4, 0.7, 1.0),
                                  emission_strength=12.0)
    # 人物
    m["skin"] = make_material("Skin", COL_SKIN, roughness=0.45)
    _set_input(m["skin"].node_tree.nodes.get("Principled BSDF"),
               "Subsurface Weight", 0.15)
    m["male_jacket"] = make_material("MaleJacket", COL_MALE_JACKET, roughness=0.7)
    m["male_shirt"] = make_material("MaleShirt", COL_MALE_SHIRT, roughness=0.6)
    m["female_knit"] = make_material("FemaleKnit", COL_FEMALE_KNIT, roughness=0.85)
    m["hair"] = make_material("Hair", COL_HAIR_DARK, roughness=0.35)
    return m


def setup_world():
    world = bpy.data.worlds.new("World") if not bpy.data.worlds else bpy.data.worlds[0]
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.02, 0.018, 0.025, 1.0)  # 暗い夜
        bg.inputs[1].default_value = 0.3


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    # Cycles が使える環境なら高品質に（任意で有効化）
    try:
        if "CYCLES" in [e.identifier for e in
                        bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]:
            pass  # 既定は EEVEE。リアル重視なら次行を有効化:
            # scene.render.engine = "CYCLES"
    except Exception:
        pass
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.film_transparent = False
    scene.render.filepath = OUTPUT_PATH
    scene.render.image_settings.file_format = "PNG"
    # EEVEE 設定（バージョン差を吸収）
    ee = getattr(scene, "eevee", None)
    if ee:
        for attr, val in (("taa_render_samples", RENDER_SAMPLES),
                          ("use_raytracing", True),
                          ("use_bloom", True)):
            if hasattr(ee, attr):
                try:
                    setattr(ee, attr, val)
                except Exception:
                    pass
    # ブルーム（街灯・照明の滲み）をコンポジタの Glare で
    is_v5 = bpy.app.version[0] >= 5
    if FORCE_BLOOM or not is_v5:
        add_glare_bloom()
    else:
        print("bloom skipped on Blender %d.x (set FORCE_BLOOM=True to enable)"
              % bpy.app.version[0])


def add_glare_bloom():
    """街灯・照明の滲み（ブルーム）をコンポジタの Glare で足す。
    Blender 4.x（scene.node_tree）と 5.x（compositing_node_group）両対応。
    失敗してもシーン生成は止めない。"""
    scene = bpy.context.scene
    try:
        scene.use_nodes = True
    except Exception:
        pass

    # --- Blender 5.x: コンポジタは node group ---
    if hasattr(scene, "compositing_node_group"):
        try:
            ng = scene.compositing_node_group
            if ng is None:
                ng = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
                scene.compositing_node_group = ng
            nodes, links = ng.nodes, ng.links
            grp_in = next((n for n in nodes if n.type == "GROUP_INPUT"), None) \
                or nodes.new("NodeGroupInput")
            grp_out = next((n for n in nodes if n.type == "GROUP_OUTPUT"), None) \
                or nodes.new("NodeGroupOutput")
            # 入出力ソケットを用意
            if not ng.interface.items_tree:
                ng.interface.new_socket("Image", in_out="INPUT",
                                        socket_type="NodeSocketColor")
                ng.interface.new_socket("Image", in_out="OUTPUT",
                                        socket_type="NodeSocketColor")
            glare = nodes.new("CompositorNodeGlare")
            _set_glare(glare)
            links.new(grp_in.outputs[0], glare.inputs[0])
            links.new(glare.outputs[0], grp_out.inputs[0])
        except Exception as e:
            print("glare(5.x) skipped:", e)
        return

    # --- Blender 4.x: scene.node_tree ---
    try:
        nt = scene.node_tree
        nodes, links = nt.nodes, nt.links
        rl = next((n for n in nodes if n.type == "R_LAYERS"), None)
        comp = next((n for n in nodes if n.type == "COMPOSITE"), None)
        if not rl or not comp:
            return
        glare = nodes.new("CompositorNodeGlare")
        _set_glare(glare)
        links.new(rl.outputs["Image"], glare.inputs[0])
        links.new(glare.outputs[0], comp.inputs[0])
    except Exception as e:
        print("glare(4.x) skipped:", e)


def _set_glare(glare):
    for attr, val in (("glare_type", "FOG_GLOW"), ("quality", "HIGH"),
                      ("threshold", 1.0)):
        try:
            setattr(glare, attr, val)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
def main():
    clear_scene()
    mats = build_materials()
    setup_world()

    env = new_collection("Environment")
    people = new_collection("People")
    props = new_collection("Props")

    build_room(env, mats)
    build_pendant_lamps(env, mats)
    build_booth(env, mats, y_center=-0.75, name="Booth_Front")
    build_booth(env, mats, y_center=0.75, name="Booth_Back")
    build_table(env, mats)

    # テーブルの上の食器・パフェ
    build_parfait(props, mats, (-0.12, -0.05, 0.75), cream_color=(1.0, 0.92, 0.95))
    build_parfait(props, mats, (0.10, 0.05, 0.75), cream_color=(0.98, 0.95, 0.85))
    build_coffee(props, mats, (0.30, 0.18, 0.75))
    build_plate_cake(props, mats, (0.0, 0.22, 0.75))

    # 男性（手前・奥を向く: +Y）右腕は可動アームにするので省く
    male = build_person("Male", location=(0, -0.95, 0.62), facing=+1,
                        mat_body=mats["skin"], mat_top=mats["male_jacket"],
                        mat_hair=mats["hair"], female=False,
                        with_right_arm=False)
    # 白T（ジャケットの内側にのぞく）
    add_mesh_primitive("uv_sphere", "Male_Shirt",
                       location=(0, -0.93, 0.94),
                       scale=(0.10, 0.10, 0.16), material=mats["male_shirt"])

    # 男性の可動右腕（食べる動作）
    elbow = build_animated_arm("MaleArm",
                               shoulder_world=(0.18, -0.78, 1.05), mats=mats)
    animate_eating(elbow)

    # 女性（奥・手前を向く: -Y）両腕テーブルへ
    female = build_person("Female", location=(0, 0.95, 0.62), facing=-1,
                          mat_body=mats["skin"], mat_top=mats["female_knit"],
                          mat_hair=mats["hair"], female=True,
                          with_right_arm=True)
    # 相づちの揺れ
    animate_idle_sway(female["body"], amp_deg=2.0)
    animate_idle_sway(male["body"], amp_deg=1.0)

    setup_camera()
    setup_render()

    bpy.context.scene.frame_set(FRAME_START)
    print("=== Famires scene built. frames %d-%d @ %dfps ==="
          % (FRAME_START, FRAME_END, FPS))


if __name__ == "__main__":
    main()
