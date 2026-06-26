# FF7風スチームパンク都市シーン — Blender自動生成プロジェクト

Seedance 2.0に渡す参照動画を、Blenderで自動生成するプロジェクトです。  
シーン内容：上空から降下しながら、花売り少女に通行人がぶつかり転倒するワンカット映像（15秒 / 1920×1080 / 24fps）。

---

## ディレクトリ構成

```
blender_ff7_scene/
├── create_scene.py          # Blenderシーン生成メインスクリプト
├── render_viewport.py       # レンダリング実行スクリプト
├── run_blender_render.bat   # Windows用ワンクリック実行バッチ
├── config.json              # 全パラメータ設定ファイル
├── README.md                # このファイル
├── assets/                  # ← ここにモデルを配置（自動作成）
│   ├── flower_girl_fall.fbx
│   └── passerby_walk.fbx
└── output/                  # レンダリング結果（自動作成）
    ├── flower_scene_reference.mp4
    └── ff7_scene.blend
```

---

## 必要なモデルファイル

### `assets/flower_girl_fall.fbx`
- **内容**: 花売り少女のリグ付きキャラクター＋転倒アニメーション
- **推奨アニメーション**: `Falling Back` / `Stumble Backwards` / `Getting Hit`

### `assets/passerby_walk.fbx`
- **内容**: 通行人（男）のリグ付きキャラクター＋歩行アニメーション
- **推奨アニメーション**: `Walking` / `Casual Walk`

---

## モデルの入手方法（Mixamo推奨）

1. [Mixamo](https://www.mixamo.com/) にAdobeアカウントでサインイン
2. 「Characters」からキャラクターを選択（例: Xbot / Ybot）
3. 「Animations」タブで上記アニメーションを検索・選択
4. **Download設定**:
   - Format: `FBX`
   - Skin: `With Skin`
   - Frames per Second: `24`
   - Keyframe Reduction: `none`
5. ダウンロードしたファイルを `assets/` フォルダにリネームして配置

> **ヒント**: flower_girl_fall.fbxとpasserby_walk.fbxは別々のキャラクターで問題ありません。  
> Blenderのスクリプトがそれぞれ自動でスケール・位置・向きを調整します。

---

## 実行方法

### 方法A: run_blender_render.bat（Windows推奨）

#### Blenderパスの変更方法

`run_blender_render.bat` をテキストエディタで開き、以下の行を環境に合わせて編集します：

```bat
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
```

Blenderのインストール場所の調べ方：
- スタートメニューで「Blender」を右クリック → 「ファイルの場所を開く」
- またはBlenderを起動して `Edit > Preferences > File Paths` で確認

バージョン別パス例：
```
Blender 4.2:  C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
Blender 4.1:  C:\Program Files\Blender Foundation\Blender 4.1\blender.exe
Blender 4.0:  C:\Program Files\Blender Foundation\Blender 4.0\blender.exe
```

編集後、`run_blender_render.bat` をダブルクリックで実行。  
`output/flower_scene_reference.mp4` が生成されます。

---

### 方法B: Blenderで手動実行

#### シーンのみ生成（.blendファイル確認用）

1. Blenderを起動
2. `Scripting` ワークスペースに切り替え
3. 「Open」から `create_scene.py` を選択
4. 「Run Script」ボタン（▶）をクリック
5. `output/ff7_scene.blend` が生成される

#### レンダリングまで一括実行

1. 同様に `render_viewport.py` を開いて「Run Script」
2. シーン生成＋MP4出力まで自動実行

#### コマンドラインから実行

```bash
# シーン生成のみ
blender --background --python create_scene.py

# レンダリングまで一括
blender --background --python render_viewport.py
```

---

## config.json でカスタマイズ

モデルのサイズ・向き・位置が合わない場合は `config.json` を編集します。

### モデルスケールの調整

Mixamoモデルは通常 `0.01` で約1.7m人物サイズになります。

```json
"flower_girl": {
  "scale": [0.01, 0.01, 0.01]   ← 大きすぎる場合は小さく、小さい場合は大きく
}
```

### モデルの向き調整

FBXの軸設定によって向きがずれる場合があります：

```json
"rotation_euler_deg": [90, 0, 180]
```

| 問題 | 修正例 |
|------|--------|
| 人物が横倒しになっている | `[0, 0, 180]` |
| 人物が後ろ向き | `[90, 0, 0]` |
| 人物が反転している | `[90, 0, 180]` → `[90, 0, 0]` |

### 少女の位置

```json
"position": [2.0, 0.0, 0.0]   ← X: 道路からの距離, Y: 奥行き方向
```

### 男の歩行ルート

```json
"walk_route": [
  [-12.0, 0.5, 0.0],   ← 画面左端からスタート
  [ 2.0,  0.5, 0.0],   ← 少女付近（衝突点）
  [ 14.0, 0.5, 0.0]    ← 画面右端へ退場
]
```

### タイミング調整

```json
"animation": {
  "fall_start_frame": 220,       ← 転倒モーション開始
  "collision_frame": 235,        ← 男が少女にぶつかる
  "flower_drop_frame": 245,      ← 花束が地面に落ちる
  "flower_stomp_start_frame": 300,   ← 男が花を踏み始める
  "flower_stomp_end_frame": 320      ← 花が完全に潰れる
}
```

---

## シーン仕様

| 項目 | 設定値 |
|------|--------|
| 解像度 | 1920 × 1080 |
| フレームレート | 24fps |
| 総フレーム数 | 360フレーム（15秒） |
| フォーマット | MP4 / H.264 |
| レンダラー | EEVEE（高速） |
| カメラ | 1カット・自然降下・カット割りなし |

### タイムライン概要

```
フレーム   1 〜  60  : 上空から見下ろし、都市全景
フレーム  60 〜 180  : カメラが自然に降下、車が行き交う
フレーム 180 〜 220  : 少女の近くへ、男が歩いてくる
フレーム 220         : 少女の転倒モーション開始
フレーム 235         : 男が少女にぶつかる
フレーム 245         : 花束が地面に落ちる
フレーム 300 〜 320  : 男の足が花を踏み潰す
フレーム 320 〜 360  : 引きで状況を映す
```

---

## トラブルシューティング

### Q: 「assets/flower_girl_fall.fbx がありません」と表示される
→ `assets/` フォルダにFBXファイルを配置してください（README上部の入手方法参照）。

### Q: 人物が地面に埋まる / 宙に浮いている
→ `config.json` の `position` の Z値と `scale` を調整してください。

### Q: 人物が極端に大きい / 小さい
→ `scale` の値を調整。通常 `0.01` が標準的なMixamoモデルのサイズです。

### Q: Blenderが「FFmpegが見つかりません」と言う
→ Blender公式サイト（blender.org）からダウンロードした版を使ってください。  
　FFmpegが同梱されており、MP4出力が可能です。

### Q: EEVEE でレンダリングが遅い
→ `config.json` の `render.engine` を変更するか、解像度を下げてテストしてください。  
　確認後に `1920x1080` でレンダリングすることを推奨します。
