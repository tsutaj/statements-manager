# Contribution Guide

このリポジトリへのコントリビュートに関するガイドです。

## Issues

なんでも歓迎です。例えば以下のようなトピックが考えられます。

- 不具合報告
- 機能追加・機能改善の提案
- 使い方に関する質問

## Pull Request

- Pull Request は **`master` ブランチをターゲットブランチにして** 発行してください
- 作業に関連する Issues が存在する場合は、可能な限り Issues へのリンクを示してください
  - Issue 番号 `XXX` に対する PR である場合、概要欄のどこかに `ref: #XXX` と書いてあるとわかりやすいです

## 開発環境の準備

このガイドでは、Python で書かれたパッケージに対して初めてコミットする方向けに、開発手法のうちのひとつを説明しています。既に何らかの開発手法について理解されている方は、この節を読む必要はありません。

### 1. Python (>= 3.9.12) をインストールする

[Python 公式ページ](https://www.python.org/downloads/) を参照してください。リンク先のページを見てもよくわからない場合は、お使いの OS をキーワードにして検索すると良いでしょう。(例えば Windows を使用している場合、["Python3 Windows インストール方法"](https://www.google.com/search?channel=fs&client=ubuntu&q=Python3+Windows+%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E6%96%B9%E6%B3%95) で検索する、など)

### 2. リポジトリを fork & clone する

[git](https://git-scm.com/downloads) をインストールしたのち、本リポジトリを fork & clone してください。

fork & clone をするには [GitHub のアカウント](https://github.com/) が必要です。必要であればアカウントを作成してください。

- fork の手順は [「リポジトリをフォークする」](https://docs.github.com/ja/github/getting-started-with-github/quickstart/fork-a-repo) をご覧ください。
- clone の手順は [「リポジトリをクローンする」](https://docs.github.com/ja/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository) をご覧ください。

fork したあなた (ユーザー名: `USER_NAME`) のリポジトリの名前が `YOUR_REPOSITORY` である場合、以下のコマンドで clone することができるはずです。

```bash
$ git clone https://github.com/USER_NAME/YOUR_REPOSITORY.git
```

### 3. 仮想環境をセットアップし、仮想環境上で作業する

- `venv` で仮想環境を作る

```bash
$ python3 -m venv ./virtualenv
$ source ./virtualenv/bin/activate
(virtualenv) $ # 仮想環境に入った際にはこのように表示されます
```

- `setup.py` 経由で、仮想環境に `statements-manager` をインストールする
  - 実装したものをデバッグするには、この環境で実行すると良いです。仮想環境を使用する利点は、あなたが普段使用する Python の環境を汚すことなく開発中のプログラムをインストール・実行できることです。

```bash
(virtualenv) $ python3 setup.py install
```

- (必要に応じて) 仮想環境から抜ける

```bash
(virtualenv) $ deactivate
```
