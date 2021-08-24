# statements-manager

![PyPI](https://img.shields.io/pypi/v/statements-manager) [![Python Versions](https://img.shields.io/pypi/pyversions/statements-manager.svg)](https://pypi.org/project/statements-manager/)

**English description is under preparation. Sorry for inconvenience.**

競技プログラミングの作問時に使用する、問題文管理を便利にするツール

## What is this?

- Markdown 形式で記述された「制約やサンプルの情報を外部に委ねた」問題文ファイルを、 HTML / PDF / Markdown 形式に変換して出力します
  - 制約やサンプルは問題文に直接的には書きません。詳しくは後述
- **特長**: 問題の制約・サンプル管理の一本化
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

作業ディレクトリ `WORKING_DIR` に対して、以下で説明する credentials というものを登録します。

- [Google Docs - Quickstart](https://developers.google.com/docs/api/quickstart/python) の手順通りに進め、API を使える状態にします。リンク先のサンプルを実行できるかどうかで動作確認が可能です。
  - 扱いたい Docs ファイルが閲覧できる権限を持っているアカウントで作成しなければならないはずですので、アカウントの選択に注意してください
- [Google Cloud Platform](https://console.cloud.google.com/) にアクセスし、「API とサービス」→「認証情報」に進みます

![Screenshot from 2021-08-19 23-16-51](https://user-images.githubusercontent.com/19629946/130088968-92409236-ef85-49c5-a244-33e4380308ea.png)

- 以下の画面で OAuth クライアントをダウンロードします。JSON ファイルを任意の場所にダウンロードしてください
  - 以降の説明では、ダウンロードした場所が `CREDS_PATH` であるとします

![Screenshot from 2021-08-19 23-24-51](https://user-images.githubusercontent.com/19629946/130088491-761cf3bb-6b8c-4bb4-9396-91e98be6ab8a.png)

![Screenshot from 2021-08-19 23-25-11](https://user-images.githubusercontent.com/19629946/130088501-5e1208df-445a-4797-be31-60a77f04c91d.png)
- 以下のコマンドを打って、JSON ファイルを作業ディレクトリに登録します
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
  - ID は、実行時に操作対象となる設定ファイルそれぞれで **一意でなければなりません**。例えば、`ID = "A"` となる設定ファイルが複数存在してはいけません
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
  - `assets_path` 以下に存在する全てのファイル・ディレクトリが `ss-out` ディレクトリ中の **`assets` ディレクトリにコピー** されます。画像などのリンクを張る際は、この仕様を念頭に置いて指定してください。
- `sample_path` (任意)
  - サンプルケースが含まれているディレクトリへのパスを指定します
    - 何も指定しなかった場合は、`problem.toml` が存在する階層下の `tests` ディレクトリが設定されます
  - 指定されたディレクトリ内のファイルであって、以下に全て当てはまるものはサンプルケース関連のファイルとみなし、問題文に記載されます
    - 拡張子が `.in` / `.out` / `.md` のいずれかである
      - `.in` ファイル: 入力例を表すファイル
      - `.out` ファイル: 出力例を表すファイル
      - `.md` ファイル: 入出力例に関する説明 (`sample` ディレクトリの A 問題参照)、またはインタラクティブの入出力例を表すファイル (`sample` ディレクトリの I 問題参照)
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

### 4. 問題文を用意する

**書き方を直感的に把握するために、`sample` ディレクトリにある問題文ファイルを参考にすることをお勧めします**

- ローカル・Google Docs のいずれにおいても、問題文は Markdown 形式で記述してください。
- 問題文中では以下の記法が使用できます。いずれの記法に関しても、出力ファイル上では何らかのパラメータ・ファイルに置換されます。
  - `{@constraints.<CONSTRAINT_NAME>}`
    - 問題制約のパラメータに置換されます
    - パラメータ名 `<CONSTRAINT_NAME>` は `problem.toml` の `[constraints]` で記述されていた定数名である必要があります
  - `{@samples.s<NUMBER>}`
    - サンプルに関連するファイル群のうち、`<NUMBER>` 番目 (leading-zero は許容しない) のものに置換されます
    - サンプルの名前は拡張子を無視した状態で集合として管理されており、辞書順で小さいものから 1, 2, 3, ... と番号付けられています
      - 例えばサンプルに関連するファイルが `00_sample_00.in`, `00_sample_00.out`, `00_sample_00.md`, `00_sample_01.in`, `00_sample_01.out` の 5 つであった場合、`00_sample_00` が 1 番目・`00_sample_01` が 2 番目となります
  - `{@samples.all}`
    - `problem.toml` の `sample_path` で指定されたディレクトリ以下にある、サンプルに関連するすべてのファイル群に置換されます
    - サンプルの挿入順番は、上述した「サンプルの番号付け」で得られた順番通りに行われます

### 5. ファイルを HTML / PDF / Markdown 化する

以下のコマンドで、プロジェクトファイルで定義された各問題を HTML 化できます。出力された HTML は、各問題ディレクトリ内の `ss-out` ディレクトリに格納されます。

```bash
ss-manager run [-o OUTPUT] WORKING_DIR
```

- `WORKING_DIR`: 各問題ディレクトリの 1 つ上の階層
- `OUTPUT`: 以下のうちいずれか 1 つを指定します。指定しなかった場合は `html` が指定されているものとして扱われます。
  - `html` (default): HTML を出力
  - `md`: Markdown を出力
  - `pdf`: PDF を出力
    - `-o` オプションで `pdf` を指定した場合のみ、セット全体の PDF も出力するようになっています。`WORKING_DIR` 直下に `problemset.pdf` というファイルが出力されます。

## Links

- [Rime](https://github.com/icpc-jag/rime)
  - 作問するならまずこれを使うべきでしょう。これのプラグインとして開発しようか迷いましたが、Rime v3 でプラグインが廃止される (かもしれない) らしいので、独立に作ることにしています
  - statements-manager がもっと発展したら merge することも考えています
- [library-checker-problems](https://github.com/yosupo06/library-checker-problems)
  - 当アプリケーションの機能は、これの影響を強く受けています
  - library-cheker-problems の作問機能で出来ることを網羅しつつ、Rime と親和性が良い設計にし、さらに作問時に便利な Google Docs とも連携させたいというモチベーションがあり、このアプリケーションが作られました


## For Contributors

- 本リポジトリへの Issue / PR など、なんでも歓迎です。詳細は [`CONTRIBUTING`](./CONTRIBUTING.md) をご覧ください。