# statements-manager

競技プログラミングの作問時に使用する、問題文管理を便利にするツール (仮)

## Getting Started

**!! 実装途中なので、操作・設定方法は今後変更される可能性があります !!**

### Quickstart (とにかく動作させたい人向け)

```bash
# 初回のみ
pip -r requirements.txt

# 実行後に output ディレクトリの中身を確認すること
python3 statements_manager.py -p config/local_sample.toml run
```

### 1. 所有している Google アカウントについて、Google Docs API を使用可能にする (Google Docs にある問題文を変換する方のみ)

- [Google Docs - Quickstart](https://developers.google.com/docs/api/quickstart/python#step_1_turn_on_the) の "Step 1: Turn on the Google Docs API" 内にある "Enable the Google Docs API" を押して、API を使える状態にします
  - project name は何でもいいと思います
  - 扱いたい Docs ファイルが閲覧できる権限を持っているアカウントで作成しなければならないはずなので注意してください
- うまくいけば "DOWNLOAD CLIENT CONFIGURATION" を押すようなダイアログに行くので、`credentials.json` を任意の場所にダウンロードします (このファイルはプロジェクトファイルの `docs.credentials_src` に、絶対パスまたはスクリプト実行元からの相対パスで設定する必要があります)
  - 一度認可に成功すると、`token.pickle` というファイルが生成されます。これをプロジェクトファイルに指定することで、毎回認可することなく高速に実行できます。

### 2. 必要なライブラリをダウンロードする

`pip -r requirements.txt` で、スクリプトの動作に必要なライブラリをダウンロードできます。(環境を汚されたくない人は `venv` とかの仮想環境を適宜使ってください)

### 3. プロジェクトファイルを作る

作問プロジェクトファイルを作ります (開発者は、1 ファイルで 1 問題セットを扱い、各問題ファイルは「全てローカル」および「全て Google Docs」のいずれかで管理されていることを仮定しているので、それを念頭に置いてください)

プロジェクトファイルの雛形は以下を実行することで生成されます。

```bash
python3 statements_manager.py -p [path_to_project.toml] create
```

あとは、問題セットの都合に合わせてプロジェクトファイルを編集してください。プロジェクトファイルの書き方についてはそのうちリファレンスを書きます (TODO)。なお、[Google Docs ファイルに対するサンプル](https://github.com/tsutaj/statements-manager/blob/master/config/docs_sample.toml) や [ローカルファイルに対するサンプル](https://github.com/tsutaj/statements-manager/blob/master/config/local_sample.toml) が存在するので、これを参考にしながら書くとだいたいのことはできるはずです・・・

### 4. 各ファイルを HTML 化する

以下のコマンドで、プロジェクトファイルで定義された各問題を HTML 化できます。出力された HTML は `output` ディレクトリ内に格納されます。

- HTML 化される対象のプロジェクト名と同名のディレクトリが `output` 直下に存在する場合は実行できません (上書き防止)。その場合はディレクトリを適宜削除してください。

```bash
python3 statements_manager.py -p [path_to_project.toml] run
```

## Future Development

- 構想: https://github.com/tsutaj/googledocs2md/issues/1
- TODO: https://github.com/tsutaj/statements-manager/issues/3

## Links

- [library-checker-problems](https://github.com/yosupo06/library-checker-problems)
  - 当スクリプトでできる機能については、このリポジトリの影響を強く受けています。いまのところ「ここでできることを自由度を高めつつ一般化したい」and「作問時に便利な Google Docs と連携させたい」というモチベーションがあります。
- [Rime](https://github.com/icpc-jag/rime)
  - 作問するならまずこれを使うべきでしょう。これのプラグインとして開発しようか一瞬迷いましたが、Rime v3 でプラグインが廃止される (かもしれない) らしいので、独立に作ることにしちゃいました。
