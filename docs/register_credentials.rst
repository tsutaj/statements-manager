.. _register_credentials:

================================
Google Docs API を使用可能にする
================================

.. warning:: 
    **Google Docs にある問題文を扱いたい場合は、この操作が必須となります。** 問題文がすべてローカル環境に存在する場合はこの操作は不要です。

作業ディレクトリ ``WORKING_DIR`` に対して、以下で説明する credentials というものを登録します。

- `Google Docs - Quickstart <https://developers.google.com/docs/api/quickstart/python>`_ の手順通りに進め、API を使える状態にします。リンク先のサンプルを実行できるかどうかで動作確認が可能です。
    - 扱いたい Docs ファイルが閲覧できる権限を持っているアカウントで作成しなければならないはずですので、アカウントの選択に注意してください

- `Google Cloud Platform <https://console.cloud.google.com/>`_ にアクセスし、「API とサービス」→「認証情報」に進みます

.. image:: https://user-images.githubusercontent.com/19629946/130088968-92409236-ef85-49c5-a244-33e4380308ea.png
    :alt: 「認証情報」セクションの場所を示す画像

- 以下の画面で OAuth クライアントをダウンロードします。JSON ファイルを任意の場所にダウンロードしてください
    - 以降の説明では、ダウンロードした場所が ``CREDS_PATH`` であるとします

.. image:: https://user-images.githubusercontent.com/19629946/130088491-761cf3bb-6b8c-4bb4-9396-91e98be6ab8a.png
    :alt: OAuth クライアントをダウンロードできる場所を示す画像

.. image:: https://user-images.githubusercontent.com/19629946/130088501-5e1208df-445a-4797-be31-60a77f04c91d.png
    :alt: JSON ファイルをダウンロードできる場所を示す画像

- 以下のコマンドを打って、JSON ファイルを登録します
    - 登録が終われば、 ``CREDS_PATH`` にある json ファイルは削除しても構いません
    - JSON ファイルは、ホームディレクトリに生成される隠しフォルダ ``.ss-manager`` の中に格納されます

.. code-block:: bash
    :class: highlight

    $ ss-manager reg-creds CREDS_PATH
