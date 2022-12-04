.. _examples:

=======================
Rime と組み合わせて使う
=======================

.. warning::
    TODO(tsutaj): 書く

========================================
リポジトリにある問題文を半自動で更新する
========================================

GitHub Actions などの CI サービスと併用することで、リポジトリに変更が加えられたときに問題文に関する成果物の差分を push し、常にリポジトリ内の問題文を最新の状態に保つことが可能です。

設定の一例を以下に示します。これは ``master`` ブランチに push された際に ``ss-manager run`` を実行し、差分を自動で push するものです。以下の実装を、リポジトリに ``.github/workflows/statements-manager.yml`` として保存すると動作するはずです。

.. code-block:: yaml
    :linenos:
    
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
