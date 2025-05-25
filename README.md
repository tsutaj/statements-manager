# statements-manager

![format workflow](https://github.com/tsutaj/statements-manager/actions/workflows/format.yml/badge.svg) ![pypi workflow](https://github.com/tsutaj/statements-manager/actions/workflows/pypi.yml/badge.svg) [![Documentation Status](https://readthedocs.org/projects/statements-manager/badge/?version=stable)](https://statements-manager.readthedocs.io/ja/stable/?badge=stable)

![PyPI](https://img.shields.io/pypi/v/statements-manager) [![Python Versions](https://img.shields.io/pypi/pyversions/statements-manager.svg)](https://pypi.org/project/statements-manager/)

**English description is under preparation. Sorry for inconvenience.**

競技プログラミングの作問時に使用する、問題文管理を便利にするツール

## What is this?

- Markdown 形式で記述された「制約やサンプルの情報を外部に委ねた」問題文ファイルを、 HTML / PDF / Markdown 形式に変換して出力します
  - 制約やサンプルは問題文に直接的には書きません。詳しくは Documentation を参照してください。
- **特長**: 問題の制約・サンプル管理の一本化
  - 問題制約は、問題設定ファイル内で記述します
  - 定義したものを問題文ファイルで利用することができるほか、generator / validator で利用可能な形で出力することができます
  - **「制約やサンプルを途中で変更したので、問題文・generator / validator の双方をそれぞれ変更する」という作業をする必要がなくなります**
  - **問題文とデータセットでサンプルが一致しているかを確認する必要がなくなります**
- Google Docs 上の問題文 / ローカル上の問題文の両方に対応
  - **Google Docs で管理している問題文** であっても、制約やサンプルを一元的に管理できます

## Screencast

![screencast](https://user-images.githubusercontent.com/19629946/131149286-39111b9b-9719-4693-98f9-88ed8caea34d.gif)

## Documentation

Sorry, currently Japanese only :bow:

https://statements-manager.readthedocs.io/

## License

- Apache-2.0
