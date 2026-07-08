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

## 3. Pixverse 動画プロンプト（15秒×2クリップ、計30秒）

Pixverseは1クリップ最大15秒のため、**独立した2本のクリップ**として生成し、編集で連結する。

共通設定:
- 尺: **各15秒（Duration: 15s）**
- アスペクト比: 16:9
- スタイル: アニメ調（Makoto Shinkai風の深い藍紫の夜空、紫ピンクに輝く天の川、濡れた路面の反射）

---

### クリップ①（動画の0:00–0:15）「過去 — 喪失と7年」

**画像参照（開始フレーム）**: メイン背景（過去と今が同居する橋の絵）
**キャラクター参照**: 彼の三面図・彼女の三面図（過去側の制服姿）

プロンプト（日本語）:

```
アニメ映画風、16:9。七夕祭りの夕暮れの川辺の橋。笹飾りと色とりどりの短冊が風に揺れ、提灯が温かく灯る。学ラン姿の16歳の少年と、セーラー夏服の長い黒髪の少女が橋の上で笑い合い、小指を絡めて約束を交わす（0-5秒）。画面が雨に滲み、色彩が消えていく。傘も差さず立ち尽くす少年、手から滑り落ちる携帯電話、遠ざかる救急車の光——「彼女は死んだ」という報せ（5-9秒）。時間経過のモンタージュ：同じ橋、移ろう季節、成長していく彼のシルエット。空は夕暮れから深い星夜へと変わり、紫ピンクの天の川が空に架かる（9-13秒）。ラストカット：23歳になった彼（水色のシャツ、ネイビーのパンツ）が夜の橋の中央にひとり立ち、天の川を見上げる。一筋の流れ星が空を切る。カメラは彼の背中越しにゆっくりと引き、完全に静止した構図で終わる（13-15秒）。切なく静かな余韻。
```

プロンプト（英語）:

```
Anime film style, 16:9. A riverside bridge at Tanabata festival dusk: bamboo branches with colorful tanzaku wishes, warm paper lanterns. A 16-year-old boy in a black gakuran and a girl with long dark hair in a white sailor summer uniform laugh together on the bridge and make a pinky promise (0-5s). The frame blurs into rain, colors draining away — the boy stands frozen in the downpour, a phone slipping from his hand, distant ambulance lights: the news that she died (5-9s). Time-lapse montage over the same bridge: seasons change, his silhouette grows older, the sky shifts from dusk into a deep starry night as the purple-pink Milky Way arcs overhead (9-13s). Final shot: now 23, in a light blue open shirt and navy trousers, he stands alone at the center of the bridge looking up at the Milky Way; a single shooting star cuts the sky. Camera slowly pulls back over his shoulder and ends on a completely still, stable composition (13-15s). Quiet, aching stillness.
```

**このクリップの終わり方が重要**: 最終フレームは「橋の中央に立つ彼の後ろ姿＋天の川＋一筋の流れ星」の静止構図で終わらせること。この絵がクリップ②の開始フレームになる。

---

### クリップ②（動画の0:15–0:30）「現在 — 流星群の再会」 ※クリップ単体では0:00–0:15

**最終フレーム参照（必須）**: **クリップ①の最終フレームを書き出し（スクリーンショットまたはPixverseの「Extend/Last frame」機能）、このクリップの開始フレーム（First Frame / Image reference）に指定する。** これにより橋・空・彼の立ち位置がクリップ①から途切れずに継続する。
**キャラクター参照**: 彼女の三面図（現在側・ラベンダーのドレス）

プロンプト（日本語・秒数はクリップ②内の時間）:

```
開始フレーム（前クリップの最終フレーム：天の川の下、橋の中央に立つ彼の後ろ姿）から連続して動き出す。アニメ映画風、16:9。空一面に流星群が降り始め、数十の流れ星が紫ピンクの天の川を切り裂き、川面と濡れた路面にきらめきが反射する（0-4秒）。彼がふと顔を上げると、橋の向こう端に淡い光をまとった人影——星の髪飾りを付け、透けるラベンダーのドレスを着た長い黒髪の彼女。死んだはずの少女が、そこに立っている（4-7秒）。彼女が静かに歩み寄る。ドレスと髪が夜風になびき、流星の光が彼女を包む。彼の目に涙があふれ、信じられないように一歩、また一歩と近づく（7-11秒）。二人は向かい合い、彼女が涙ながらに微笑む——「ただいま」。彼が彼女の手を取る。カメラは大きく引き、天の川のアーチと降り注ぐ無数の流星の下、川面に映る二人のシルエットで終わる（11-15秒）。奇跡的で美しい大団円。
```

