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

# --- 格闘ゲーム用の派手なポーズ ---
UPPERCUT_R = pose(GUARD, **{"upperarm.R": (-0.10, 0.40, 0.91), "forearm.R": (-0.05, 0.30, 0.95),
                            "torso": (0, -0.10, 0.99), "head": (0, -0.05, 1.0)})
SPIN_KICK_R = pose(GUARD, **{"thigh.R": (-0.15, 0.75, 0.64), "shin.R": (-0.10, 0.99, 0.05),
                             "torso": (0.15, -0.30, 0.94), "upperarm.L": (0.80, 0.20, -0.10),
                             "upperarm.R": (-0.85, -0.20, 0.15)})
SWEEP_L = pose(GUARD, **{"thigh.L": (0.15, 0.92, -0.35), "shin.L": (0.05, 0.99, -0.05),
                         "thigh.R": (-0.10, 0.20, -0.97), "shin.R": (0.0, -0.65, -0.75),
                         "torso": (0, 0.60, 0.80), "head": (0, 0.55, 0.83),
                         "upperarm.L": (0.70, 0.40, -0.50), "upperarm.R": (-0.70, 0.20, -0.60)})
JUMP_TUCK = pose(GUARD, **{"thigh.L": (0.10, 0.80, -0.58), "shin.L": (0.05, -0.75, -0.65),
                           "thigh.R": (-0.10, 0.80, -0.58), "shin.R": (-0.05, -0.75, -0.65),
                           "torso": (0, 0.30, 0.95)})
LAUNCHED = pose(GUARD, **{"torso": (0, -0.60, 0.80), "head": (0, -0.70, 0.70),
                          "upperarm.L": (0.85, -0.30, 0.40), "forearm.L": (0.60, -0.40, 0.60),
                          "upperarm.R": (-0.85, -0.30, 0.40), "forearm.R": (-0.60, -0.40, 0.60),
                          "thigh.L": (0.10, 0.70, -0.70), "shin.L": (0.05, -0.30, -0.95),
                          "thigh.R": (-0.10, 0.55, -0.83), "shin.R": (-0.05, -0.40, -0.91)})
STAGGER = pose(GUARD, **{"torso": (0, -0.50, 0.86), "head": (0, -0.45, 0.89),
                         "upperarm.L": (0.90, 0.10, 0.20), "upperarm.R": (-0.90, 0.10, 0.20),
                         "thigh.L": (0.10, 0.50, -0.86)})
BACKFIST_R = pose(GUARD, **{"upperarm.R": (-0.70, 0.70, 0.10), "forearm.R": (-0.60, 0.79, 0.05),
                            "torso": (0.20, 0.15, 0.97),
                            "upperarm.L": (0.60, -0.40, -0.60)})
KNOCKED_DOWN = {
    "torso": (0, -0.98, 0.15), "head": (0, -1.0, 0.08),
    "upperarm.L": (0.85, -0.35, 0.10), "forearm.L": (0.70, -0.55, 0.15),
    "upperarm.R": (-0.85, -0.35, 0.10), "forearm.R": (-0.70, -0.55, 0.15),
    "thigh.L": (0.12, 0.92, -0.30), "shin.L": (0.05, 0.98, -0.10),
    "thigh.R": (-0.12, 0.85, -0.45), "shin.R": (-0.05, 0.95, -0.20),
}
VICTORY = {
    "torso": (0, 0.02, 1.0), "head": (0, 0.05, 1.0),
    "upperarm.L": (0.30, 0.05, -0.95), "forearm.L": (0.20, 0.10, -0.97),
    "upperarm.R": (-0.30, 0.05, -0.95), "forearm.R": (-0.20, 0.10, -0.97),
    "thigh.L": (0.10, 0.05, -0.99), "shin.L": (0.05, -0.02, -1.0),
    "thigh.R": (-0.10, 0.05, -0.99), "shin.R": (-0.05, -0.02, -1.0),
}

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


