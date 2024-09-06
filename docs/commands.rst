.. _commands:

========
コマンド
========

statements-manager の実行は次のように行います。

.. code-block:: bash

    $ ss-manager COMMAND [OPTIONS] [ARGS]

使用できるコマンド ``COMMAND`` は以下のとおりです。

run
===

.. code-block:: text
    
    usage: ss-manager run [-h] [-o {html, md, pdf}] [-p] [-f] [-c] [working_dir]

用意した Markdown ファイルを読み込み、指定された形式の出力ファイルを作成します。また、制約ファイルを出力する設定になっているときは、制約ファイルも出力します。

オプション
----------

.. option:: working_dir

    問題文の生成対象となるディレクトリを指定します。何も指定しない場合、コマンドが実行された階層を指定したとみなします。

    ``working_dir`` 以下を再帰的に探索し、見つかった ``problem.toml`` それぞれについて問題文の生成が行われます。ただし ``-p`` がついているときは、問題セットにあるすべての問題に対して問題文の生成が行われることがあります。詳しくは ``-p`` の説明を参照してください。

.. option:: -o, --output
    
    出力ファイルの形式を指定します。オプジョンに続けて ``html``, ``md``, ``pdf`` のいずれかを指定します。
    
    このオプションが指定されていない場合、 ``html`` が指定されているとみなして実行されます。

.. option:: -p, --make-problemset

    問題セットのファイルも出力します。出力形式は ``-o, --output`` オプションで指定されたものに従います。

    .. tip::
        ``working_dir`` の祖先にある ``problemset.toml`` のうち、最も ``working_dir`` に近いものを読み込みます。

        また、 ``-p`` がついていて ``problemset.toml`` が存在するときは、 ``problemset.toml`` が存在するディレクトリの子孫にあるすべての問題に対して問題文の生成が行われます。

.. option:: -f, --force-dump

    キャッシュファイルの情報を無視し、常に出力ファイルを更新します。

    このオプションが付いておらず、既に存在する出力ファイルから内容が変化していない場合は、出力ファイルは更新されません。

    .. tip::
        statements-manager を実行すると、出力ファイルのバージョンを管理するためのファイル ``cache.json`` も出力されます。通常、このファイルに書かれているハッシュ値と一致するときはファイルの更新を行いません。

.. option:: -c, --constraints-only

    制約ファイルのみを更新します。このオプションを付けた場合、問題文の出力ファイルは更新されません。

.. option:: -h, --help

    ヘルプメッセージを出力します。

実行例
------

次のコマンドを考えます。

.. code-block:: bash

    $ ss-manager run ./problems -o pdf

このコマンドは次のように実行されます。

- ``./problems`` 以下にある問題文を対象として出力ファイルを作成する
- PDF 形式で出力する
- 出力ファイルの内容に変化がなければファイルを更新しない

reg-creds
=========

.. code-block:: text

    usage: ss-manager reg-creds [-h] [creds_path]

Google Docs の API credentials を登録します。詳しい登録方法は :ref:`register_credentials` をご覧ください。

.. warning:: 
    **Google Docs にある問題文を扱いたい場合は、このコマンドによる API credential の登録が必須となります。** 問題文がすべてローカル環境に存在する場合はこの操作は不要です。
