.. _problemset_config:

problemset.toml の書き方
========================

必要であれば、適用したいテンプレートを指定するためのファイル ``problemset.toml`` を作成します。このファイルが無い場合は、デフォルトのテンプレートが使用されます。

``problemset.toml`` は、 ``ss-manager run`` を実行するときの ``WORKING_DIR`` の階層と一致しているときにのみ参照されます。

.. tip:: 
    **Rime を使用したことがある方向け**: このファイルは Rime で言うところの ``PROJECT`` ファイルに似た位置づけです。 ``PROJECT`` と同じ階層に保存することを推奨します。

書き方の一例は次のとおりです。より具体的な例は :blob:`リポジトリ内のサンプル <sample/problemset.toml>` をご覧ください。

.. literalinclude:: codes/reference/problemset.toml

設定項目それぞれについて説明します。

.. problemsettoml:: encoding

    入力ファイルおよび出力ファイルの文字コードを指定します。`Python の codec 文字列 <https://docs.python.org/ja/3/library/codecs.html#standard-encodings>`_ を指定してください。
    
    何も設定しなかった場合、 ``utf-8`` が適用されます。


.. problemsettoml:: [template]
    
    .. problemsettoml:: template_path
        
        問題文に適用されるテンプレートファイルへのパスを指定します。指定されていない場合、デフォルトのテンプレート (HTML 形式) が適用されます。
        
        テンプレートでは、問題文本文に相当する部分に ``{@problem.statement}`` 文を記述する必要があります。詳細は :blob:`sample/templates/default.html` などをご覧ください。

        .. tip::

            Markdown 形式で出力する場合 (``--output md`` を指定した場合) 、 ``template_path`` の設定値は使われません。常にデフォルトの Markdown テンプレートが適用されます。
    
    .. problemsettoml:: sample_template_path

        入出力例の部分に使われるテンプレートファイルへのパスを指定します。指定されていない場合、デフォルトのテンプレート (Markdown 形式) が適用されます。

        テンプレートの書き方は :blob:`sample/templates/sample_default.html` などをご覧ください。

    .. problemsettoml:: preprocess_path
        
        変数やサンプルの埋め込み・HTML への変換 (HTML か PDF に変換する場合)・テンプレートの適用 を行う前のファイルに関して前処理を行うスクリプトへのパスを指定します。指定されていない場合、前処理は行われません。
        
        ファイルの中身は標準入力で与えられ、前処理の結果は標準出力で返す必要があります。終了コードが 0 以外であった場合は異常終了とみなし、エラーになります。詳細は :blob:`sample/templates/icpc_domestic/preprocess.py` をご覧ください。

    .. problemsettoml:: preprocess_command
        
        preprocess_path で指定されたスクリプトを実行するためのコマンドを指定します。デフォルトは ``python3`` です。Python 以外のスクリプトを使用する場合や、``python3`` コマンドを使用したい場合などに指定してください。
    
    .. problemsettoml:: postprocess_path
        
        変数やサンプルの埋め込み・HTML への変換 (HTML か PDF に変換する場合)・テンプレートの適用 を行った後のファイルに関して後処理を行うスクリプトへのパスを指定します。指定されていない場合、後処理は行われません。
        
        ファイルの中身は標準入力で与えられ、後処理の結果は標準出力で返す必要があります。終了コードが 0 以外であった場合は異常終了とみなし、エラーになります。詳細は :blob:`sample/templates/icpc_domestic/postprocess.py` をご覧ください。

    .. problemsettoml:: postprocess_command
        
        postprocess_path で指定されたスクリプトを実行するためのコマンドを指定します。デフォルトは ``python3`` です。Python 以外のスクリプトを使用する場合や、``python3`` コマンドを使用したい場合などに指定してください。

    .. problemsettoml:: output_extension

        ``--output custom`` **を指定した場合は必須です。それ以外の場合では無視されます。** ``custom`` についての詳細は :ref:`commands` をご覧ください。
        
        ``custom`` を指定したときの、出力ファイルの拡張子を指定します。


.. problemsettoml:: [pdf]

    PDF 出力時の `wkhtmltopdf <https://wkhtmltopdf.org/>`_ (PDF にレンダリングする際に使用されるサードパーティライブラリ) の設定を書きます。設定項目の詳細については `wkhtmltopdf のリファレンス <https://wkhtmltopdf.org/usage/wkhtmltopdf.txt>`_ をご覧ください。

    .. problemsettoml:: [pdf.common]
        
        各問題のファイルにも、問題セットのファイルにも適用されてほしい設定をここに記載します。
    
    .. problemsettoml:: [pdf.problem]
        
        各問題のファイルにのみ適用されてほしい設定をここに記載します。
    
    .. problemsettoml:: [pdf.problemset]
        
        問題セットのファイルにのみ適用されてほしい設定をここに記載します。