def key_pose(arm, frame, p, loc=None, yaw=None, crouch=0.0, z=0.0):
    """1 フレームにポーズ・立ち位置・向き・沈み込み・ジャンプ高さをまとめてキーフレーム"""
    hips = arm.pose.bones["hips"]
    hips.location = (0, 0, -crouch)
    hips.keyframe_insert("location", frame=frame)
    for bname in BONE_ORDER:
        if bname in p:
            aim_bone(arm, arm.pose.bones[bname], p[bname], frame)
    if loc is not None:
        arm.location = (loc[0], loc[1], z)
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
    """15 秒の格闘ゲーム風バトル。R=赤 B=青。
    ダッシュ・スピンキック・アッパーで打ち上げ・ジャンプ回避・
    スピニングバックフィストでノックダウンして決着、という流れ。"""
    spin = {"r": 0.0, "b": 0.0}

    def place(t, ang_deg, dist=1.9, crouch_r=0.05, crouch_b=0.05,
              pr=GUARD, pb=GUARD, dr=0.0, db=0.0, zr=0.0, zb=0.0,
              spin_r=0.0, spin_b=0.0):
        """ang_deg: 対峙軸の回転。dr/db: 前後ステップ(+で相手へ)。
        zr/zb: ジャンプ高さ。spin_r/spin_b: このキーまでに回る追加回転(度)"""
        spin["r"] += spin_r
        spin["b"] += spin_b
        a = D(ang_deg)
        axis = Vector((math.sin(a), math.cos(a), 0))
        c = Vector((0, 0, 0))
        r_pos = c - axis * (dist / 2 - dr)
        b_pos = c + axis * (dist / 2 - db)
        key_pose(red, sec(t), pr, loc=(r_pos.x, r_pos.y),
                 yaw=-ang_deg + spin["r"], crouch=crouch_r, z=zr)
        key_pose(blue, sec(t), pb, loc=(b_pos.x, b_pos.y),
                 yaw=180 - ang_deg + spin["b"], crouch=crouch_b, z=zb)

    # --- タイムライン ---
    # 0-1.5s: 対峙、じりじり回る
    place(0.0, 0, dist=2.6)
    place(1.4, 10, dist=2.4)
    # 1.5-2.6s: 赤がダッシュしてワンツー、青は2回ブロック
    place(1.8, 12, dist=1.8, dr=0.2, pr=JAB_L, pb=BLOCK)
    place(2.1, 12, dist=1.8, dr=0.3, pr=JAB_R, pb=BLOCK, crouch_b=0.12)
    place(2.6, 14, dist=1.9, pr=GUARD, pb=GUARD)
    # 2.6-3.6s: 青のスピンキック → 赤が仰け反って吹き飛ぶ
    place(3.0, 14, dist=1.7, pb=SPIN_KICK_R, db=0.35, spin_b=-360, crouch_b=0.10)
    place(3.3, 14, dist=1.7, pb=SPIN_KICK_R, db=0.3, pr=STAGGER, dr=-0.55, crouch_r=0.15)
    place(3.9, 12, dist=2.6, pr=pose(GUARD, torso=(0, -0.20, 0.98)), pb=GUARD)
    # 3.9-5.2s: 仕切り直しの回り込み
    place(5.0, -4, dist=2.4)
    # 5.2-6.6s: 赤の足払い → 青がジャンプでかわす
    place(5.6, -8, dist=1.7, dr=0.3, pr=SWEEP_L, crouch_r=0.42, spin_r=360)
    place(5.95, -8, dist=1.7, dr=0.3, pr=SWEEP_L, crouch_r=0.45, pb=JUMP_TUCK, zb=0.75, crouch_b=0.1)
    place(6.3, -8, dist=1.8, pr=pose(GUARD, torso=(0, 0.4, 0.92)), crouch_r=0.25, pb=GUARD, zb=0.0)
    # 6.6-8.2s: 赤のアッパーカットで青が打ち上がる → 崩れて着地
    place(6.9, -10, dist=1.5, dr=0.35, pr=pose(GUARD, torso=(0, 0.5, 0.87)), crouch_r=0.3)
    place(7.15, -10, dist=1.5, dr=0.4, pr=UPPERCUT_R, crouch_r=0.0)
    place(7.45, -10, dist=1.6, pr=UPPERCUT_R, pb=LAUNCHED, db=-0.45, zb=0.9, crouch_b=0.1)
    place(7.9, -10, dist=2.2, pr=GUARD, pb=pose(DUCK, torso=(0, 0.65, 0.76)), db=-0.5, zb=0.0, crouch_b=0.4)
    # 8.2-9.6s: 青がゆっくり立ち上がって構え直す
    place(9.0, -12, dist=2.5, pb=pose(GUARD, torso=(0, 0.3, 0.95)), crouch_b=0.2)
    place(9.6, -14, dist=2.4)
    # 9.6-11.2s: 青のジャンプスピンキック → 赤は重いブロックでスライド後退
    place(10.2, -16, dist=1.9, db=0.3, pb=JUMP_TUCK, zb=0.5, spin_b=360, crouch_b=0.05)
    place(10.5, -16, dist=1.7, db=0.4, pb=SPIN_KICK_R, zb=0.35, pr=BLOCK)
    place(10.9, -16, dist=2.0, pb=GUARD, zb=0.0, pr=BLOCK, dr=-0.5, crouch_r=0.18)
    place(11.4, -18, dist=2.2, pr=GUARD)
    # 11.4-12.6s: 赤ジャブ → 青ダック → 青ボディ → 赤よろける
    place(11.8, -20, dist=1.6, dr=0.3, pr=JAB_L)
    place(12.05, -20, dist=1.6, dr=0.3, pb=DUCK, crouch_b=0.3)
    place(12.3, -20, dist=1.5, pb=BODY_HIT, db=0.35, crouch_b=0.15, pr=STAGGER, dr=-0.2)
    # 12.6-14.0s: 赤のスピニングバックフィストが直撃 → 青ノックダウン
    place(13.0, -22, dist=1.6, dr=0.35, pr=BACKFIST_R, spin_r=360, pb=pose(GUARD, torso=(0, -0.15, 0.99)))
    place(13.35, -22, dist=1.9, pr=BACKFIST_R, pb=LAUNCHED, db=-0.8, zb=0.55)
    place(13.9, -22, dist=2.8, pr=pose(GUARD, torso=(0, 0.2, 0.98)), pb=KNOCKED_DOWN, db=-1.0, zb=0.0, crouch_b=0.82)
    # 14.0-15s: 赤の勝利ポーズ、青はダウンしたまま
    place(14.6, -22, dist=2.8, pr=VICTORY, pb=KNOCKED_DOWN, db=-1.0, crouch_b=0.84)

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


