# ガラスの鯨と夏の屋上
*The Glass Whale and the Summer Rooftop*

Seedance 2.0 用ショートフィルム企画(15秒 / アニメ調 / X公開向け)

---

## ログライン

夏の終わりの放課後。ひとり屋上で空を見上げる少女の前に、体がガラスでできた巨大な鯨が現れる。誰にも信じてもらえない、彼女だけの5時16分の奇跡。

## 物語(プロット)

**場所:** 日本の地方都市の高校・屋上。遠くに海と入道雲が見える。
**時間:** 8月末、夕方5時過ぎ。蝉の声が少しだけ弱くなった頃。

**起:** 補習を終えた高校2年の少女・**ナギ**(制服のセーラー服、少し癖のある黒髪、スクールバッグを足元に置いている)は、ひとり屋上のフェンス際に立ち、オレンジ色に染まりはじめた空をぼんやり見ている。風が前髪を揺らす。どこか物憂げな横顔——夏が終わってしまうことへの、言葉にならない寂しさ。

**承:** ふいに、蝉の声が止む。空気が変わる。入道雲の間から、**鯨の歌**のような低く澄んだ音が響く。ナギが顔を上げると、雲を割って**全身が透明なガラスでできた巨大な鯨**がゆっくりと現れる。体長は校舎よりも大きい。ゆったりと尾びれを振り、空を泳ぐ。

**転:** 鯨の透明な巨体を夕日が貫き、光が屈折して**虹色の光の帯**が校庭と屋上に降り注ぐ。ナギの髪と制服のスカーフが風に舞い、瞳に鯨と夕焼けが映り込む。彼女は驚きから、次第に泣き笑いのような表情に変わり、フェンスに駆け寄って手を伸ばす。

**結:** 鯨はナギのすぐ頭上を、雲のように静かに通り過ぎていく。ガラスの腹に、小さく手を伸ばす彼女自身の姿が映る。鯨は一度だけ大きく歌い、夕焼けの奥へと溶けるように消えていく。屋上に残るのは、風と、少しだけ強くなった蝉の声。ナギの伸ばした手が、ゆっくりと胸の前に降りる——夏の終わりを、受け取ったように。

**テーマ:** 「終わっていく季節への惜別と、それでも前を向く一瞬」。誰にも証明できない奇跡をひとりで受け取る、というエモーションが引用RTで語られることを狙う。

---

## 15秒 絵コンテ / ショットリスト

Seedance 2.0 は1生成内のマルチショットに対応。以下の4カットを1本のプロンプトで指示する。

| カット | 時間 | 内容 | カメラ |
|---|---|---|---|
| 1 | 0.0–3.5s | 夕暮れの屋上。フェンス際に立つナギの後ろ姿〜横顔。風に髪が揺れる。蝉の声、遠い部活の音 | 背後からのミディアム、ゆっくり右へ回り込み |
| 2 | 3.5–7.0s | 蝉の声が止み、鯨の歌。雲を割ってガラスの鯨が現れる。ナギの見上げる顔(瞳のハイライト) | ローアングルの空ショット → ナギの顔アップに切り返し |
| 3 | 7.0–11.5s | 鯨の巨体を夕日が貫き、虹色の光が屋上に降る。ナギがフェンスに駆け寄り手を伸ばす | 光の中の広角。逆光でレンズフレア |
| 4 | 11.5–15.0s | 頭上を通過する鯨の腹にナギが映る。鯨がひと声歌い、夕焼けの奥へ消える。ナギの手が胸に降りる | 真下からの仰角 → 引きのラストカット |

**ループ設計:** ラストの空の色をカット1の空に近づけ、リピート再生に耐える構成にする。

## キャラクターデザイン — ナギ(凪)

- 高校2年生、16歳。肩下までの黒髪(毛先に少し癖)、風で揺れるおくれ毛
- 夏服セーラー服(白基調・紺襟・赤系スカーフ)、スカートは膝丈
- 感情表現:物憂げ → 驚き → 泣き笑い → 静かな決意、の4段階
- 瞳のハイライトに夕焼けと鯨を映すのが最重要ポイント

## 美術・光・色設計

