.. _files_organization:

====================
推奨するファイル構成
====================

以下のようなディレクトリ構成を推奨しています。作問支援ツールである `Rime <https://github.com/icpc-jag/rime>`_ を使用するときのディレクトリ構成と似ています。

.. code-block:: text

    --- WORKING_DIR/
        |
        |- A/                 (directory of Problem A)
        |  |- tests/          (generator / validator / sample cases)
        |  |- statement/      (problem statement, assets such as images)
        |  |- problem.toml    (problem config file for ss-manager)
        |  |- solution_1/     (solution)
        |  |- solution_2/     (solution)
        |  ...
        |
        |- B/                 (directory of Problem B)
        |  |- (same as above)
        |  ...
        |
        ...