.. _write_problem_statement:

==============
問題文の書き方
==============

ローカル・Google Docs のいずれにおいても、問題文は Markdown 形式で記述してください。

入力形式を表す箇所はバッククオート 3 つで囲みます。以下がその例です。

.. literalinclude:: codes/reference/sample_input_format.md
    :language: text

問題文中では以下の記法が使用できます。いずれの記法に関しても、出力ファイル上では何らかのパラメータ・ファイルに置換されます。使用例は :tree:`リポジトリ内のサンプル <sample>` をご覧ください。

.. statementvar:: {@constraints.<CONSTRAINT_NAME>}
    
    問題制約のパラメータに置換されます。パラメータ名 ``<CONSTRAINT_NAME>`` は ``problem.toml`` の ``[constraints]`` で記述されている定数名である必要があります。

.. statementvar:: {@samples.s<NUMBER>}

    サンプルに関連するファイル群のうち、 ``<NUMBER>`` 番目 (leading-zero は許容しない) のものに置換されます。
    
    サンプルの名前は拡張子を無視した状態で集合として管理されており、辞書順で小さいものから 1, 2, 3, ... と番号付けられています。例えばサンプルに関連するファイルが ``00_sample_00.in``, ``00_sample_00.out``, ``00_sample_00.md``, ``00_sample_01.in``, ``00_sample_01.out`` の 5 つであった場合、 ``00_sample_00`` が 1 番目・ ``00_sample_01`` が 2 番目となります。

.. statementvar:: {@samples.all}
    
    ``problem.toml`` の ``sample_path`` で指定されたディレクトリ以下にある、サンプルに関連するすべてのファイル群に置換されます。
    
    サンプルの挿入順番は、上述したサンプルの順序の通りに行われます。