- スタイル:劇場アニメクオリティ。新海誠的な光表現(強い逆光、レンズフレア、密度の高い入道雲、彩度の高い夕焼けグラデーション)
- パレット:オレンジ〜マゼンタの夕焼け / 紺に沈む校舎の影 / 鯨のガラスは無色透明+プリズムの虹色
- ガラスの鯨:内部で夕日が屈折・分光する。輪郭は夕焼けを歪めて透かす。実在感のための細かい気泡と厚みの表現

## 音響設計(Seedance ネイティブ音声)

1. 蝉の声+遠い環境音(0–3.5s)
2. 無音の一拍 → 低く澄んだ鯨の歌(3.5s〜)
3. 壮大で切ないアンビエント(ストリングス+ピアノ)が立ち上がる(7s〜)
4. 鯨のひと声の残響と風、戻ってくる蝉の声で締め(12s〜)

## Seedance 2.0 生成パラメータ

| パラメータ | 値 |
|---|---|
| model | `seedance_2_0` |
| duration | 15 |
| resolution | 1080p(完成後 4K アップスケール) |
| mode | std |
| bitrate_mode | high |
| aspect_ratio | 16:9(X のタイムライン映え優先。縦版は 9:16 で別生成) |
| genre | drama |
| generate_audio | true |
| start_image | 下記プロンプトで生成したキーフレーム画像を使用 |

---

## イメージ画像用プロンプト(Codex / 画像生成AI にそのまま貼り付け可)

### 1. キービジュアル(開始フレーム兼用・16:9)

```
Cinematic anime key visual, Makoto Shinkai style, ultra-detailed theatrical anime quality.
A Japanese high school girl (16 years old, shoulder-length black hair swaying in the wind,
white summer sailor uniform with navy collar and red scarf) stands alone at the fence of a
school rooftop at golden hour, seen from behind at a slight side angle. Above the towering
cumulonimbus clouds, an enormous whale made entirely of transparent glass swims through the
sunset sky. The evening sun refracts through its crystal body, casting prismatic rainbow
light across the rooftop. Distant sea on the horizon, saturated orange-to-magenta sunset
gradient, dense detailed clouds, strong backlight with lens flare, volumetric light rays,
melancholic end-of-summer atmosphere. 16:9, masterpiece, extremely detailed sky.
```

### 2. ナギ 表情アップ(カット2用・16:9)

```
Cinematic anime close-up, Makoto Shinkai style. A 16-year-old Japanese girl with
shoulder-length black hair looks up in awe, sunset and a giant transparent glass whale
reflected as highlights in her wide eyes. Wind lifts her hair and the red scarf of her white
sailor uniform. Warm golden-hour rim light on her cheek, soft depth of field, emotional,
tears about to form but smiling. 16:9, theatrical anime quality.
```

### 3. ガラスの鯨 単体設定画(1:1)

```
Concept art of a colossal whale made entirely of clear glass, translucent crystal body with
subtle internal air bubbles and thickness variations, sunset light refracting into prismatic
rainbows inside its body, swimming through cumulonimbus clouds in a golden-hour sky, anime
film background art style, highly detailed, awe-inspiring scale. 1:1.
```

### 日本語版(そのまま日本語対応モデルに渡す場合)

```
劇場アニメ品質・新海誠風のキービジュアル。夕暮れの高校の屋上、フェンス際に立つセーラー服の
少女(16歳、肩下の黒髪、赤いスカーフ)を斜め後ろから。入道雲の上を、全身が透明なガラスで
できた巨大な鯨が泳ぐ。夕日が鯨の体で屈折し、虹色の光が屋上に降り注ぐ。水平線に海、オレンジ
からマゼンタへの夕焼けグラデーション、強い逆光とレンズフレア、夏の終わりの切ない空気。16:9。
```

---

## 制作フロー

1. 上記プロンプトでキービジュアル(開始フレーム)を画像生成 → 構図・キャラデザを確定
2. 確定画像を `start_image` + `image_references` にして Seedance 2.0 で 15 秒動画を生成
3. bytedance アップスケーラで 4K 化(preset: `aigc`)
4. X 投稿:16:9 本編+必要なら 9:16 縦版を再生成
