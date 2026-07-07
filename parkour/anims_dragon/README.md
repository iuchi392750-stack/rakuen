# ここに剣士用の Mixamo FBX を入れてください

Mixamo で「Sword and Shield」系を検索すると剣士のモーションが揃います。
ダウンロード設定はパルクールと同じ(**FBX Binary / 30fps / In Place オフ**、
最初の 1 本だけ **With Skin**)。

## おすすめの構成(番号順に再生されます)

| ファイル名 | Mixamo での検索キーワード | 役割 |
|---|---|---|
| `01_walk.fbx` | Sword And Shield Walk | 洞窟を歩いて進む(With Skin) |
| `02_run.fbx` | Sword And Shield Run | 駆け出す |
| `03_dodge.fbx` | Sword And Shield Roll / Dodge | 回避アクション |
| `04_slash.fbx` | Sword And Shield Slash | 戦闘開始(この位置の先にドラゴンが立つ) |
| `05_attack.fbx` | Sword And Shield Attack | 連続攻撃 |
| `06_victory.fbx` | Sword And Shield Power Up / Victory | このクリップが始まるとドラゴンが倒れる |

- ファイル名に `slash` / `attack` / `combo` / `fight` を含むクリップの位置にドラゴンが配置されます
- `victory` を含むクリップが始まるタイミングでドラゴンが崩れ落ちます(無い場合は最後の攻撃の終わり)
- `walk` / `run` を含むクリップは尺が足りないとき自動で繰り返されます

## 実行

```bash
cd parkour
blender -b -P build_dragon.py -- --anims ./anims_dragon --out ./out_dragon --seconds 15 --render
```

`out_dragon/dragon_reference.mp4` ができたら、それを Seedance 2.0 の video_reference に渡します。
