# ファミコン風F1レース 60秒 — Hailuo (MiniMax H3) 用プロンプト集

15秒 × 4本 = 60秒 / 16:9 / 2K
主人公マシン:**赤・白・青のトリコロールカラーのF1マシン**

---

## 制作手順(Hailuo での操作)

1. **Clip 1** はテキスト+参照画像(添付のドット絵2枚)から生成
2. **Clip 2〜4** は、**前のクリップの最終フレームを書き出して「開始フレーム(首帧)」に設定**してから、下記プロンプトを入力
   - Hailuo の画面で生成済み動画の最終フレームを保存 → 次の生成の開始画像として指定
   - これで4本が途切れずに繋がります
3. 4本を書き出して動画編集ソフトで連結 → 60秒の完成尺

**共通のスタイル指定(全クリップに含める):**
`Famicom / NES era pixel art racing game, chunky visible pixels, limited retro color palette, no anti-aliasing, flat 2D sprite look, arcade game screen`

---

## Clip 1 — スタート(0:00–0:15)

### 英語版

```
Retro Famicom-era pixel art racing game footage, chunky visible pixels, limited color
palette, no anti-aliasing, flat 2D sprite look. Third-person view from behind a
red-white-blue tricolor Formula 1 car sitting on the starting grid of a pixel-art circuit.
Other pixel F1 cars line up alongside: a yellow-and-black car, a green-and-white car, an
orange-and-white car. Packed pixel crowd in grandstands on both sides, snow-capped blue
pixel mountains and blocky white clouds on the horizon, red-and-white striped curbs,
dashed white center line on grey asphalt. A tall start-signal gantry on the right side
lights RED, then YELLOW, then GREEN. On green all cars launch forward together, exhaust
puffs and horizontal speed lines, the road scrolling rapidly toward the camera. Retro HUD
overlay in pixel font. 16:9 arcade game screen, energetic.
```

### 日本語版

```
ファミコン時代のドット絵レースゲーム映像。粗いドット、レトロな限定色パレット、
アンチエイリアスなしの2Dスプライト調。赤白青のトリコロールカラーのF1マシンを真後ろから見た
視点。スターティンググリッドには黄×黒、緑×白、オレンジ×白のマシンが並ぶ。両側の観客席は
ドット絵の観衆でびっしり、地平線には雪をかぶった青い山並みとブロック状の白い雲、路肩には
赤白の縁石、灰色のアスファルトに白い破線のセンターライン。画面右のシグナル塔が赤→黄→緑と
点灯し、緑の瞬間に全車が一斉にスタートダッシュ。排気の煙と横方向のスピード線、路面が
高速で手前に流れる。ドット文字のレトロHUD表示。16:9のアーケードゲーム画面。
```

---

## Clip 2 — 集団バトル(0:15–0:30)

> **前提:** Clip 1 の最終フレームを開始フレームに設定

### 英語版

```
Continue the same Famicom-era pixel art racing game footage, identical chunky pixel style
and color palette. The red-white-blue tricolor F1 car races through the pack at high speed,
weaving between the orange-and-white and green-and-white pixel cars. The pixel road curves
left, red-and-white curbs scrolling past, dust and dirt pixels kicking up from the grass
verge. Grandstands and snow-capped pixel mountains sweep across the background, parallax
scrolling. Slipstream speed lines, tyre smoke sprites, the tricolor car overtakes two rivals
one after another. Retro HUD shows the position counter dropping. 16:9 arcade game screen,
fast and aggressive.
```

### 日本語版

```
同じファミコン風ドット絵レースゲーム映像の続き。粗いドットと色パレットは完全に統一。
赤白青のトリコロールF1マシンが高速で集団に突入し、オレンジ×白、緑×白のドット絵マシンの間を
縫うように走る。コースは左へカーブし、赤白の縁石が流れ、芝生から土煙のドットが舞い上がる。
背景の観客席と雪山が多重スクロールで流れる。スリップストリームのスピード線、タイヤスモークの
スプライト、トリコロールのマシンが2台を続けざまにオーバーテイク。レトロHUDの順位表示が
上がっていく。16:9アーケードゲーム画面、スピード感と迫力。
```