プロンプト（英語）:

```
Start from the given first frame (the final frame of the previous clip: his back at the center of the bridge under the Milky Way) and continue the motion seamlessly. Anime film style, 16:9. A meteor shower erupts across the whole sky — dozens of shooting stars slicing through the purple-pink galaxy, their light shimmering on the river and wet pavement (0-4s). He looks up, then notices a figure at the far end of the bridge, wrapped in faint light: a young woman with very long dark hair, star hair ornaments, and a sheer lavender layered dress. The girl who was supposed to be dead is standing there (4-7s). She walks slowly toward him, dress and hair drifting in the night wind, meteor light haloing her. Tears well in his eyes as he steps forward in disbelief, one step, then another (7-11s). They stop face to face; she smiles through tears — "I'm home." He takes her hand. The camera pulls far back: beneath the arch of the Milky Way and countless falling stars, their two silhouettes reflect on the river (11-15s). A miraculous, beautiful reunion finale.
```

---

### ネガティブプロンプト（両クリップ共通）

```
low quality, blurry, distorted faces, extra fingers, text, watermark, photorealistic, 3DCG, horror, gore, character design change, different hairstyle, different outfit
```

## 4. 動画コンテ（Gemini omni 参照動画用）

Blenderプリビズの代わりに、**動画コンテ→Gemini omniで参照動画を生成→Pixverseでその動画＋三面図＋背景を参照して本番生成**というフロー用のコンテ。絵はラフ、**キャラの動き（赤矢印）とカメラワーク（青矢印）優先**。

| コンテ | 内容 |
|---|---|
| Part 1『過去 — 喪失と7年』(15秒/5カット) | CUT01 約束（小指）→ CUT02 雨・事故の報せ → CUT03 時間経過タイムラプス → CUT04 現在の彼が橋へ歩く → CUT05 見上げる＋流れ星1本、プルバックして完全静止（**最終フレーム＝Part 2開始**） |
| Part 2『現在 — 流星群の再会』(15秒/5カット) | CUT06 同構図から流星群開始 → CUT07 振り向くと彼女 → CUT08 歩み寄り → CUT09 手を取る → CUT10 クレーン上昇の大引きで静止 |

| 動画コンテ Part 1 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260708_013520_8cd8bc2f-1a8c-4049-bd0b-643eadcda3ef.png |
| 動画コンテ Part 2 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260708_013624_dedb01d9-48e6-4aae-95a4-6f9edc127ec3.png |

### Gemini omni用プロンプト — 参照動画 Part 1（15秒）

添付: 動画コンテ Part 1 の画像

```
添付の動画コンテ（Part 1）の通りに、16:9・15秒の映像を生成してください。これはPixverseの参照動画（プリビズ）に使うため、絵の質感よりもキャラクターの動き・タイミング・カメラワークの正確さを最優先してください。スタイルはシンプルなアニメ調で構いません。
0-3秒: 橋の上で制服の少年と少女が向かい合い、笑って小指をつなぐ。カメラはミディアムからゆっくりドリーイン。
3-6秒: 雨の中、少年がひとり立ち尽くし、手から携帯電話が落ちる。奥を救急車の光が横切る。カメラ固定。
6-9秒: 同じ橋の遠景タイムラプス。空が夕暮れから星空へ変わり、橋の上の少年のシルエットが大人へ成長する。カメラ固定。
9-12秒: 現在の青年が画面右から橋の中央へゆっくり歩く。カメラは横移動で追従。
12-15秒: 青年が橋の中央で立ち止まり、天の川を見上げる。流れ星が1本流れる。カメラは背後からゆっくりプルバックし、最後の1秒は完全に静止して終わる。
```

