# -*- coding: utf-8 -*-
"""
build_dragon.py — 剣士が洞窟を進んでドラゴンを倒すシーンを Mixamo モーションから構築する

使い方:
    blender -b -P build_dragon.py -- --anims ./anims_dragon --out ./out_dragon --render --engine workbench

anims_dragon/ に入れる Mixamo クリップの例(番号順に再生。詳しくは anims_dragon/README.md):
    01_walk.fbx      … Sword And Shield Walk(With Skin)
    02_run.fbx       … Sword And Shield Run
    03_dodge.fbx     … Sword And Shield Roll / Dodge
    04_slash.fbx     … Sword And Shield Slash(戦闘開始 → この位置にドラゴンが立つ)
    05_slash2.fbx    … Sword And Shield Attack など
    06_victory.fbx   … 勝利ポーズ(このクリップが始まるとドラゴンが倒れる)

仕組みは build_parkour.py と同じ(ルートモーション連結・尺の自動調整・追従カメラ)。
このスクリプトが追加するのは:
  - 洞窟のブロックアウト: 進路に沿った岩壁・鍾乳石・たいまつ
  - ドラゴンのブロックアウト: 最初の攻撃クリップの位置の先に配置。
    首と翼がゆっくり動き、victory クリップ(無ければ最後の攻撃クリップの終わり)で倒れる
出来上がった動画を Seedance 2.0 の video_reference に渡し、
プロンプトで「鎧の剣士」「洞窟」「ドラゴン」の見た目を与える。
"""

import importlib.util
import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector

_here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("build_parkour", os.path.join(_here, "build_parkour.py"))
bp = importlib.util.module_from_spec(spec)
sys.modules["build_parkour"] = bp
spec.loader.exec_module(bp)

D = math.radians

# 攻撃系のクリップ名 → その場所にドラゴンを置く。victory → ドラゴンが倒れる合図
bp.OBSTACLE_KEYWORDS = {
    "slash": "dragon", "attack": "dragon", "combo": "dragon", "fight": "dragon",
    "victory": "kill",
}
bp.CAMERA_OFFSET = Vector((-1.1, -2.3, 1.55))  # 洞窟の通路の内側に収まる寄りのカメラ


# ------------------------------------------------------------------ 洞窟 --

def cave_environment(scene, arm):
    """NLA 構築後の腰の軌跡に沿って、岩壁・鍾乳石・たいまつを並べる"""
    ground = bp.make_material("cave_floor", (0.24, 0.21, 0.19))
    rock = bp.make_material("cave_rock", (0.36, 0.32, 0.28))
    torch = bp.make_material("cave_torch", (1.0, 0.45, 0.05))

    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "CaveFloor"
    floor.data.materials.append(ground)
    floor.color = (0.24, 0.21, 0.19, 1.0)

    hips = bp.find_hips(arm)
    rng = random.Random(11)
    path = []
    for f in range(scene.frame_start, scene.frame_end + 1, 10):
        scene.frame_set(f)
        p = (arm.matrix_world @ hips.head).copy()
        path.append(Vector((p.x, p.y, 0)))

    def add_rock(pos, sx, sy, sz, mat, color):
        bpy.ops.mesh.primitive_cube_add(location=(pos.x, pos.y, pos.z))
        c = bpy.context.object
        c.scale = (sx, sy, sz)
        c.rotation_euler = (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15),
                            rng.uniform(0, math.pi))
        c.data.materials.append(mat)
        c.color = color
        return c

    placed = 0.0
    for i in range(1, len(path)):
        seg = path[i] - path[i - 1]
        placed += seg.length
        if placed < 2.0:
            continue
        placed = 0.0
        d = seg.normalized() if seg.length > 1e-4 else Vector((0, 1, 0))
        side = Vector((-d.y, d.x, 0))
        for s in (-1, 1):
            off = rng.uniform(3.2, 4.4)  # カメラより外側に
            h = rng.uniform(1.2, 3.2)
            add_rock(path[i] + side * (s * off) + Vector((0, 0, h / 2)),
                     rng.uniform(0.5, 1.3), rng.uniform(0.5, 1.3), h / 2,
                     rock, (0.36, 0.32, 0.28, 1.0))
        if rng.random() < 0.5:  # 鍾乳石(上から吊る)
            add_rock(path[i] + side * rng.uniform(-1.5, 1.5) + Vector((0, 0, rng.uniform(3.2, 4.0))),
                     0.18, 0.18, rng.uniform(0.5, 1.1), rock, (0.32, 0.28, 0.25, 1.0))
        if rng.random() < 0.35:  # たいまつ(小さなオレンジのブロック)
            t = add_rock(path[i] + side * (rng.choice((-1, 1)) * 2.9) + Vector((0, 0, 1.6)),
                         0.09, 0.09, 0.18, torch, (1.0, 0.45, 0.05, 1.0))
            lamp = bpy.data.lights.new("TorchLight", type="POINT")
            lamp.energy = 120
            lamp.color = (1.0, 0.55, 0.25)
            lo = bpy.data.objects.new("TorchLight", lamp)
            lo.location = t.location + Vector((0, 0, 0.3))
            scene.collection.objects.link(lo)

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.13, 0.14, 0.18, 1.0)  # 洞窟の薄暗さ
        bg.inputs[1].default_value = 0.6


