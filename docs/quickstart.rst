.. _quickstart:

================
クイックスタート
================

リポジトリにある例を試してみたい方へ
====================================

まずは動作させてみたいという方は、以下のようにコマンドを実行してください。

.. code-block:: bash

    $ pip install statements-manager
    $ git clone https://github.com/tsutaj/statements-manager.git
    $ cd statements-manager
    
    $ ss-manager run ./sample

``ss-manager run ./sample`` を実行した後は、H 問題以外の各問題ディレクトリについて、 ``ss-out`` ディレクトリ内に HTML が生成されており、 ``tests`` ディレクトリ内に制約ファイルが生成されているはずです。

H 問題の問題文は Google Docs にあるため、この手順だけでは HTML 生成ができません。:ref:`google_docs_api` で述べられている設定を行うと、H 問題に関しても HTML 生成が可能です。

デフォルトでは HTML が生成されますが、Markdown や PDF の出力にも対応しています。出力形式を指定するには ``-o``, ``--output`` オプションを使います。

.. code-block:: bash

    # generate Markdown files
    ss-manager run ./sample -o md

    # generate PDF files
    ss-manager run ./sample -o pdf

また、 ``-p``, ``--make-problemset`` オプションによって、問題セット全体をまとめたファイルの生成も可能です。

.. code-block:: bash

    # generate problemset PDF
    ss-manager run ./sample -o pdf -p

さらに詳しく使い方を知りたい方は、 :ref:`how_to_use` をご覧ください。

.. _introduce_this_tool:

本ツールの導入の流れを知りたい方へ
==================================

問題文と設定ファイルを実際に用意して動作させることで、本ツールの導入の流れを説明します。

ここでは、「整数 :math:`A` と :math:`B` が与えられるので、
:math:`A + B` の計算結果を出力してください」という問題を作りたいときに、どのように問題文を準備すればよいか説明します。ファイル構成などの詳細を確認したいときは `リポジトリ内のサンプル <https://github.com/tsutaj/statements-manager/tree/master/sample/A>`_ を参照してください。

問題文を用意する
----------------

問題文を普通に書くと、以下のような Markdown ファイル ``statement.md`` を作ることになるでしょう。(数式は MathJax を想定した記法になっています)

.. literalinclude:: codes/quickstart/statement_hardcode.md
    :language: markdown

この Markdown にはいくつか問題点があります。

- 入力 :math:`A, B` に対する制約がファイルに直接書かれています。仮に :math:`A, B` の上限をともに :math:`10^{9}` から :math:`10^{18}` に変更しなければならないとき、問題文の制約とデータセット生成器で使う制約を両方変更しなければなりませんが、これを別々に変更するとミスが起きやすいです。
- サンプル入出力も直接書かれているため、上で述べたことと同様の問題が起きやすいです。また、サンプルのナンバリングもファイルに直接書かれているため、番号が重複したり抜け落ちたりする可能性があります。

これらの問題を解消するため、statements-manager を導入して問題文を書き直していきます。

問題制約とサンプル入出力を別ファイルに移す
------------------------------------------

サンプル入出力を別ファイルに移します。入力例 1 に対応するファイルは ``00_sample_00.in`` に、出力例 1 に対応するファイルは ``00_sample_00.out`` に用意します。同様に入出力例 2 に対応するファイル ``00_sample_01.in``, ``00_sample_01.out`` も用意します。これらのファイルは全て ``tests`` というディレクトリ内に格納しておきます。

また、問題制約を問題文ファイルから分離するため、以下のような設定ファイル ``problem.toml`` を用意します。

.. literalinclude:: codes/quickstart/problem.toml
    :language: toml

これで問題制約とサンプル入出力を問題文から分離できました！最後に、問題文のファイル ``statement.md`` を次のように書き換えます。

.. literalinclude:: codes/quickstart/statement.md
    :language: Markdown

重要なのは、 **問題制約とサンプル入出力が問題文ファイルに直接書かれていない** ことです。

ここまで作ったファイルの階層を整理してみましょう。以下と同じであれば OK です。
   
.. code-block:: text

    problem.toml
    statement.md
    tests/
    ├─ 00_sample_00.in
    ├─ 00_sample_00.out
    ├─ 00_sample_01.in
    └─ 00_sample_01.out

ツールを実行して出力結果を得る
------------------------------

ここまで用意できたら、statements-manager を実行していきます。 ``problem.toml`` と同じ階層で以下のコマンドを実行します。

.. code-block:: bash

    $ ss-manager run

実行が終わると ``ss-out/A.html`` というファイルと、 ``tests/constraints.hpp`` というファイルが出来ているはずです。

``ss-out/A.html`` ファイルは、問題制約やサンプルが埋め込まれた後の HTML 形式の問題文です。

.. image:: images/quickstart/a_plus_b.png

``tests/constraints.hpp`` は、問題制約が書かれた C++ 形式のファイルであり、内容は以下のとおりです。 **このファイルを使ってデータセットを作ることで、問題文と同じ制約でデータセットを作ることができます。**

.. literalinclude:: codes/quickstart/constraints.hpp
    :language: cpp

問題文を編集して statements-manager を実行することで、問題文の出力結果と問題制約のファイルが得られることを学んできました。さらに詳しく使い方を知りたい方は、 :ref:`how_to_use` をご覧ください。