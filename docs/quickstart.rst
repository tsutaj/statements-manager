.. _quickstart:

Quickstart
============

.. warning:: 
    TODO(tsutaj): 分かりやすく書く

まずは動作させてみたいという方は、以下のようにコマンドを実行してください。

.. code-block:: bash

    # 初回のみ
    pip install statements-manager
    git clone https://github.com/tsutaj/statements-manager.git

    # on 'statements-manager' directory
    ss-manager run ./sample

    # 実行後は、各問題ディレクトリ (H 問題以外) について
    # - ss-out ディレクトリ内に HTML が生成されている
    # - tests ディレクトリ内に制約ファイルが生成されている

    # "How to use" の 1. で述べられている設定を行うと H 問題に関しても HTML 生成可能です

