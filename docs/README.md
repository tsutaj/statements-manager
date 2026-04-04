# Docs Build Guide

## 前提条件

- Python 3.x
- git リポジトリ上で実行すること（sphinx-polyversion が git 履歴を参照するため）

## ビルド手順

リポジトリルートで以下を実行します。

```bash
python3 -m venv venv-docs
source venv-docs/bin/activate
pip install -r docs/requirements.txt
sphinx-polyversion docs/poly.py
```

出力は `docs/_build/` に生成されます。

## 仕組み

`sphinx-polyversion` は以下の処理を自動で行います。

1. git のブランチ・タグをチェックアウト
   - ブランチ: `master`, `stable`
   - タグ: `v1.7.xx`以降、`v1.8.x`以降、`v2.x.x`以降
2. `docs/.venv` に一時的な venv を作成し依存パッケージをインストール
3. 各バージョンの Sphinx ビルドを実行
4. `docs/_build/` にバージョンごとの HTML を出力

## ローカルビルド（モックモード）

未コミットのローカルファイルだけをビルドしたい場合は `--mock` オプションを使います。

```bash
sphinx-polyversion docs/poly.py --mock
```

`poly.py` 内の `MOCK_DATA` に定義されたダミーのバージョン情報でビルドされます。
