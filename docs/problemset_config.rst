.. _problemset_config:

problemset.toml の書き方
========================

必要であれば、HTML・PDF に適用されるテンプレートを指定するためのファイル ``problemset.toml`` を作成します。このファイルが無い場合は、デフォルトのテンプレートが使用されます。

``problemset.toml`` は、 ``ss-manager run`` を実行するときの ``WORKING_DIR`` の階層と一致しているときにのみ参照されます。

.. tip:: 
    **Rime を使用したことがある方向け**: このファイルは Rime で言うところの ``PROJECT`` ファイルに似た位置づけです。 ``PROJECT`` と同じ階層に保存することを推奨します。

書き方の一例は次のとおりです。より具体的な例は :blob:`リポジトリ内のサンプル <sample/problemset.toml>` をご覧ください。

.. literalinclude:: codes/reference/problemset.toml

設定項目それぞれについて説明します。

.. problemsettoml:: [template]
    
    .. problemsettoml:: template_path
        
        HTML および PDF 出力で使用されるテンプレート HTML へのパスを指定します。指定されていない場合、デフォルトのテンプレートが適用されます。
        
        テンプレートでは、問題文本文に相当する部分に ``{@problem.statement}`` 文を記述する必要があります。詳細は :blob:`sample/templates/default.html` などをご覧ください。
    
    .. problemsettoml:: sample_template_path

        入出力例の部分に使われるテンプレート HTML へのパスを指定します。指定されていない場合、デフォルトのテンプレートが適用されます。

        テンプレートの書き方は :blob:`sample/templates/sample_default.html` などをご覧ください。

    .. problemsettoml:: preprocess_path
        
        Markdown ファイルに関して前処理を行う **Python スクリプト** へのパスを指定します。Markdown が HTML 形式にレンダリングされる前に適用したい処理を記述してください。指定されていない場合、前処理は行われません。
        
        Markdown ファイルの中身は標準入力で与えられ、前処理の結果は標準出力で返す必要があります。終了コードが 0 以外であった場合は異常終了とみなし、エラーになります。詳細は :blob:`sample/templates/icpc_domestic/preprocess.py` をご覧ください。
    
    .. problemsettoml:: postprocess_path
        
        HTML ファイルに関して後処理を行う **Python スクリプト** へのパスを指定します。HTML 形式にレンダリングされた後に適用したい処理を記述してください。指定されていない場合、後処理は行われません。
        
        HTML ファイルの中身は標準入力で与えられ、後処理の結果は標準出力で返す必要があります。終了コードが 0 以外であった場合は異常終了とみなし、エラーになります。詳細は :blob:`sample/templates/icpc_domestic/postprocess.py` をご覧ください。

.. problemsettoml:: [pdf]

    PDF 出力時の `wkhtmltopdf <https://wkhtmltopdf.org/>`_ (PDF にレンダリングする際に使用されるサードパーティライブラリ) の設定を書きます。設定項目の詳細については `wkhtmltopdf のリファレンス <https://wkhtmltopdf.org/usage/wkhtmltopdf.txt>`_ をご覧ください。

    .. problemsettoml:: [pdf.common]
        
        各問題のファイルにも、問題セットのファイルにも適用されてほしい設定をここに記載します。
    
    .. problemsettoml:: [pdf.problem]
        
        各問題のファイルにのみ適用されてほしい設定をここに記載します。
    
    .. problemsettoml:: [pdf.problemset]
        
        問題セットのファイルにのみ適用されてほしい設定をここに記載します。