---

## Clip 3 — 首位との一騎打ち(0:30–0:45)

> **前提:** Clip 2 の最終フレームを開始フレームに設定

### 英語版

```
Continue the same Famicom-era pixel art racing game footage, identical pixel style. Now
only the yellow-and-black leader car remains ahead. The red-white-blue tricolor car closes
in and they run side by side down a long pixel straight, wheel to wheel, trading positions.
Sparks as pixel sprites fly from under the cars, heat shimmer lines, the crowd in the
grandstands waving pixel flags. Sunset light begins tinting the sky orange behind the
snow-capped mountains. Retro HUD shows FINAL LAP in blinking pixel font. Tense, dramatic,
16:9 arcade game screen.
```

### 日本語版

```
同じファミコン風ドット絵レースゲーム映像の続き。スタイル完全統一。前方に残るのは黄×黒の
トップマシンのみ。赤白青のトリコロールマシンが追いつき、長いストレートで真横に並んでの
サイド・バイ・サイドの攻防、抜きつ抜かれつ。車体の下からドット絵の火花が飛び散り、
陽炎の揺らぎ線、観客席ではドット絵の観衆が旗を振る。雪山の向こうの空が夕焼けの
オレンジに染まりはじめる。レトロHUDに「FINAL LAP」がドット文字で点滅。緊迫感と
ドラマ性。16:9アーケードゲーム画面。
```

---

## Clip 4 — 1位でゴール(0:45–1:00)

> **前提:** Clip 3 の最終フレームを開始フレームに設定

### 英語版

```
Continue the same Famicom-era pixel art racing game footage, identical pixel style. Final
corner: the red-white-blue tricolor F1 car takes the inside line and pulls decisively ahead
of the yellow-and-black car onto the last straight. It crosses the finish line in FIRST
PLACE under a black-and-white checkered flag waving in chunky pixels, checkered start-finish
gantry overhead. Confetti pixels burst, the pixel crowd leaps up cheering, fireworks sprites
pop in the orange sunset sky. The car does a victory slide, and a retro results screen
appears in pixel font: "1st PLACE — WINNER!" with a golden pixel trophy. Triumphant,
celebratory, 16:9 arcade game screen.
```

### 日本語版

```
同じファミコン風ドット絵レースゲーム映像の続き。スタイル完全統一。最終コーナーで
赤白青のトリコロールF1マシンがインを差し、黄×黒のマシンを決定的に抜き去って最終ストレートへ。
頭上のチェッカー柄のゲートの下、粗いドットではためく白黒のチェッカーフラッグを受けて
**1位でフィニッシュラインを通過**。紙吹雪のドットが舞い、観客が飛び上がって歓声、
夕焼けのオレンジの空に花火のスプライトが弾ける。マシンがビクトリースライドを決め、
ドット文字のリザルト画面「1st PLACE — WINNER!」と金色のドット絵トロフィーが表示される。
高揚感と祝祭感。16:9アーケードゲーム画面。
```

---

## Hailuo 推奨設定

| 項目 | 値 |
|---|---|
| モデル | MiniMax H3(Hailuo) |
| 尺 | 15秒 × 4本 |
| 解像度 | 2K |
| アスペクト比 | 16:9 |
| 参照 | Clip 1 = 添付ドット絵2枚を画像参照 / Clip 2〜4 = 前クリップの最終フレームを開始フレームに指定 |

## 音について

MiniMax H3 は動画のみで音声は出力されません。ファミコン風のチップチューンBGMと
効果音(エンジン音、シフト音、歓声、ファンファーレ)を Suno などで別途作成し、
編集ソフトで合わせてください。

**Suno 用スタイル指定の例:**
```
8-bit chiptune, NES soundtrack, upbeat racing game BGM, fast tempo 160bpm,
square wave lead, driving bassline, triumphant finale
```
