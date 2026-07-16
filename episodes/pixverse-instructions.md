# PixVerse制作指示書「にほんへいこう！〜おとうさんに会いに〜」

480P・15秒（8秒×2クリップ構成）・BGMなし

## 前提

PixVerseの1クリップは最大8秒のため、15秒は2クリップに分割し、
**クリップ1の最終フレームをクリップ2の開始画像（First Frame）に使って**つなげます。
（もし480Pの選択肢が無いプランの場合は、一番近い解像度（540Pなど）を選択）

## 使用素材（ダウンロードして使用）

| 素材 | URL |
|---|---|
| 開始フレーム（カット1） | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260716_072411_5b745def-fee7-407c-9c73-792804aecde5.png |
| ぺんぎんちゃん三面図 | episodes/assets/penguin-chan-sheet.png |
| お父さん三面図（案1） | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260716_065849_2938df64-cee0-46c1-a691-d7c0400a1ab1.png |
| お母さん三面図 | episodes/assets/okaasan-sheet.png |
| さかなくん三面図 | episodes/assets/sakana-kun-sheet.png |
| 9コマ絵コンテv2 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260716_100827_d507b2c6-4911-4f64-b5c4-ac5e9d099bdf.png |
| 背景：空港ロビー | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260716_115031_4839f748-c08d-4c02-89be-f8b68646e219.png |
| 背景：富士山上空 | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260716_115042_533fb0b1-c5c8-4533-8d2c-803b52434396.png |
| 背景：到着ゲート | https://d8j0ntlcm91z4.cloudfront.net/user_38k3HpgLGtIPunR7RsTJbhIIlkv/hf_20260716_115045_2b3bc336-3491-4016-9e42-e880751553d9.png |

## クリップ1（8秒｜絵コンテ①〜④）

- モード：Image to Video
- First Frame：開始フレーム（カット1）
- キャラクター参照が使える場合：ぺんぎんちゃん・お母さん・お父さんの三面図を登録
- 解像度：480P／アスペクト比：16:9／8秒
- 音声：効果音ON可・**BGM/音楽はOFF**

プロンプト（日本語）：

> やわらかいセル塗りのアニメ。空港の出発ロビーで、ペンギンの着ぐるみの女の子が自分より大きいスーツケースを引いて元気に歩く（横移動）。後ろに茶髪のお母さん、バッグから青いおさかなのぬいぐるみ。カットが変わり、富士山上空を飛ぶ白い旅客機のロング、窓に女の子の顔がぺたっ。カットが変わり、到着ゲートの人混みの向こうで、黒髪でグレーのスウェットに聴診器をかけた優しいお父さんが手を振る。最後にお母さんの顔アップ、目が潤み涙が一粒こぼれる。BGMなし。

プロンプト（英語版・精度が高い場合はこちら）：

> Soft cel-shaded anime. In an airport departure lobby, a small girl in a penguin kigurumi cheerfully pulls a big suitcase (lateral tracking), her brown-haired mother behind with a blue fish plush in her bag. Cut to a wide shot of a white airplane over Mt. Fuji, the girl's face pressed to a window. Cut to the arrival gate: across the crowd a gentle black-haired father in a gray sweatshirt with a stethoscope waves. Final close-up: the mother's eyes glisten and a single tear rolls down. No music, no BGM.

## クリップ2（8秒｜絵コンテ⑤〜⑨）

- モード：Image to Video
- First Frame：**クリップ1の最終フレーム**（PixVerseのExtend機能または最終フレームを書き出して指定）
- 解像度・比率・音声設定はクリップ1と同じ

プロンプト（日本語）：

> 同じアニメ。涙目のお母さんが両手を広げてお父さんへ駆け出す。その広げた腕の下を、ペンギンの着ぐるみの女の子が弾丸のようにすり抜けて先にお父さんの胸へダイブ（スピード線）。お父さんはよろけながらキャッチ、聴診器が跳ねる。お母さんは両手を広げたまま固まり、涙をぬぐって苦笑いで肩をすくめる。バッグの青いおさかなも真似してすくめる。最後は家族全員であたたかくハグ。BGMなし。

プロンプト（英語版）：

> Same anime. The teary mother spreads both arms and runs toward the father. Under her outstretched arms, the penguin-kigurumi girl rockets past and dives into the father's chest first (speed lines). He staggers and catches her, stethoscope bouncing. The mother freezes with arms spread, then wipes her tear and shrugs with a wry smile; the blue fish plush in her bag mimics the shrug. The whole family joins in a warm group hug. No music, no BGM.

## 仕上げ

1. クリップ1（8秒）＋クリップ2（8秒）を編集ソフトで連結し、15秒にトリミング（クリップ2の末尾を1秒詰める）
2. 音楽・BGMはこの後に後入れ
3. セリフを載せる場合の台本：
   - ① ぺんぎんちゃん「にっぽん、しゅっぱーつ！」
   - ③ お父さん「おーい！」
   - ④ お母さん「あなた……やっと会えた……」
   - ⑤ お母さん「あなたー！」
   - ⑥ ぺんぎんちゃん「さみしかったよー！！」
   - ⑦ お父さん「おっと！元気そうだね」
   - ⑨ お父さん「おかえり」
