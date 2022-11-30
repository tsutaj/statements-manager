.. _quickstart:

================
クイックスタート
================

リポジトリにある例を試してみたい方へ
------------------------------------

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


.. _ss_manager_from_scratch:

ゼロから設定して問題文を作ってみたい方へ
----------------------------------------

「:math:`A` と :math:`B` が与えられるので,
:math:`A + B` の計算結果を出力してください」という問題を作りたいとします。

.. warning:: 
    TODO(tsutaj): 書く