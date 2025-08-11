.. _commands:

========
コマンド
========

statements-manager の実行は次のように行います。

.. code-block:: bash

    $ ss-manager COMMAND [OPTIONS] [ARGS]

使用できるコマンド ``COMMAND`` は以下のとおりです。

setup
=====

.. code-block:: text

    usage: ss-manager setup [-h] [-i ID] [-m {local,docs}] [-l {ja,en} [{ja,en} ...]] [-t TEMPLATE] working_dir

指定した作業ディレクトリに、問題文のファイルや、適切に構成された ``problem.toml`` ファイルなどを作成します。作業ディレクトリの初期設定に便利です。

オプション
----------

.. option:: working_dir

    新しい問題の作業ディレクトリ名を指定します。

.. option:: -i, --id

    問題 ID を指定します。指定しない場合、ディレクトリ名を問題 ID として使用します。

.. option:: -m, --mode

    問題文の保存場所を指定します。 ``local`` または ``docs`` を選択できます。デフォルトは ``local`` です。

    - ``local``: ローカルファイルとして問題文を作成
    - ``docs``: Google Docs ドキュメントとして問題文を作成
        
        - 認証を行ったアカウントの Google Drive のマイドライブ上に Google Docs ドキュメントが作成されます
        - 作成された Google Docs ドキュメントの ID が ``problem.toml`` に記録されます

    .. tip::
        ``docs`` モードを使用する場合は、事前に ``ss-manager auth login`` で認証を行う必要があります。

.. option:: -l, --language

    問題文の言語を指定します。 ``ja`` または ``en`` を選択できます。デフォルトは ``en`` です。複数の言語を指定することも可能です。

    - 単一言語の場合: ``-l en`` または ``-l ja``
    - 複数言語の場合: ``-l en ja``

    .. tip::
        同じ言語名を複数回指定することで、同じ言語の問題文を複数作成できます。問題設定が同じで制約だけが異なる複数の問題を出題したい場合にご利用ください。

        たとえば、 ``-l ja ja`` と指定すると、日本語の問題文を 2 つ作成します。


.. option:: -t, --template

    テンプレートファイルのパスを指定します。指定したファイルの内容が、作成されるすべての問題文ファイルにコピーされます。
    
    指定しなかった場合は、空の問題文ファイルが作成されます。

.. option:: -h, --help

    ヘルプメッセージを出力します。

作成されるファイル構造
----------------------

setup コマンドを実行すると、 ``working_dir`` 以下に次のファイルやディレクトリが作成されます。

- ``problem.toml``: 問題設定ファイル
- ``tests/``: テストケース用ディレクトリ
- ``statement/``: ローカル問題文ファイル用ディレクトリ（ ``local`` モードの場合のみ）
- Google Docs ドキュメント（ ``docs`` モードの場合のみ）

また、生成される ``problem.toml`` は、主に次の情報を含みます。

- 問題 ID
- 問題文情報: ローカルファイルへのパス または Google Docs ID
- 言語設定
- デフォルトのパラメータパス: ``./tests/constraints.hpp``

run
===

.. code-block:: text
    
    usage: ss-manager run [-h] [-o {html, md, pdf}] [-p] [-f] [-c] [-k] [--fail-on-suggestions] [working_dir]

用意した Markdown ファイルを読み込み、指定された形式の出力ファイルを作成します。また、制約ファイルを出力する設定になっているときは、制約ファイルも出力します。

オプション
----------

.. option:: working_dir

    問題文の生成対象となるディレクトリを指定します。何も指定しない場合、コマンドが実行された階層を指定したとみなします。

    ``working_dir`` 以下を再帰的に探索し、見つかった ``problem.toml`` それぞれについて問題文の生成が行われます。ただし ``-p`` がついているときは、問題セットにあるすべての問題に対して問題文の生成が行われることがあります。詳しくは ``-p`` の説明を参照してください。