# ---------------------------------------------------------------- ドラゴン --

def build_dragon(scene, pos, yaw, kill_frame):
    """ブロックアウトのドラゴンを配置する。kill_frame で倒れる"""
    mat = bp.make_material("dragon_body", (0.45, 0.10, 0.08))
    wing_mat = bp.make_material("dragon_wing", (0.35, 0.08, 0.10))

    root = bpy.data.objects.new("DragonRoot", None)
    root.location = (pos.x, pos.y, 0)
    root.rotation_euler = (0, 0, yaw)  # 首(-Y 側)が剣士の方を向く
    root.scale = (1.2, 1.2, 1.2)
    scene.collection.objects.link(root)

    def box(name, loc, scale, m, color, parent=root):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        o = bpy.context.object
        o.name = name
        o.parent = parent
        o.location = loc
        o.scale = scale
        o.data.materials.append(m)
        o.color = color
        return o

    col = (0.45, 0.10, 0.08, 1.0)
    wcol = (0.35, 0.08, 0.10, 1.0)
    box("d_body", (0, 0.3, 1.15), (1.0, 1.5, 0.75), mat, col)
    box("d_hips", (0, 1.7, 1.0), (0.8, 0.7, 0.6), mat, col)
    # 尻尾
    box("d_tail1", (0, 2.8, 0.85), (0.4, 0.6, 0.35), mat, col)
    box("d_tail2", (0, 3.8, 0.7), (0.25, 0.55, 0.22), mat, col)
    # 脚
    for sx in (-1, 1):
        box("d_leg", (0.75 * sx, 0.1, 0.45), (0.28, 0.4, 0.45), mat, col)
        box("d_leg2", (0.6 * sx, 1.7, 0.4), (0.24, 0.35, 0.4), mat, col)
    # 首(前方 = -Y に伸びる)+ 頭
    neck = bpy.data.objects.new("DragonNeck", None)
    neck.parent = root
    neck.location = (0, -0.9, 1.6)
    scene.collection.objects.link(neck)
    box("d_neck1", (0, -0.25, 0.3), (0.35, 0.45, 0.4), mat, col, parent=neck)
    box("d_neck2", (0, -0.6, 0.85), (0.3, 0.35, 0.35), mat, col, parent=neck)
    box("d_head", (0, -1.05, 1.25), (0.42, 0.6, 0.3), mat, col, parent=neck)
    box("d_jaw", (0, -1.5, 1.1), (0.3, 0.45, 0.12), mat, col, parent=neck)
    # 翼
    wings = []
    for sx in (-1, 1):
        w = bpy.data.objects.new("DragonWingRoot", None)
        w.parent = root
        w.location = (0.55 * sx, 0.3, 1.8)
        scene.collection.objects.link(w)
        box("d_wing", (1.5 * sx, 0, 0.45), (1.6, 0.9, 0.06), wing_mat, wcol, parent=w)
        wings.append((w, sx))

    fps = scene.render.fps
    end = scene.frame_end

    # 生きている間: 首がゆっくり揺れ、翼がはためく
    for f in range(1, min(kill_frame, end) + 1, 12):
        t = f / fps
        neck.rotation_euler = (D(6) * math.sin(t * 1.7), 0, D(10) * math.sin(t * 0.9))
        neck.keyframe_insert("rotation_euler", frame=f)
        for w, sx in wings:
            w.rotation_euler = (0, sx * (D(18) + D(16) * math.sin(t * 3.0)), 0)
            w.keyframe_insert("rotation_euler", frame=f)
        root.location.z = 0.05 * math.sin(t * 2.2)
        root.keyframe_insert("location", frame=f)

    # 倒れる(kill_frame から 25 フレームかけて崩れ落ちる)
    if kill_frame < end:
        f0, f1 = kill_frame, min(kill_frame + 25, end)
        root.keyframe_insert("location", frame=f0)
        root.rotation_euler = (0, 0, yaw)
        root.keyframe_insert("rotation_euler", frame=f0)
        root.location.z = -0.5
        # 剣士側ではなく横向きに崩れ落ちる(倒れてもカメラを塞がない)
        root.rotation_euler = (D(8), D(50), yaw + D(25))
        root.keyframe_insert("location", frame=f1)
        root.keyframe_insert("rotation_euler", frame=f1)
        neck.rotation_euler = (D(-35), 0, D(20))
        neck.keyframe_insert("rotation_euler", frame=f1)
        for w, sx in wings:
            w.rotation_euler = (0, sx * D(55), 0)
            w.keyframe_insert("rotation_euler", frame=f1)


