# 天の川の再会 — 30秒ショートフィルム 制作資料

七夕・天の川伝説を舞台にした「奇跡の再会」を描く30秒映像（15秒×2パート、Pixverseで生成）。

---

## 1. 生成済みビジュアル素材

| 素材 | 内容 | URL |
|---|---|---|
| 彼女・三面図（過去↔現在） | 左：7年前・16歳セーラー夏服／右：現在・23歳ラベンダーの星のドレス。各 正面・側面・背面 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260707_232828_884bbdca-1d08-4fef-8e7e-17c6d2978314.png |
| 彼・三面図（過去↔現在） | 左：7年前・16歳学ラン／右：現在・23歳水色シャツ。各 正面・側面・背面 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260707_232841_219fc4ff-4cf7-4bd5-a607-c333a807c7e9.png |
| メイン背景（過去と今が同居） | 川辺の遊歩道と橋。左＝7年前の七夕祭りの夕暮れ（笹飾り・短冊・提灯）、右＝現在の天の川と流星群の夜。空が夕暮れ→星夜へシームレスに遷移 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260707_232849_514f50c4-227e-41c7-86de-affe30cf89b9.png |

参照元（ユーザー提供）: `girl_ref.png` / `boy_ref.png` / `bg_ref.png`（同ディレクトリ）

---

## 2. プロット（背景設定）

**七夕の夜。彦星と織姫のように、一年に一度だけ天の川が二人を引き合わせた。**

- 7年前の七夕祭りの夜、高校生だった二人は川辺の橋で「来年もここで」と約束した。
- その直後、彼女は交通事故に遭う。彼が聞かされたのは「彼女は亡くなった」という話だけだった。
- 彼女の家族は町を離れ、連絡先も消えた。彼は7年間、七夕のたびにひとりで橋に立ち続けた。
- 真実は違った。彼女は意識不明の重体のまま遠い町の病院で眠り続け、そして奇跡的に目を覚ましていた。
- 今年、共通の友人からの伝え聞きで彼女は知る——彼が今も毎年あの橋に来ていることを。
- 流星群の降る七夕の夜。天の川の橋の上で、死んだはずの彼女が彼の前に現れる。

**30秒構成**
- Part 1（0:00–0:15）「過去 — 喪失と7年」: 祭りの記憶→事故の報せ→ひとりで橋に立ち続ける彼。ラストは現在の橋の上、天の川の下にひとり立つ彼。
- Part 2（0:15–0:30）「現在 — 流星群の再会」: Part 1最終フレームから継続。流星群が激しくなり、橋の向こうに彼女が現れ、歩み寄り、涙の再会。引きの絵で天の川のアーチと無数の流星が二人を祝福して終わる。

---

## 3. Pixverse 動画プロンプト

共通設定: 16:9 / アニメ調（Makoto Shinkai風の深い藍紫の夜空、紫ピンクに輝く天の川、濡れた路面の反射）/ 各15秒。
画像参照: キャラ三面図2枚＋メイン背景を image reference / character reference に指定。

### Part 1（0:00–0:15）「過去 — 喪失と7年」

**開始フレーム参照**: メイン背景（過去と今が同居する橋の絵）＋二人の三面図（過去側の制服姿）

```
アニメ映画風、16:9。七夕祭りの夕暮れの川辺の橋。笹飾りと色とりどりの短冊が風に揺れ、提灯が温かく灯る。学ラン姿の16歳の少年と、セーラー夏服の長い黒髪の少女が橋の上で笑い合い、小指を絡めて約束を交わす（0-5秒）。画面が雨に滲み、色彩が消えていく。傘も差さず立ち尽くす少年、手から滑り落ちる携帯電話、遠ざかる救急車の光——「彼女は死んだ」という報せ（5-9秒）。時間経過のモンタージュ：同じ橋、移ろう季節、成長していく彼のシルエット。空は夕暮れから深い星夜へと変わり、紫ピンクの天の川が空に架かる（9-13秒）。ラストカット：23歳になった彼（水色のシャツ、ネイビーのパンツ）が夜の橋の中央にひとり立ち、天の川を見上げる。一筋の流れ星が空を切る。カメラは彼の背中越しにゆっくりと引き、静止（13-15秒）。切なく静かな余韻。
```

