# statements-manager

**English description is under preparation. Sorry for inconvenience.**

競技プログラミングの作問時に使用する、問題文管理を便利にするツール

## Getting Started

### Quickstart (とにかく動作させたい人向け)

```bash
# 初回のみ
pip install statements-manager
git clone https://github.com/tsutaj/statements-manager.git

# on 'statements-manager' directory
# 実行後に output ディレクトリの中身を確認すること
ss-manager run ./sample
```

### 1. 所有している Google アカウントについて、Google Docs API を使用可能にする (Google Docs にある問題文を変換する方のみ)

- [Google Docs - Quickstart](https://developers.google.com/docs/api/quickstart/python#step_1_turn_on_the) の "Step 1: Turn on the Google Docs API" 内にある "Enable the Google Docs API" を押して、API を使える状態にします
  - project name は何でもいいと思います
  - 扱いたい Docs ファイルが閲覧できる権限を持っているアカウントで作成しなければならないはずなので注意してください
- うまくいけば "DOWNLOAD CLIENT CONFIGURATION" を押すようなダイアログに行くので、`credentials.json` を任意の場所にダウンロードします
  - 一度認可に成功すると、`token.pickle` というファイルが生成されます。これをプロジェクトファイルに指定することで、毎回認可することなく高速に実行できます。

### 2. statements-manager をダウンロードする

`pip install statements-manager` で、`statements-manager` をダウンロードできます。(環境を汚されたくない人は `venv` とかの仮想環境を適宜使ってください)

### 3. プロジェクトファイル `project.toml` を作る

作問プロジェクトファイルを作ります。プロジェクトファイルは `project.toml` という名前にして `toml` 形式で記述します。設定する項目は以下の通りです。

**tips (Rime を使用したことがある方向け)**: このファイルは Rime で言うところの `PROJECT` ファイルに似た位置づけです。`PROJECT` と同じ階層に保存することを推奨します。

**tips**: パスの記述は絶対パスでも良いですし、`project.toml` からの相対パスでも構いません。

- `docs.creds_path` (任意)
  - 手順 1 で取得した credentials へのパスを記述します
- `docs.token_path` (任意)
  - 手順 1 で取得した token へのパスを記述します
- `style.template_path` (任意)
  - 出力 HTML のテンプレートとなるファイルへのパスを記述します
  - テンプレートでは、`<body>` タグ内に `{@task.statements}` と書いてください。詳しい例は `sample/assets/template.html` をご覧ください。
- `style.copied_files` (任意)
  - CSS / JS ファイルなど、HTML 生成に必要なものの一覧をリスト形式で記述します
  - ここに指定されたファイルは、出力 HTML と同一の階層にコピーされます
    - テンプレートで相対パスを指定するときは、この仕様に注意してください

### 4. 問題ごとに設定ファイル `problem.toml` を作る

問題ディレクトリごとに設定ファイルを作ります。`problem.toml` という名前にして `toml` 形式で記述します。設定する項目は以下の通りです。

**tips (Rime を使用したことがある方向け)**: このファイルは Rime で言うところの `PROBLEM` ファイルに似た位置づけです。`PROBLEM` と同じ階層に保存することを推奨します。

**tips**: パスの記述は絶対パスでも良いですし、`problem.toml` からの相対パスでも構いません。

- `mode` (**必須**)
  - `docs` もしくは `local` のいずれか一方を指定します
    - `docs`: 問題文のファイルが Google Docs 内に存在することを想定したモードで実行します
    - `local`: 問題分のファイルがローカルに存在することを想定したモードで実行します
- `id` (**必須**)
  - 問題 ID を指定します
  - スクリプト実行中の問題判別や、出力される HTML の名前に使用されます
    - 例: id に `A` と指定したならば、出力 HTML は `A.html` という名前になる
- `statement_path` (**必須**)
  - docs mode の場合: 問題文の Document ID を記載する
    - Document ID とは Docs の URL にある、ランダムのような文字列のことです
  - local mode の場合: 問題文が記載されている Markdown ファイルへのパスを記載する
- `params_path` (任意)
  - 問題制約となるパラメータの値を、generator や validator で利用できるようにファイルに出力したいときに、パラメータを記載したファイルの出力パスを指定します
    - 例: `path/to/constraints.hpp` としたならば、当該パスにファイルが生成されて出力されます
  - 指定されたパスの拡張子から言語を推定し、その言語に合ったパラメータファイルを出力するようになっています
    - 注意: 現状は C++ のみ (`.cpp`, `.cc`, `.h`, `.hpp`) 対応しています。今後対応言語は増やす予定です。
- `[constraints]` (任意)
  - 問題制約を記述します
  - `[定数名] = [定数]` のように記載します。詳しい例は `sample/A/problem.toml` をご覧ください。

### 5. 各ファイルを HTML 化する

以下のコマンドで、プロジェクトファイルで定義された各問題を HTML 化できます。出力された HTML は、各問題ディレクトリ内の `ss-out` ディレクトリに格納されます。

```bash
ss-manager run [path_to_project.toml]
```

## Links

- [library-checker-problems](https://github.com/yosupo06/library-checker-problems)
  - 当スクリプトでできる機能については、このリポジトリの影響を強く受けています。いまのところ「ここでできることを自由度を高めつつ一般化したい」and「作問時に便利な Google Docs と連携させたい」というモチベーションがあります。
- [Rime](https://github.com/icpc-jag/rime)
  - 作問するならまずこれを使うべきでしょう。これのプラグインとして開発しようか一瞬迷いましたが、Rime v3 でプラグインが廃止される (かもしれない) らしいので、独立に作ることにしちゃいました
  - ここの実装がいい感じになったら merge することも考えています
