"""
render_viewport.py
create_scene.py でシーンを構築したあと、MP4としてレンダリングするスクリプト。

使い方（単独実行）:
  blender --background --python render_viewport.py

run_blender_render.bat から自動呼び出しされる想定。
"""

import bpy
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def load_scene():
    """create_scene.py を exec で取り込んでシーンを構築する"""
    scene_script = SCRIPT_DIR / "create_scene.py"
    if not scene_script.exists():
        print(f"[ERROR] create_scene.py が見つかりません: {scene_script}")
        sys.exit(1)

    # パスをsys.pathに追加して import できるようにする
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))

    with open(scene_script, "r", encoding="utf-8") as f:
        source = f.read()

    namespace = {"__name__": "__render__", "__file__": str(scene_script)}
    exec(compile(source, str(scene_script), "exec"), namespace)

    # main() を呼ぶ
    if "main" in namespace:
        namespace["main"]()
    else:
        print("[ERROR] create_scene.py に main() 関数が見つかりません")
        sys.exit(1)


def configure_output():
    """レンダー出力設定を確定する"""
    scene = bpy.context.scene

    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = str(output_dir / "flower_scene_reference")
    scene.render.filepath = output_path

    # FFMPEG対応確認（Blender 5.xでは利用不可の場合あり）
    available_formats = scene.render.image_settings.bl_rna.properties["file_format"].enum_items.keys()
    if "FFMPEG" in available_formats:
        scene.render.image_settings.file_format  = "FFMPEG"
        scene.render.ffmpeg.format               = "MPEG4"
        scene.render.ffmpeg.codec                = "H264"
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scene.render.ffmpeg.ffmpeg_preset        = "GOOD"
        try:
            scene.render.ffmpeg.audio_codec = "AAC"
        except Exception:
            pass
        print("[Render] Output format: MP4 (H.264)")
    else:
        frames_dir = output_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(frames_dir / "frame_")
        print("[Render] FFMPEG not available - rendering PNG sequence")
        print(f"[Render] Frames output: {frames_dir}")

    # 解像度・fps
    scene.render.resolution_x           = 1920
    scene.render.resolution_y           = 1080
    scene.render.resolution_percentage  = 100
    scene.render.fps                    = 24

    # フレーム範囲
    scene.frame_start = 1
    scene.frame_end   = 360

    print(f"[Render] 出力先: {output_path}.mp4")
    print(f"[Render] 解像度: {scene.render.resolution_x}x{scene.render.resolution_y}")
    print(f"[Render] フレーム: {scene.frame_start} - {scene.frame_end}  ({scene.render.fps}fps)")


def render_animation():
    """アニメーションレンダリングを実行する"""
    print("\n[Render] レンダリング開始...")
    bpy.ops.render.render(animation=True)
    print("[Render] レンダリング完了！")

    output_file = SCRIPT_DIR / "output" / "flower_scene_reference.mp4"
    if output_file.exists():
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"[Render] 出力ファイル: {output_file}  ({size_mb:.1f} MB)")
    else:
        print("[Render] WARNING: 出力ファイルが見つかりません。FFmpegがBlenderに組み込まれているか確認してください。")


def main():
    print("\n" + "=" * 60)
    print("FF7風シーン レンダリング開始")
    print("=" * 60)

    load_scene()
    configure_output()
    render_animation()

    print("=" * 60)
    print("完了: output/flower_scene_reference.mp4")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