.. option:: -o, --output
    
    出力ファイルの形式を指定します。オプジョンに続けて ``html``, ``md``, ``pdf``, ``custom`` のいずれかを指定します。
    
    このオプションが指定されていない場合、 ``html`` が指定されているとみなして実行されます。

    .. tip::
        PDF ファイルの出力には `Python-PDFKit <https://github.com/JazzCore/python-pdfkit>`_ を利用しています。出力時にトラブルが発生した場合は、PDFKit に関する情報も参考にしてください。

        PDF ファイルの出力機能は備えていますが、任意のデザインで出力できることは保証しません。当アプリケーションの機能で所望のデザインが実現できない場合は、独自の方法で HTML ファイルから PDF ファイルを生成することもご検討ください。

    .. tip:: 
        ``custom`` が指定されたときは、次のように動作します。
        
        - HTML への変換は行いません。
        - 前処理の適用・テンプレートファイルの適用・後処理の適用は行います。
        
        この機能は、HTML / Markdown / PDF 以外の形式に変換したい場合や、出力ファイルをさらに細かくカスタマイズしたい場合に役立ちます。

        なお、``custom`` を指定した場合、 ``problemset.toml`` の ``[template]`` セクションに ``output_extension`` を指定する必要があります。詳しくは :ref:`problemset_config` や :tree:`リポジトリ内のサンプル <sample_tex>` をご覧ください。

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

.. option:: -k, --keep-going

    問題文の取得時にエラーが発生した場合でも処理を継続します。このオプションが付いていない場合、問題文の取得エラーが発生すると処理が停止し、非ゼロの終了コードで終了します。

.. option:: --fail-on-suggestions

    Google Docs に未解決の提案（コメント）が存在する場合に失敗扱いにします。このオプションが付いている場合、Google Docs から問題文を取得した際に未解決の提案があると、処理が停止し、非ゼロの終了コードで終了します。

    このオプションが付いていない場合、未解決の提案は警告として出力されますが、処理は継続されます。

    .. tip::
        このオプションは作業終盤に未解決の提案が残っていないかを確認したい場合に役立ちます。ローカルファイルの問題文には影響しません。

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
- 問題文の取得時にエラーが発生した場合は処理が停止し、非ゼロの終了コードで終了する

  - エラーが発生しても処理を継続したい場合は ``-k`` オプションを指定してください

auth
====

.. code-block:: text

    usage: ss-manager auth [-h] {login,logout,status,use} ...

Google Docs への認証を管理します。

.. option:: -h, --help

    ヘルプメッセージを出力します。

サブコマンド
------------

.. option:: login

    OAuth2 を使用して Google アカウントで認証します。ブラウザが開いて Google アカウントでの認証を行います。

    .. warning::
        この認証方法では、statements-manager を介して自分のアカウントで作成した Google Docs のみを読み書きできます。これはセキュリティ上の制限によるものです。

    .. option:: --force

        既にログインしている場合でも、強制的に再認証を行います。

.. option:: logout

    保存された認証情報を削除し、ログアウトします。

.. option:: status

    現在の認証状況を確認します。次の情報が表示されます。

    - 現在の認証方法の優先順位
    - OAuth2 ログインの状況
    - 手動登録した credentials の状況

.. option:: use

    認証方法の優先順位を設定します。これにより、statements-manager が Google Docs にアクセスする際に、どの認証方法を最初に試すかを制御できます。
    
    ``use`` に続けて、次のいずれかを指定します。

    - ``login``: ``ss-manager auth login`` で行った認証を優先
    - ``creds``: ``ss-manager reg-creds`` で登録した credentials を使用する認証を優先

    .. tip::
        設定した優先順位の認証方法が失敗した場合は、自動的に別の認証方法が試されます。

reg-creds
=========

.. code-block:: text

    usage: ss-manager reg-creds [-h] [creds_path]

Google Docs の API credentials を手動で登録します。詳しい登録方法は :ref:`register_credentials` をご覧ください。

.. tip::
    この認証方法では、アカウントがアクセスできるすべての Google Docs を利用できます。
