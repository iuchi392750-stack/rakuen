# パルクール映像パイプライン(Mixamo → Blender → Seedance 2.0)

Mixamo のパルクール系モーションを Blender で 30 秒に繋ぎ、そのプレビュー動画を
Seedance 2.0 の **video_reference**(動きのお手本)として渡して最終映像を生成するためのツール一式です。

Blender のシーン構築(モーションの連結・障害物配置・カメラ・レンダリング設定)は
`build_parkour.py` がすべて自動でやります。手作業は「Mixamo からのダウンロード」だけです。

## 必要なもの

- Blender 4.0 以降(<https://www.blender.org/download/>)
- Adobe アカウント(Mixamo のダウンロードに必要・無料)

## 手順

### 1. Mixamo からモーションをダウンロード

<https://www.mixamo.com/> にログインし、キャラクターを 1 体選んでから
以下のようなモーションを検索してダウンロードします(検索キーワード例):

| 順番 | 検索キーワード | 役割 |
|---|---|---|
| 1 | Running | 助走 |
| 2 | Vault / Jump Over | 障害物の跳び越え |
| 3 | Running | 繋ぎの走り |
| 4 | Running Jump | ギャップジャンプ |
| 5 | Falling To Roll | 着地ロール |
| 6 | Running Slide | スライディング |
| 7 | Freehang Climb | 壁登り |
| 8 | Front Flip | フィニッシュの宙返り |

**ダウンロード設定:**

- Format: **FBX Binary (.fbx)**、30 Frames per Second
- **最初の 1 本だけ Skin: With Skin**、2 本目以降は **Without Skin**(同じキャラなので体は 1 回で十分)
- 「In Place」のチェックは **外す**(移動込みのモーションを使います。連結は script が自動処理)

### 2. ファイルを再生順に命名して `anims/` に置く

```
parkour/anims/
  01_running.fbx      ← With Skin(この 1 本だけ体つき)
  02_vault.fbx
  03_running.fbx
  04_running_jump.fbx
  05_roll.fbx
  06_running.fbx
  07_slide.fbx
  08_climb.fbx
  09_frontflip.fbx
```

- 数字の順に再生されます
- 同じモーションを繰り返したいときはファイルをコピーして `06_running.fbx` のように別番号を付けるだけ
- ファイル名に `vault` / `slide` / `climb` が含まれると、その場所に対応する障害物ブロックを自動配置します
- 30 秒(900 フレーム @30fps)に届くまでクリップを足してください。実行時に合計秒数が表示されます

### 3. シーンを構築してレンダリング

```bash
cd parkour
blender -b -P build_parkour.py -- --anims ./anims --out ./out --render
```

- `out/parkour.blend` … 構築済みシーン(Blender で開いて微調整できます)
- `out/parkour_preview.mp4` … 1280x720 / 30fps のプレビュー動画

`--render` を外せばシーン構築だけ行うので、Blender で開いて
カメラ位置や障害物を調整してから **Ctrl+F12** でレンダリングしても OK です。

GPU の無いサーバーで実行する場合は `--engine workbench` を付けてください
(EEVEE より簡素な見た目ですが高速で、動きの参照用途には十分です)。

### 4. Seedance 2.0 で最終映像に変換

Seedance 2.0 は 1 回の生成が **4〜15 秒**なので、30 秒のプレビューを
**15 秒 × 2 本(または 10 秒 × 3 本)に分割**して生成し、あとで結合します。

- 各セグメントを `video_references`(動き・カメラの参照)として渡す
- 主人公の見た目を固定する画像を `image_references` に渡すとキャラが一貫する
- 2 本目以降は前セグメントの最終フレームを `start_image` に渡すと繋がりが自然
- プロンプト例:
  > 夕暮れの都市の屋上、トレーサーがコンクリートの壁をヴォルトして着地ロール、
  > 手持ちカメラで追従、実写風、モーションブラー
- 推奨設定: `mode: std / 1080p / generate_audio: true`(足音・環境音も自動生成)

## Mixamo なしで試運転する

Mixamo のファイルを用意する前にパイプラインを試したい場合は、
ダミーのモーションクリップを生成できます:

```bash
blender -b -P make_test_anims.py -- --out ./anims
blender -b -P build_parkour.py -- --anims ./anims --out ./out --render
```

## 細かい調整

`build_parkour.py` の先頭にある設定で調整できます:

- `DEFAULT_BLEND` … 繋ぎ目のブレンドフレーム数(大きいほど滑らか、デフォルト 12)
- `CAMERA_OFFSET` … カメラの位置(腰からの相対位置)
- `CLIP_OVERRIDES` … クリップごとのブレンド量・進行方向の追加回転(コースを曲げる)・障害物の種類
