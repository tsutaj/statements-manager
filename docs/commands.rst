.. _commands:

========
コマンド
========

statements-manager の実行は次のように行います。

.. code-block:: bash

    $ ss-manager COMMAND [OPTIONS] [ARGS]

また、 ``-h``, ``--help`` を付けることでヘルプメッセージを表示できます。コマンドを指定すると、そのコマンドに関するヘルプを見ることができます。

使用できるコマンドは以下のとおりです。

.. describe:: ss-manager run [OPTIONS] [WORKING_DIR]

用意した Markdown ファイルを読み込み、指定された形式の出力ファイルを作成します。また、制約ファイルを出力する設定になっているときは、制約ファイルも出力します。

.. describe:: ss-manager reg-creds CREDS_PATH

Google Docs の API credentials を登録します。詳しい登録方法は :ref:`register_credentials` をご覧ください。

.. warning:: 
    **Google Docs にある問題文を扱いたい場合は、このコマンドによる API credential の登録が必須となります。** 問題文がすべてローカル環境に存在する場合はこの操作は不要です。
