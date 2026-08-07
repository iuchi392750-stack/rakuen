# 引き継ぎメモ — クラウドセッション → ローカルセッション

このファイルをローカルの Claude Code に読ませれば、続きから作業できます。

**最初にこれを伝えてください:**
> `HANDOFF.md` と `CLAUDE.md` を読んで、続きをやって。

---

## 1. いま何を作っているか

**ナイトライダー風の30秒映像**(実写調・オリジナルデザイン)。
参照画像は生成済みで、プロンプトも書き上がっている。**あとは生成するだけ**の状態。

前段までに作ったもの(すべてこのリポジトリに入っている):

| ファイル | 内容 |
|---|---|
| `seedance/knight_drive_30s.md` | **本命。**30秒のプロンプト本文と設定 |
| `seedance/seedance25_prompt_guide.md` | Seedance 2.5 公式プロンプト作法(必読) |
| `seedance/natsu_no_tonari_mv.md` | 青春MV「夏のとなり」企画(未着手) |
| `seedance/okinawa_whale_plot.md` | 沖縄の鯨MV企画(未着手) |
| `seedance/hailuo_h3_asset_package.md` | ファミコン風レース60秒のH3用素材(未着手) |
| `unity/` | ファミコン風レースゲーム(動作確認済み・調整中) |

## 2. なぜローカルに移すのか

クラウド環境では **PixVerse と Hailuo のドメインがネットワークポリシーで遮断**されていて、
API・CLI・ブラウザのいずれからも到達できなかった。ローカルなら問題なく使える。

遮断されていたもの:`pixverse.ai` / `app-api.pixverse.ai` / `hailuoai.video` /
`preview.hailuoai.video` / `api.minimax.chat` / 画像CDN(`d8j0ntlcm91z4.cloudfront.net`)

## 3. ローカルで最初にやること

```sh
npm install -g pixverse
pixverse auth login
npx skills add https://github.com/pixverseai/skills --skill pixverse-ai-image-and-video-generator
```

`auth login` でブラウザが開くので、PixVerse アカウントでログインする。
クラウド側ではここが 403 で止まっていた。

このリポジトリをまだ clone していない場合:

```sh
git clone -b claude/seedance-video-concepts-696vb4 https://github.com/iuchi392750-stack/rakuen.git
```

## 4. 参照画像4枚(要ダウンロード)

Higgsfield で生成済み。**higgsfield.ai のマイページから保存**して、
ローカルの作業フォルダに以下の名前で置く。クラウド側からは CDN が遮断されていて渡せなかった。

| ファイル名 | 内容 | プロンプト内の呼称 |
|---|---|---|
| `01_driver_sheet.png` | 主人公の三面図(全身+バストアップ) | `@Image 1` = `<ドライバー>` |
| `02_car_sheet.png` | 車の三面図(前面・側面・背面) | `@Image 2` = `<ブラッククーペ>` |
| `03_bg_highway.png` | 夜のハイウェイ | `@Image 3` = `<ハイウェイ>` |
| `04_bg_neon.png` | ネオンの繁華街 | `@Image 4` = `<ネオン街>` |

**アップロード順が `@Image 1`〜`4` の番号と一致していないと、人物と車の定義が入れ替わる。**

すべて Higgsfield Soul 2.0(`soul_2`)で生成、2048×1152。
作り直したい場合、プロンプトは `seedance/knight_drive_30s.md` に載っていない
(画像生成時のもの)ので、必要なら同じ仕様で再生成すること:
主人公は30代前半・黒レザージャケット・左眉に傷、車は黒のウェッジクーペ・
赤いピンストライプ・フロントノーズに赤いスキャナーライト。

## 5. 生成の実行

プロンプト本文は `seedance/knight_drive_30s.md` にある。そのまま使う。

**PixVerse CLI で回す場合の要点:**

- 30秒ワンショットに対応しているのは **Seedance 2.5** のみ(他は最大15〜20秒)
- 参照画像は最大7枚まで混ぜられる(`create reference`)
- 設定は CLI のフラグで渡す。**プロンプト本文には比率・尺・解像度を書かない**
  (Seedance 2.5 ではこれらが自動ロックされるため。`seedance25_prompt_guide.md` FIG 07)

設定値:16:9 / 30秒 / 720p / 音声あり

**Higgsfield 経由(クラウドでも可)の場合:**
`seedance_2_5` を `mode: omni_reference` で、`image_references` に4枚。
費用は195クレジット。ただし生成直後の画像は
`IP check not finished for input media` で弾かれることがある(時間を置けば通る)。

## 6. 未解決の課題

- **Seedance 2.5 の30秒生成が未実行。**参照画像の IP チェック待ちで2回失敗した
- Unity のレースゲームは動作するが、カメラの詰め具合は要調整
  (`RetroCamera` → `Chase Camera` の Trail / Lift / Ahead Look / Lateral Follow)

## 7. 作業のきまり

**動画プロンプトを書く前に、必ず `seedance/seedance25_prompt_guide.md` を読むこと。**
Seedance に限らず、PixVerse・Hailuo・Veo など**すべての動画生成モデルで同じ作法に従う。**
詳細は `CLAUDE.md` に記載。とくに外しやすいのは次の4点:

1. 比率・尺・解像度をプロンプト本文に書かない(UI/CLI 側で指定)
2. 参照素材には「使うもの」と「使わないもの」の両方を書く
   (書かないと白いスタジオ背景や三面図のレイアウトが出力に混ざる)
3. 出しうるものは個数を固定する(「出力には常に1台だけ映す」)
4. 1ステージ = 1変化。各ステージにフレームを止めて確認できる終了状態を書く
