# ここに Mixamo の FBX ファイルを入れてください

再生したい順番に番号を付けて命名します:

```
01_running.fbx      ← 最初の1本だけ「With Skin」でダウンロード(体つき)
02_vault.fbx        ← 2本目以降は「Without Skin」
03_running.fbx
04_running_jump.fbx
05_roll.fbx
...
```

- Mixamo のダウンロード設定: **FBX Binary / 30fps / In Place はオフ**
- ファイル名に `vault` / `slide` / `climb` が含まれると障害物ブロックが自動配置されます
- 同じモーションを繰り返すときはファイルをコピーして別番号を付けるだけ
- 30秒(900フレーム)に届くまでクリップを追加してください

ファイルを置いたら `parkour/` フォルダで:

```bash
blender -b -P build_parkour.py -- --anims ./anims --out ./out --render
```

※ Mixamo のファイルを用意する前に試したい場合は、ダミークリップを生成できます:

```bash
blender -b -P make_test_anims.py -- --out ./anims
```
