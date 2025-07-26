.. _examples:

=======================
Rime と組み合わせて使う
=======================

statements-manager は、問題作成支援ツール :github:`Rime <icpc-jag/rime>` と組み合わせて使うことを想定した作りになっています。statements-manager は問題文の準備作業を補助し、Rime は問題文作成を除くすべての工程の準備作業を補助するツールです。

このため、想定しているディレクトリ構成も Rime と似ています。設定ファイル類は以下のように配置することを推奨しています。

- 問題セットに関する設定を行うファイル ``problemset.toml`` は、Rime のプロジェクト設定ファイル ``PROJECT`` と同じ階層に置く
- 各問題に関する設定を行うファイル ``problem.toml`` は、Rime の問題設定ファイル ``PROBLEM`` と同じ階層に置く
- 制約ファイルの出力先 ``params_path`` は、Rime で入力生成器・入力検証器を配置するディレクトリ ``tests`` と同じ階層のパスにする
- サンプルケースが含まれているディレクトリへのパス ``sample_path`` は、Rime でサンプルケースを使って模範解答 (reference solution) を実行した結果が格納されるディレクトリ ``rime-out/tests`` と同じ階層のパスにする

また、組み合わせて使う際に推奨している実行順は以下のとおりです。

.. code-block:: text

    # create constraints files
    $ ss-manager run -c WORKING_DIR

    # create correct sample outputs
    $ rime clean WORKING_DIR
    $ rime test WORKING_DIR

    # create problem statements
    $ ss-manager run WORKING_DIR

statements-manager によって、問題の制約ファイルを更新します。次に、その制約ファイルを使って Rime でデータセットを生成し、用意された解法が正しく動作するかどうかをチェックします。その後に、問題文の出力ファイルを更新します。この順番で操作することで、問題文とデータセットの制約のズレを減らすことができます。

========================================
リポジトリにある問題文を半自動で更新する
========================================

GitHub Actions などの CI サービスと併用することで、リポジトリに変更が加えられたときに問題文に関する成果物の差分を push し、常にリポジトリ内の問題文を最新の状態に保つことが可能です。

設定の一例を以下に示します。これは ``master`` ブランチに push された際に ``ss-manager run`` を実行し、差分を自動で push するものです。以下の実装を、リポジトリに ``.github/workflows/statements-manager.yml`` として保存すると動作するはずです。

.. code-block:: yaml
    :linenos:
    
    # run statements-manager and commit/push diffs
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
            python-version: 3.9
        - name: Install dependencies
            run: |
            python3 -m pip install --upgrade pip
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

エラーハンドリングについて
==========================

バージョン 1.8.0 から、問題文の取得時にエラーが発生した場合の動作が変更されました。

デフォルトの動作
----------------

問題文の取得でエラーが発生した場合、処理が即座に停止し、非ゼロの終了コードで終了します。これにより、CI 環境でエラーを確実に検出できます。

.. code-block:: bash

    $ ss-manager run ./
    # エラーが発生すると exit code 1+ で終了

従来の動作（エラーを無視）
--------------------------

従来のようにエラーが発生しても処理を継続したい場合は、 ``-k, --keep-going`` オプションを使用してください。

.. code-block:: bash

    $ ss-manager run ./ -k

CI での活用例
-------------

GitHub Actions で使用する場合、エラーハンドリングの方針に応じてコマンドを選択してください：

**エラーがあれば CI を失敗させたい場合：**

.. code-block:: yaml

    - name: Run statements-manager
      run: |
        ss-manager run ./

**一部エラーがあっても成果物を生成したい場合：**

.. code-block:: yaml

    - name: Run statements-manager
      run: |
        ss-manager run ./ -k
