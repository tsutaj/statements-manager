# statements-manager

**English description is under preparation. Sorry for inconvenience.**

競技プログラミングの作問時に使用する、問題文管理を便利にするツール

## What is this?

- Markdown 形式で記述された問題文ファイルを HTML 形式に変換して出力します
- 問題の制約・サンプル管理の一本化
  - 問題制約は、問題設定ファイル内で記述します
  - 定義したものを問題文ファイルで利用することができるほか、generator / validator で利用可能な形で出力することができます
  - **「制約やサンプルを途中で変更したので、問題文・generator / validator の双方をそれぞれ変更する」という作業をする必要がなくなります**
  - **問題文とデータセットでサンプルが一致しているかを確認する必要がなくなります**
- Google Docs 上の問題文 / ローカル上の問題文の両方に対応
  - **Google Docs で管理している問題文** であっても、制約やサンプルを一元的に管理できます

## Screencast

![Peek 2021-03-23 12-17](https://user-images.githubusercontent.com/19629946/112087941-427fd900-8bd2-11eb-8cd5-e76bb73a8e23.gif)

## Quickstart

まずは動作させてみたいという方はこちらをご覧ください。

```bash
# 初回のみ
pip install statements-manager
git clone https://github.com/tsutaj/statements-manager.git

# on 'statements-manager' directory
ss-manager run ./sample

# 実行後は、各問題ディレクトリ (H 問題以外) について
# - ss-out ディレクトリ内に HTML が生成されている
# - tests ディレクトリ内に制約ファイルが生成されている

# "How to use" の 1. で述べられている設定を行うと H 問題に関しても HTML 生成可能です
```

## How to use

以下のようなディレクトリ構成を推奨しています。作問支援ツールである Rime を使用するときのディレクトリ構成と似ています。

```
--- WORKING_DIR/
    |
    |- A/                 (A 問題用のディレクトリ)
    |  |- tests/          (generator / validator / サンプルケース が格納されている)
    |  |- statement/      (問題文や、それに関連する図などが格納されている)
    |  |- problem.toml    (今回のアプリケーションで必要になる設定ファイル)
    |  |- AC_solution/    (解答コードが格納されている)
    |  ...
    |
    |- B/                 (B 問題用のディレクトリ)
    |  |- (同上)
    |  ...
    |
    ...
```

### 1. statements-manager をダウンロードする

以下のコマンドを打って `statements-manager` をダウンロードできます。

```python
pip install statements-manager
```

### 2. 所有している Google アカウントについて、Google Docs API を使用可能にする (Google Docs にある問題文を変換する方のみ)

**注意: Google Docs にある問題文を扱いたい場合は、この操作が必須となります。** 問題文がすべてローカル環境に存在する場合はこの操作は不要です。

- [Google Docs - Quickstart](https://developers.google.com/docs/api/quickstart/python#step_1_turn_on_the) の "Step 1: Turn on the Google Docs API" 内にある "Enable the Google Docs API" を押して、API を使える状態にします
  - 扱いたい Docs ファイルが閲覧できる権限を持っているアカウントで作成しなければならないはずですので、アカウントの選択に注意してください
  - Project name の入力を求められるかもしれません。名前は何でもいいと思います
  - Configure you OAuth client という画面が出たら "Desktop App" を選択してください
- うまくいけば "DOWNLOAD CLIENT CONFIGURATION" というボタンが押せるようなダイアログに行くので、`credentials.json` を任意の場所にダウンロードします (以降の説明では、ダウンロードした場所が `CREDS_PATH` であるとします)
- 以下のコマンドを打って、`credentials.json` をプロジェクトに登録します
  - `WORKING_DIR` とは、"How to use" の冒頭にあるように、各問題ディレクトリの 1 つ上の階層です
  - 登録が終われば、`CREDS_PATH` にある json ファイルは削除しても構いません

```python
ss-manager reg-creds WORKING_DIR CREDS_PATH
```

### 3. 問題ごとに設定ファイル `problem.toml` を作る

問題ディレクトリごとに設定ファイルを作ります。`problem.toml` という名前にして `toml` 形式で記述します。詳しい例は [`sample/A/problem.toml`](https://github.com/tsutaj/statements-manager/blob/master/sample/A/problem.toml) をご覧ください。

**tips (Rime を使用したことがある方向け)**: このファイルは Rime で言うところの `PROBLEM` ファイルに似た位置づけです。`PROBLEM` と同じ階層に保存することを推奨します。

**tips**: パスの記述は絶対パスでも良いですし、`problem.toml` からの相対パスでも構いません。

設定する項目は以下の通りです。

- `mode` (**必須**)
  - `docs` もしくは `local` のいずれか一方を指定します
    - `docs`: 問題文のファイルが Google Docs 内に存在することを想定したモードで実行します
    - `local`: 問題文のファイルがローカルに存在することを想定したモードで実行します
- `id` (**必須**)
  - 問題 ID を指定します
  - アプリケーション実行中の問題判別や、出力される HTML の名前に使用されます
    - 例: id に `A` と指定したならば、出力 HTML は `A.html` という名前になる
- `statement_path` (**必須**)
  - docs mode の場合: 問題文の Document ID を記載します
    - Document ID とは Docs の URL 末尾にある、英数字でできた長い文字列のことです
  - local mode の場合: 問題文が記載されている Markdown ファイルへのパスを記載します
- `lang` (任意)
  - 問題文が書かれている言語を設定します
  - `ja` (日本語) もしくは `en` (英語) のいずれか一方を指定します
  - 何も指定しなかった場合は `en` が設定されているとみなして実行します
- `assets_path` (任意)
  - 問題文に添付する画像などが含まれているディレクトリへのパスを指定します (問題文に図が必要な場合などにご利用ください)
  - `assets_path` 以下に存在する全てのファイル・ディレクトリが `ss-out` ディレクトリ中の **`assets` ディレクトリにコピー** されます
- `sample_path` (任意)
  - サンプルケースが含まれているディレクトリへのパスを指定します
    - 何も指定しなかった場合は、`problem.toml` が存在する階層下の `tests` ディレクトリが設定されます
  - 指定されたディレクトリ内のファイルであって、以下に全て当てはまるものはサンプルケース関連のファイルとみなし、問題文に記載されます
    - 拡張子が `.in` / `.out` / `.md` のいずれかである
    - ファイル名に `sample` が部分文字列として含まれる
- `params_path` (任意)
  - 問題制約となるパラメータの値を、generator や validator で利用できるようにファイルに出力したいときに、パラメータを記載したファイルの出力パスを指定します
    - 例: `path/to/constraints.hpp` としたならば、当該パスにファイルが生成されて出力されます
    - 何も指定しなかった場合は、ファイルが出力されません
  - 指定されたパスの拡張子から言語を推定し、その言語に合ったパラメータファイルを出力するようになっています
    - 注意: 現状は C++ のみ (`.cpp`, `.cc`, `.h`, `.hpp`) 対応しています。今後対応言語は増やす予定です
- `[constraints]` (任意)
  - 問題制約を記述します
  - `[定数名] = [定数]` のように記載します

### 4. 各ファイルを HTML 化する

以下のコマンドで、プロジェクトファイルで定義された各問題を HTML 化できます。出力された HTML は、各問題ディレクトリ内の `ss-out` ディレクトリに格納されます。

```bash
ss-manager run WORKING_DIR
```

## Links

- [Rime](https://github.com/icpc-jag/rime)
  - 作問するならまずこれを使うべきでしょう。これのプラグインとして開発しようか迷いましたが、Rime v3 でプラグインが廃止される (かもしれない) らしいので、独立に作ることにしています
  - statements-manager がもっと発展したら merge することも考えています
- [library-checker-problems](https://github.com/yosupo06/library-checker-problems)
  - 当アプリケーションの機能は、これの影響を強く受けています
  - library-cheker-problems の作問機能で出来ることを網羅しつつ、Rime と親和性が良い設計にし、さらに作問時に便利な Google Docs とも連携させたいというモチベーションがあり、このアプリケーションが作られました