英語版:

```
Anime film style, 16:9. A riverside bridge at Tanabata festival dusk: bamboo branches with colorful tanzaku wishes, warm paper lanterns. A 16-year-old boy in a black gakuran and a girl with long dark hair in a white sailor summer uniform laugh together on the bridge and make a pinky promise (0-5s). The frame blurs into rain, colors draining away — the boy stands frozen in the downpour, a phone slipping from his hand, distant ambulance lights: the news that she died (5-9s). Time-lapse montage over the same bridge: seasons change, his silhouette grows older, the sky shifts from dusk into a deep starry night as the purple-pink Milky Way arcs overhead (9-13s). Final shot: now 23, in a light blue open shirt and navy trousers, he stands alone at the center of the bridge looking up at the Milky Way; a single shooting star cuts the sky. Camera slowly pulls back over his shoulder and holds still (13-15s). Quiet, aching stillness.
```

**重要**: Part 1の最終フレーム（橋の中央に立つ彼の後ろ姿＋天の川＋最初の流れ星）で必ず静止して終わること。この最終フレームがPart 2の開始参照になる。

### Part 2（0:15–0:30）「現在 — 流星群の再会」

**開始フレーム参照**: **Part 1の最終フレームを first frame / image reference に指定**（前パート最終フレーム参照）。＋彼女の三面図（現在側・ラベンダーのドレス）

```
前クリップの最終フレームから継続。アニメ映画風、16:9。天の川の下、橋の中央に立つ彼の背中。空一面に流星群が降り始め、数十の流れ星が紫ピンクの天の川を切り裂き、川面と濡れた路面にきらめきが反射する（15-19秒）。彼がふと顔を上げると、橋の向こう端に淡い光をまとった人影——星の髪飾りを付け、透けるラベンダーのドレスを着た長い黒髪の彼女。死んだはずの少女が、そこに立っている（19-22秒）。彼女が静かに歩み寄る。ドレスと髪が夜風になびき、流星の光が彼女を包む。彼の目に涙があふれ、信じられないように一歩、また一歩と近づく（22-26秒）。二人は向かい合い、彼女が涙ながらに微笑む——「ただいま」。彼が彼女の手を取る。カメラは大きく引き、天の川のアーチと降り注ぐ無数の流星の下、川面に映る二人のシルエットで終わる（26-30秒）。奇跡的で美しい大団円。
```

英語版:

```
Continue from the final frame of the previous clip. Anime film style, 16:9. His back at the center of the bridge under the Milky Way. A meteor shower erupts across the whole sky — dozens of shooting stars slicing through the purple-pink galaxy, their light shimmering on the river and wet pavement (15-19s). He looks up, then notices a figure at the far end of the bridge, wrapped in faint light: a young woman with very long dark hair, star hair ornaments, and a sheer lavender layered dress. The girl who was supposed to be dead is standing there (19-22s). She walks slowly toward him, dress and hair drifting in the night wind, meteor light haloing her. Tears well in his eyes as he steps forward in disbelief, one step, then another (22-26s). They stop face to face; she smiles through tears — "I'm home." He takes her hand. The camera pulls far back: beneath the arch of the Milky Way and countless falling stars, their two silhouettes reflect on the river (26-30s). A miraculous, beautiful reunion finale.
```

### ネガティブプロンプト（両パート共通）

```
low quality, blurry, distorted faces, extra fingers, text, watermark, photorealistic, 3DCG, horror, gore, character design change, different hairstyle, different outfit
```

### Pixverse運用メモ

- Pixverseの1クリップ上限が15秒未満のプラン/モデルの場合は、各パートを 8秒＋7秒（または5秒×3）に分割し、必ず「前クリップの最終フレーム→次クリップの開始フレーム」で連結する（Part内も同じ最終フレーム参照方式）。
- キャラの同一性維持のため、三面図の「現在」側を切り出してcharacter referenceに使うと安定する。
- Part 1→Part 2の橋・空・彼の立ち位置が一致していることを書き出し前に確認。
- BGM想定: 静かなピアノ（Part 1）→ストリングスが広がる（Part 2後半）。