# -------------------------------------------------------------------- main --

def main():
    args = bp.parse_args()
    bp.TARGET_SECONDS = args.seconds
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = args.fps

    arm, clips = bp.import_clips(os.path.abspath(args.anims))
    markers = bp.build_nla(scene, arm, clips, args.fps)

    # ドラゴンの位置 = 戦闘が終わった時点の剣士の位置からさらに前方。
    # 攻撃クリップ中も剣士は少しずつ前進するので、最終立ち位置を基準にすれば
    # 剣士がドラゴンの中に歩き込むことがない
    dragons = [m for m in markers if m[0] == "dragon"]
    kills = [m for m in markers if m[0] == "kill"]
    if dragons:
        yaw = dragons[-1][2]
        kill_frame = kills[0][3] if kills else dragons[-1][4]
        hips = bp.find_hips(arm)
        scene.frame_set(int(kill_frame))
        stand = arm.matrix_world @ hips.head
        fwd = (Matrix.Rotation(yaw, 3, "Z") @ Vector((0, 1, 0))).normalized()
        dpos = Vector((stand.x, stand.y, 0)) + fwd * 4.0
        build_dragon(scene, dpos, yaw, int(kill_frame))
        print(f"ドラゴンを配置: ({dpos.x:.1f}, {dpos.y:.1f})  倒れるフレーム: {int(kill_frame)}")
    else:
        print("注意: 攻撃クリップ(slash/attack など)が無いためドラゴンを置けませんでした")

    cave_environment(scene, arm)
    bp.build_camera(scene, arm, args.fps)

    # 戦闘が始まったら、カメラは剣士とドラゴンの中間を注視しつつ少し引く
    if dragons:
        target = bpy.data.objects["CamTarget"]
        dolly = bpy.data.objects["CamDolly"]
        hips = bp.find_hips(arm)
        fight_start = int(dragons[0][3])
        focus_d = dpos + Vector((0, 0, 1.7))
        for f in range(fight_start, scene.frame_end + 1, bp.CAMERA_BAKE_STEP):
            scene.frame_set(f)
            hp = arm.matrix_world @ hips.head
            w = min(1.0, (f - fight_start) / 25.0)  # 25 フレームかけて切り替え
            focus = hp.lerp(focus_d, 0.45 * w)
            target.location = focus + Vector((0, 0, 0.2 * (1 - w)))
            target.keyframe_insert("location", frame=f)
            dolly.location = hp + bp.CAMERA_OFFSET * (1.0 + 0.8 * w)
            dolly.keyframe_insert("location", frame=f)

    bp.setup_render(scene, out_dir, args.fps, args.engine)
    scene.render.filepath = os.path.join(out_dir, "dragon_reference.mp4")

    blend = os.path.join(out_dir, "dragon.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("保存しました:", blend)

    if args.render:
        bpy.ops.render.render(animation=True)
        print("完了:", scene.render.filepath)


if __name__ == "__main__":
    main()
