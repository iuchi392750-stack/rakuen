# -*- coding: utf-8 -*-
"""
make_test_anims.py — build_parkour.py の動作確認用に、Mixamo 風のダミー FBX クリップを生成する

使い方:
    blender -b -P make_test_anims.py -- --out ./anims

生成物(簡易スティックフィギュア + 前進モーション):
    01_running.fbx  … 前方へ走る(2 秒)
    02_vault.fbx    … 山なりに跳び越える(1.5 秒)
    03_running.fbx  … さらに走る(2 秒)
    04_roll.fbx     … 低い姿勢で前転(1.3 秒)

Mixamo の本物の FBX が用意できたら、このダミーと差し替えるだけで同じ手順が使えます。
"""

import bpy
import math
import os
import sys
from mathutils import Vector


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="./anims")
    return p.parse_args(argv)


BONES = {
    # name: (head, tail, parent)
    "mixamorig:Hips":  ((0, 0, 1.0), (0, 0, 1.3), None),
    "mixamorig:Spine": ((0, 0, 1.3), (0, 0, 1.7), "mixamorig:Hips"),
    "mixamorig:LegL":  ((0.15, 0, 1.0), (0.15, 0, 0.05), "mixamorig:Hips"),
    "mixamorig:LegR":  ((-0.15, 0, 1.0), (-0.15, 0, 0.05), "mixamorig:Hips"),
}


def build_rig():
    arm_data = bpy.data.armatures.new("TestRig")
    arm = bpy.data.objects.new("TestRig", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    ebones = {}
    for name, (head, tail, parent) in BONES.items():
        eb = arm_data.edit_bones.new(name)
        eb.head, eb.tail = Vector(head), Vector(tail)
        if parent:
            eb.parent = ebones[parent]
        ebones[name] = eb
    bpy.ops.object.mode_set(mode="OBJECT")

    # ボーンごとに直方体を作り、その骨に 100% ウェイトで割り当てた 1 枚メッシュを作る
    verts, faces, groups = [], [], {}
    for name, (head, tail, _) in BONES.items():
        h, t = Vector(head), Vector(tail)
        c = (h + t) / 2
        half = Vector((0.08, 0.08, (t - h).length / 2))
        base = len(verts)
        for dx in (-1, 1):
            for dy in (-1, 1):
                for dz in (-1, 1):
                    verts.append(c + Vector((dx * half.x, dy * half.y, dz * half.z)))
        cube_faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                      (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        faces += [tuple(base + i for i in f) for f in cube_faces]
        groups[name] = list(range(base, base + 8))

    mesh = bpy.data.meshes.new("TestBody")
    mesh.from_pydata(verts, [], faces)
    body = bpy.data.objects.new("TestBody", mesh)
    bpy.context.scene.collection.objects.link(body)
    for name, idxs in groups.items():
        vg = body.vertex_groups.new(name=name)
        vg.add(idxs, 1.0, "REPLACE")
    body.parent = arm
    mod = body.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    return arm


def key_hips_world(arm, frame, world_offset):
    """Hips ポーズボーンに『ワールドでこれだけ動いた』位置をキーフレームする"""
    pb = arm.pose.bones["mixamorig:Hips"]
    pb.location = pb.bone.matrix_local.to_3x3().inverted() @ Vector(world_offset)
    pb.keyframe_insert("location", frame=frame)


def make_clip(name, frames, path_fn, out_dir):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = 30
    arm = build_rig()
    arm.animation_data_create()

    for f in range(1, frames + 1):
        t = (f - 1) / (frames - 1)
        key_hips_world(arm, f, path_fn(t))
        # 脚を交互に振って走りらしく見せる
        swing = math.sin(t * frames / 30.0 * 2 * math.pi * 2.5) * 0.5
        for leg, sign in (("mixamorig:LegL", 1), ("mixamorig:LegR", -1)):
            pb = arm.pose.bones[leg]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = (swing * sign, 0, 0)
            pb.keyframe_insert("rotation_euler", frame=f)

    arm.animation_data.action.name = name
    fpath = os.path.join(out_dir, name + ".fbx")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.fbx(filepath=fpath, add_leaf_bones=False, bake_anim=True)
    print("生成:", fpath)


def main():
    args = parse_args()
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    speed = 3.0  # m/s
    make_clip("01_running", 60,
              lambda t: (0, t * 2 * speed, 0), out_dir)
    make_clip("02_vault", 45,
              lambda t: (0, t * 1.5 * speed * 0.8,
                         math.sin(t * math.pi) * 0.5), out_dir)
    make_clip("03_running", 60,
              lambda t: (0, t * 2 * speed, 0), out_dir)
    make_clip("04_roll", 40,
              lambda t: (0, t * 1.3 * speed * 0.6,
                         -0.4 * math.sin(t * math.pi)), out_dir)


if __name__ == "__main__":
    main()
