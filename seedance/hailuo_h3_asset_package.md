# ファミコン風F1レース 60秒 — Hailuo H3 投入用 素材一式

**保存先:** `C:\新Suno\Hailou\`
**生成環境:** https://preview.hailuoai.video/ (MiniMax H3 / Omni Reference ON / 15秒)

---

## 1. ファイル構成

以下のファイル名で `C:\新Suno\Hailou\` に配置してください。
**プロンプト内の `@ファイル名` はこの名前と完全に一致させる必要があります。**

```
C:\新Suno\Hailou\
├─ car_sheet.png     ← 三面図(F1マシン 前/側面/背面 × 4カラー)※添付済み画像
└─ track_bg.png      ← 背景(サーキット・雪山・観客席)※添付済み画像

※ BGM は動画完成後の「後入れ」。生成時にはアップロードしない。
```

---

## 2. Hailuo H3 での操作手順(各クリップ共通)

1. https://preview.hailuoai.video/ を開き、CPP登録済みアカウントでログイン
2. モデルに **`MiniMax H3`** を選択
3. **`Omni Reference` を ON**
4. 素材をアップロード
   - **Clip 1:** `car_sheet.png` + `track_bg.png`
   - **Clip 2〜4:** 上記2枚 + **前クリップの最終フレーム画像**(`last_frame_01.png` 等として保存)
5. 下記プロンプトを貼り付け
6. 尺 **15秒** / 16:9 で生成

**最終フレームの引き継ぎ:** 生成後、動画の最終フレームを静止画で書き出し
(`last_frame_01.png` など)、次のクリップにアップロードして `@last_frame_01` で参照します。

---

## 3. プロンプト(@参照付き)

### Clip 1 — スタート(0:00–0:15)

```
@car_sheet の赤白青トリコロールのF1マシンを主人公に、@track_bg のサーキットを舞台にした
ファミコン風ドット絵レースゲーム映像。粗いドット、レトロな限定色パレット、アンチエイリアス
なしの2Dスプライト調。

主人公マシンを真後ろから見た三人称視点。スターティンググリッドには @car_sheet の黄×黒、
緑×白、オレンジ×白のマシンが並ぶ。両側の観客席はドット絵の観衆で埋まり、地平線には雪山と
ブロック状の白い雲、路肩に赤白の縁石、灰色のアスファルトに白い破線。

画面右のシグナル塔が赤→黄→緑と点灯し、緑の瞬間に全車が一斉にスタートダッシュ。排気の煙と
横方向のスピード線、路面が高速で手前に流れる。ドット文字のレトロHUD表示。

16:9、15秒。
```

### Clip 2 — 集団バトル(0:15–0:30)

```
@last_frame_01 から途切れなく continue。@car_sheet と @track_bg のドット絵スタイルと
色パレットを完全に維持。

赤白青のトリコロールF1マシンが高速で集団に突入し、オレンジ×白、緑×白のマシンの間を縫うように
走る。コースは左へカーブし、赤白の縁石が流れ、芝生から土煙のドットが舞い上がる。背景の観客席と
雪山が多重スクロール。スリップストリームのスピード線、タイヤスモークのスプライト、
トリコロールのマシンが2台を続けざまにオーバーテイク。HUDの順位表示が上がっていく。

16:9、15秒。
```

### Clip 3 — 首位との一騎打ち(0:30–0:45)

```
@last_frame_02 から途切れなく continue。@car_sheet と @track_bg のドット絵スタイルを維持。

前方に残るのは @car_sheet の黄×黒のトップマシンのみ。赤白青のトリコロールマシンが追いつき、
長いストレートで真横に並んでのサイド・バイ・サイドの攻防、抜きつ抜かれつ。車体の下から
ドット絵の火花が飛び散り、陽炎の揺らぎ線、観客席の観衆が旗を振る。雪山の向こうの空が
夕焼けのオレンジに染まりはじめる。HUDに「FINAL LAP」がドット文字で点滅。

16:9、15秒。
```

### Clip 4 — 1位でゴール(0:45–1:00)

```
@last_frame_03 から途切れなく continue。@car_sheet と @track_bg のドット絵スタイルを維持。

最終コーナーで赤白青のトリコロールF1マシンがインを差し、黄×黒のマシンを決定的に抜き去って
最終ストレートへ。頭上のチェッカー柄のゲートの下、粗いドットではためく白黒のチェッカー
フラッグを受けて1位でフィニッシュラインを通過。紙吹雪のドットが舞い、観客が飛び上がって歓声、
夕焼けの空に花火のスプライトが弾ける。マシンがビクトリースライドを決め、ドット文字の
リザルト画面「1st PLACE — WINNER!」と金色のドット絵トロフィーが表示される。

16:9、15秒。
```

---

## 4. 4本の連結

4本を書き出したら、編集ソフトで順に連結して60秒に。
ffmpeg で連結する場合は `concat.txt` を作成:

```
file 'clip_01.mp4'
file 'clip_02.mp4'
file 'clip_03.mp4'
file 'clip_04.mp4'
```

```bat
ffmpeg -f concat -safe 0 -i concat.txt -c copy final_60s.mp4
```

---

## 5. BGM(後入れ)

動画4本が完成してから Suno で作成し、編集ソフトで乗せる。

### Suno スタイル指定

```
8-bit chiptune, NES / Famicom soundtrack, upbeat racing game BGM, 160bpm,
square wave lead, driving triangle bassline, noise-channel percussion,
tension build in the middle, triumphant victory fanfare at the end, instrumental
```

**構成:** 60秒。0–15秒はスタートの緊張と加速、15–30秒は疾走感、30–45秒はテンション上昇、
45–60秒は勝利のファンファーレ。

### 連結済み動画へのBGM合成(ffmpeg)

```bat
ffmpeg -i final_60s.mp4 -i bgm_full.mp3 -c:v copy -c:a aac -shortest final_60s_bgm.mp4
```

---

## 6. チェックリスト

- [ ] `car_sheet.png` / `track_bg.png` を `C:\新Suno\Hailou\` に配置
- [ ] preview.hailuoai.video にログイン → MiniMax H3 / Omni Reference ON
- [ ] Clip 1 生成 → 最終フレームを `last_frame_01.png` で保存
- [ ] Clip 2 生成 → `last_frame_02.png` 保存
- [ ] Clip 3 生成 → `last_frame_03.png` 保存
- [ ] Clip 4 生成(1位でゴール)
- [ ] 4本を連結して `final_60s.mp4`
- [ ] Suno で60秒BGMを作成 → ffmpeg で合成して `final_60s_bgm.mp4` 完成
