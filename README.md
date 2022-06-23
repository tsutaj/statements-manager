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

![screencast](https://user-images.githubusercontent.com/19629946/131149286-39111b9b-9719-4693-98f9-88ed8caea34d.gif)

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

問題ディレクトリごとに設定ファイルを作ります。`problem.toml` という名前にして `toml` 形式で記述します。詳しい例は [`sample/A/problem.toml`](https://github.com/tsutaj/statements-manager/blob/master/sample/A/problem.toml) などの、`sample` ディレクトリにある設定ファイルをご覧ください。

**tips (Rime を使用したことがある方向け)**: このファイルは Rime で言うところの `PROBLEM` ファイルに似た位置づけです。`PROBLEM` と同じ階層に保存することを推奨します。

**tips**: パスの記述は絶対パスでも良いですし、`problem.toml` からの相対パスでも構いません。

設定する項目は以下の通りです。

- `id` (**必須**)
  - 問題 ID を指定します
  - アプリケーション実行中の問題判別や、出力される HTML の名前に使用されます
  - ID は、実行時に操作対象となる設定ファイルそれぞれで **一意でなければなりません**。例えば、`id = "A"` となる設定ファイルが複数存在してはいけません
- `assets_path` (任意)
  - 問題文に添付する画像などが含まれているディレクトリへのパスを指定します (問題文に図が必要な場合などにご利用ください)
  - `assets_path` 以下に存在する全てのファイル・ディレクトリが `ss-out` ディレクトリ中の **`assets` ディレクトリにコピー** されます。画像などのリンクを張る際は、この仕様を念頭に置いて指定してください。
- `sample_path` (任意)
  - サンプルケースが含まれているディレクトリへのパスを指定します
    - 何も指定しなかった場合は、`problem.toml` が存在する階層下の `tests` ディレクトリが設定されます
  - 指定されたディレクトリ内のファイルであって、以下に全て当てはまるものはサンプルケース関連のファイルとみなし、問題文に記載されます
    - 拡張子が `.in` / `.out` / `.diff` / `.md` のいずれかである
      - `.in` ファイル: 入力例を表すファイル
      - `.out` / `.diff` ファイル: 出力例を表すファイル
      - `.md` ファイル: インタラクティブの入出力例を表すファイル (`sample` ディレクトリの I 問題参照)
      - `[言語名]/*.md` ファイル: 入出力例に関する説明 (`sample` ディレクトリの A 問題参照)
        - 例: 日本語で `00_sample_00` に関する説明をしたいならば、`[sample_path]/ja/00_sample_00.md` というファイルを用意します
        - **注意: v1.5.0 より、インタラクティブの入出力例のために用意する Markdown ファイルと、入出力例に関する説明のために用意する Markdown ファイルは、想定する格納場所が明確に異なります**
    - ファイル名に `sample` が部分文字列として含まれる
- `ignore_samples` (任意)
  - `sample_path` で指定されたディレクトリにある、サンプルケースとして認識されるファイル名のうち、問題文に反映してほしくないものをリスト形式で指定します。拡張子は含めてはなりません
  - 例えば `00_sample_00` および `00_sample_hoge` を問題文に含めてほしくない場合、`ignore_samples = ["00_sample_00", "00_sample_hoge"]` のように設定します
  - [Unix のシェル形式のワイルドカード](https://docs.python.org/ja/3/library/fnmatch.html) に対応しています
  - 何も指定されなかった場合、見つかった全てのサンプルケースが問題文に反映されます
- `params_path` (任意)

  - 問題制約となるパラメータの値を、generator や validator で利用できるようにファイルに出力したいときに、パラメータを記載したファイルの出力パスを指定します
    - 例: `path/to/constraints.hpp` としたならば、当該パスにファイルが生成されて出力されます
    - 何も指定しなかった場合は、ファイルが出力されません
  - 指定されたパスの拡張子から言語を推定し、その言語に合ったパラメータファイルを出力するようになっています
    - 注意: 現状は C++ のみ (`.cpp`, `.cc`, `.h`, `.hpp`) 対応しています。今後対応言語は増やす予定です

- `[[statements]]` (**必須**)
  - 用意する問題文ファイルそれぞれについて設定します。設定方法の例は `sample` ディレクトリにある A 問題・C 問題などを参照してください
    - A 問題では、英語・日本語の両方で問題文を作成する例を示しています
    - C 問題では、英語・日本語の両方で問題文を作成することに加えて、制約のみが異なる問題を作成する例も示しています
  - 各問題文ファイルについて以下を設定します
    - `path` (**必須**)
      - ローカルに問題文が存在する場合: 問題文が記載されているファイル名を指定します
      - Google Docs に問題文が存在する場合: Google Docs の ID か、もしくは Google Docs のファイルの URL を指定します。設定方法の例は `sample` の H 問題を参照してください。
    - `lang` (任意)
      - 問題文が書かれている言語を設定します
      - `ja` (日本語) もしくは `en` (英語) のいずれか一方を指定します
      - 何も指定しなかった場合は `en` が設定されているとみなして実行します
    - `mode` (任意)
      - `docs` または `local` のどちらかを指定します。問題文ファイルが存在する場所に応じて設定ください
      - 何も設定しなかった場合はモードが自動で認識されますので、通常は `mode` を設定する必要はありません
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

### 5. テンプレート設定ファイルを用意する (任意)

**書き方を直感的に把握するために、`sample` ディレクトリにある `problemset.toml` を参考にすることをお勧めします**

必要であれば、HTML・PDF に適用されるテンプレートを指定するためのファイル `problemset.toml` を作成します。このファイルが無い場合は、デフォルトのテンプレートが使用されます。

- `[template]`
  - `template_path`
    - HTML および PDF 出力で使用されるテンプレート HTML へのパスを指定します (指定されていない場合、デフォルトのテンプレートが適用されます)
    - テンプレートでは、問題文本文に相当する部分に `{@problem.statement}` 文を記述する必要があります。詳細は `sample/templates/default.html` などをご覧ください
  - `preprocess_path`
    - Markdown ファイルに関して前処理を行う **Python スクリプト** へのパスを指定します。Markdown が HTML 形式にレンダリングされる前に適用したい処理を記述してください (指定されていない場合、前処理は行われません)
    - Markdown ファイルの中身は標準入力で与えられ、前処理の結果は標準出力で返す必要があります。詳細は `sample/templates/icpc_domestic/preprocess.py` をご覧ください
  - `postprocess_path`
    - HTML ファイルに関して後処理を行う **Python スクリプト** へのパスを指定します。HTML 形式にレンダリングされた後に適用したい処理を記述してください (指定されていない場合、後処理は行われません)
    - HTML ファイルの中身は標準入力で与えられ、後処理の結果は標準出力で返す必要があります。詳細は `sample/templates/icpc_domestic/postprocess.py` をご覧ください

### 6. ファイルを HTML / PDF / Markdown 化する

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

## 運用例 (リポジトリにある問題文を半自動で更新する試み)

GitHub Actions などの CI サービスと併用することで、リポジトリに変更が加えられたときに問題文に関する成果物の差分を `push` し、常にリポジトリ内の問題文を最新の状態に保つことが可能です。

設定の一例を以下に示します。これは `master` に `push` された際に `ss-manager run` を実行し、差分を自動で `push` するものです。以下の実装を、リポジトリに `.github/workflows/statements-manager.yml` として保存すると動作するはずです。

```yaml
# statements-manager を動かし、変更点があれば commit & push する
name: update-statements

on:
  push:
    branches: [master]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python 3
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install statements-manager
      - name: Run statements-manager
        run: |
          ss-manager run ./
      - name: Commit files
        run: |
          git add --all
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git commit -m "[ci skip] [bot] Updating to ${{ github.sha }}."
      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          branch: ${{ github.ref }}
```

## Links

- [Rime](https://github.com/icpc-jag/rime)
  - 作問するならまずこれを使うべきでしょう。これのプラグインとして開発しようか迷いましたが、Rime v3 でプラグインが廃止される (かもしれない) らしいので、独立に作ることにしています
  - statements-manager がもっと発展したら merge することも考えています
- [library-checker-problems](https://github.com/yosupo06/library-checker-problems)
  - 当アプリケーションの機能は、これの影響を強く受けています
  - library-cheker-problems の作問機能で出来ることを網羅しつつ、Rime と親和性が良い設計にし、さらに作問時に便利な Google Docs とも連携させたいというモチベーションがあり、このアプリケーションが作られました

## For Contributors

- 本リポジトリへの Issue / PR など、なんでも歓迎です。詳細は [`CONTRIBUTING`](./CONTRIBUTING.md) をご覧ください。