### Gemini omni用プロンプト — 参照動画 Part 2（15秒）

添付: 動画コンテ Part 2 の画像 ＋ **Part 1参照動画の最終フレーム（静止画で書き出して開始フレーム参照に指定）**

```
添付の動画コンテ（Part 2）の通りに、16:9・15秒の映像を生成してください。開始フレームには添付した「Part 1の最終フレーム」を使用し、同じ構図（天の川の下、橋の中央に立つ青年の後ろ姿）から連続して始めてください。Pixverseの参照動画（プリビズ）用のため、動き・タイミング・カメラワークの正確さを最優先してください。
0-3秒: 静止構図から空一面に流星群が降り始める。カメラ固定。
3-6秒: 青年がはっと振り向くと、橋の向こう端に長い髪の女性が淡い光をまとって立っている。彼の肩越しにパン。
6-9秒: 彼女が奥からゆっくり歩み寄り、髪とドレスが風になびく。彼も一歩ずつ近づく。カメラはゆっくりドリーイン。
9-12秒: 二人は向かい合って立ち止まり、彼女が涙ながらに微笑み、彼が彼女の手を取る。カメラは寄りのままゆるやかに回り込む。
12-15秒: カメラがクレーン上昇しながら大きく引き、天の川のアーチと降り注ぐ流星群の下、橋の上で手をつなぐ二人の小さなシルエットと川面の反射で静止して終わる。
```

### 生成済み参照動画（Gemini omni / Higgsfield MCP経由・720p・16:9）

Gemini omni（Higgsfield上の `gemini_omni`）は1本最大10秒のため、各パートをカット境界で 9秒＋6秒 に分割して計4本生成。後続クリップは前クリップの動画参照（video_references）で連結済み。

| クリップ | 内容 | URL |
|---|---|---|
| Part 1-a（9秒 / CUT01〜03） | 約束→雨の報せ→タイムラプス | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260708_014038_5329d45a-56a9-4a4c-b70e-f8afdc8ce5b2.mp4 |
| Part 1-b（6秒 / CUT04〜05） | 現在の彼が橋へ→見上げて流れ星、静止 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260708_014057_8b6face8-5124-4bf6-bd7c-8933620255aa.mp4 |
| Part 2-a（9秒 / CUT06〜08） | 流星群→振り向くと彼女→歩み寄り（Part 1-b を動画参照） | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260708_014812_523850cf-61e9-44b7-99c1-2d0d999f7c17.mp4 |
| Part 2-b（6秒 / CUT09〜10） | 手を取る→クレーン上昇の大引きで静止（Part 2-a を動画参照） | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260708_015508_3ec39d1c-bd7b-4203-a6ba-2257a5f58f60.mp4 |

Pixverseでは Part 1-a + 1-b を繋いだものをパート1の参照動画、Part 2-a + 2-b をパート2の参照動画として使用する。

### Pixverse本番生成での参照の組み合わせ

| クリップ | 参照動画 | 画像参照 | テキスト |
|---|---|---|---|
| ① 過去 | Gemini omni参照動画 Part 1 | 三面図（過去側）＋メイン背景 | §3 クリップ①プロンプト |
| ② 現在 | Gemini omni参照動画 Part 2 | 三面図（彼女・現在側）＋**クリップ①最終フレーム** | §3 クリップ②プロンプト |

### Pixverse運用手順まとめ

1. クリップ①を15秒で生成（開始フレーム＝メイン背景、キャラ参照＝三面図の過去側）。
2. クリップ①の**最終フレームを取得**（Extend機能があればそのまま継続生成でも可。なければ最終フレームを静止画で書き出す）。
3. クリップ②を15秒で生成（**First Frame＝クリップ①最終フレーム**、キャラ参照＝彼女の三面図・現在側）。
4. ①＋②を編集ソフトで連結して30秒に。つなぎ目は同一フレームなのでカットのまま繋いでよい。
5. 書き出し前に橋・空・彼の立ち位置が①→②で一致していることを確認。
6. BGM想定: 静かなピアノ（クリップ①）→ストリングスが広がる（クリップ②後半）。