# 格闘ゲーム風のカット割り: (開始秒, 終了秒, カメラ始点, カメラ終点, 注視点始, 注視点終)
# 各ショット内はゆっくり押し込み(ドリーイン)、ショット間はハードカット
CAMERA_SHOTS = [
    (0.0, 2.6, (5.6, 0.8, 1.60), (5.0, 0.6, 1.55), (0, 0, 1.15), (0, 0, 1.20)),      # ワイド
    (2.6, 5.2, (-4.8, 1.6, 1.30), (-4.2, 1.2, 1.35), (0, 0.2, 1.20), (0, 0, 1.15)),  # 逆サイド
    (5.2, 8.2, (3.9, -2.0, 0.72), (3.3, -1.3, 0.85), (0, 0, 1.25), (0, 0.2, 1.35)),  # ローアングル
    (8.2, 11.4, (3.0, 2.8, 1.55), (3.4, 2.1, 1.45), (0, 0.9, 1.30), (0, 0.3, 1.25)), # 青サイド寄り
    (11.4, 13.6, (-5.2, -1.2, 1.95), (-4.4, -0.7, 1.70), (0, 0, 1.10), (0, 0, 1.15)),# 俯瞰ぎみワイド
    (13.6, 15.1, (4.4, -2.6, 0.68), (3.6, -2.1, 0.80), (0, -0.5, 1.20), (0, -0.6, 1.25)),  # 勝者の見得
]


def build_camera(scene):
    target = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(target)

    cam_data = bpy.data.cameras.new("FightCam")
    cam_data.lens = 45
    cam = bpy.data.objects.new("FightCam", cam_data)
    scene.collection.objects.link(cam)
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    scene.camera = cam

    for t0, t1, p0, p1, l0, l1 in CAMERA_SHOTS:
        f0, f1 = sec(t0), sec(t1) - 1
        cam.location = p0
        cam.keyframe_insert("location", frame=f0)
        target.location = l0
        target.keyframe_insert("location", frame=f0)
        cam.location = p1
        cam.keyframe_insert("location", frame=f1)
        target.location = l1
        target.keyframe_insert("location", frame=f1)

    # ショット内は LINEAR のドリーイン、ショット末尾は CONSTANT にして
    # 次のショットへハードカットさせる
    cut_frames = {sec(t1) - 1 for _, t1, *_ in CAMERA_SHOTS}
    for obj in (cam, target):
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = ("CONSTANT" if round(kp.co.x) in cut_frames
                                    else "LINEAR")
            # 手持ちの微揺れ
            mod = fc.modifiers.new("NOISE")
            mod.scale = 35.0
            mod.strength = 0.035 if obj is cam else 0.015
            mod.phase = fc.array_index * 23.0 + (100 if obj is target else 0)


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
