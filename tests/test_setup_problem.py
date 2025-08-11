import pathlib
import re
import tempfile
from collections import Counter
from unittest.mock import Mock, patch

import pytest

from statements_manager.src.setup_problem import (
    create_google_docs,
    create_local_statement,
    get_initial_content,
    get_problem_id,
    setup_problem,
)


class TestGetProblemId:
    """get_problem_id関数のテスト"""

    def test_with_specified_id(self):
        """specified_idが指定されている場合、その値を返すことを確認"""
        result = get_problem_id("A", "default")
        assert result == "A"

    def test_with_none_specified_id(self):
        """specified_idがNoneの場合、default_idを返すことを確認"""
        result = get_problem_id(None, "default")
        assert result == "default"

    def test_with_empty_string(self):
        """specified_idが空文字列の場合、その値を返すことを確認"""
        result = get_problem_id("", "default")
        assert result == ""


class TestGetInitialContent:
    """get_initial_content関数のテスト"""

    def test_with_none_template_path(self):
        """template_pathがNoneの場合、空文字列を返すことを確認"""
        result = get_initial_content(None)
        assert result == ""

    def test_with_existing_template(self):
        """テンプレートファイルが存在する場合、その内容を読み込んで返すことを確認"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            template_content = "# Problem Statement\n\nThis is a test template."
            f.write(template_content)
            template_path = f.name

        try:
            result = get_initial_content(template_path)
            assert result == template_content
        finally:
            pathlib.Path(template_path).unlink()

    def test_with_nonexistent_template(self):
        """テンプレートファイルが存在しない場合、FileNotFoundErrorを発生させることを確認"""
        with pytest.raises(
            FileNotFoundError, match="Template file nonexistent.md not found"
        ):
            get_initial_content("nonexistent.md")


class TestCreateGoogleDocs:
    """create_google_docs関数のテスト"""

    @patch("statements_manager.src.setup_problem.get_oauth_token")
    @patch("statements_manager.src.setup_problem.build")
    def test_success(self, mock_build, mock_get_oauth_token):
        """Google Docsの作成が成功する場合のテスト"""
        # モックの設定
        mock_token = Mock()
        mock_get_oauth_token.return_value = mock_token

        mock_service = Mock()
        mock_build.return_value = mock_service

        # ドキュメント作成のモック
        mock_created_doc = {"documentId": "test_doc_id"}
        mock_service.documents().create.return_value.execute.return_value = (
            mock_created_doc
        )

        # batchUpdateのモック
        mock_service.documents().batchUpdate.return_value.execute.return_value = None

        # テスト実行
        result = create_google_docs(
            problem_id="A",
            initial_content="# Test Content",
            lang="en",
            language_count=1,
            language_frequency=Counter(["en"]),
        )

        # 結果の検証
        assert result == "test_doc_id"
        mock_get_oauth_token.assert_called_once()
        mock_build.assert_called_once_with(
            "docs", "v1", credentials=mock_token, cache_discovery=False
        )
        mock_service.documents().create.assert_called_once_with(body={"title": "A"})
        mock_service.documents().batchUpdate.assert_called_once()

    @patch("statements_manager.src.setup_problem.get_oauth_token")
    @patch("statements_manager.src.setup_problem.build")
    def test_with_multiple_languages(self, mock_build, mock_get_oauth_token):
        """複数言語がある場合のタイトル生成をテスト"""
        mock_token = Mock()
        mock_get_oauth_token.return_value = mock_token

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_created_doc = {"documentId": "test_doc_id"}
        mock_service.documents().create.return_value.execute.return_value = (
            mock_created_doc
        )
        mock_service.documents().batchUpdate.return_value.execute.return_value = None

        # 複数言語のカウンター
        language_frequency = Counter(["en", "ja"])

        create_google_docs(
            problem_id="A",
            initial_content="",
            lang="en",
            language_count=1,
            language_frequency=language_frequency,
        )

        # タイトルに言語サフィックスが付くことを確認
        mock_service.documents().create.assert_called_once_with(body={"title": "A_en"})

    @patch("statements_manager.src.setup_problem.get_oauth_token")
    @patch("statements_manager.src.setup_problem.build")
    def test_with_multiple_same_language(self, mock_build, mock_get_oauth_token):
        """同じ言語が複数ある場合のタイトル生成をテスト"""
        mock_token = Mock()
        mock_get_oauth_token.return_value = mock_token

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_created_doc = {"documentId": "test_doc_id"}
        mock_service.documents().create.return_value.execute.return_value = (
            mock_created_doc
        )
        mock_service.documents().batchUpdate.return_value.execute.return_value = None

        # 同じ言語が複数あるカウンター
        language_frequency = Counter(["en", "en"])

        create_google_docs(
            problem_id="A",
            initial_content="",
            lang="en",
            language_count=1,  # 1番目のen
            language_frequency=language_frequency,
        )

        # タイトルにカウントが付くことを確認（同じ言語が複数ある場合）
        mock_service.documents().create.assert_called_once_with(body={"title": "A1"})

    @patch("statements_manager.src.setup_problem.get_oauth_token")
    @patch("statements_manager.src.setup_problem.build")
    def test_with_multiple_languages_and_same_language(
        self, mock_build, mock_get_oauth_token
    ):
        """同じ言語が複数ある場合のタイトル生成をテスト"""
        mock_token = Mock()
        mock_get_oauth_token.return_value = mock_token

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_created_doc = {"documentId": "test_doc_id"}
        mock_service.documents().create.return_value.execute.return_value = (
            mock_created_doc
        )
        mock_service.documents().batchUpdate.return_value.execute.return_value = None

        # 同じ言語が複数あるカウンター
        language_frequency = Counter(["en", "en", "ja"])

        create_google_docs(
            problem_id="A",
            initial_content="",
            lang="en",
            language_count=1,  # 1番目のen
            language_frequency=language_frequency,
        )

        # タイトルにカウントが付くことを確認（同じ言語が複数ある場合）
        mock_service.documents().create.assert_called_once_with(body={"title": "A1_en"})

    @patch("statements_manager.src.setup_problem.get_oauth_token")
    def test_auth_failure(self, mock_get_oauth_token):
        """認証に失敗した場合のテスト"""
        mock_get_oauth_token.return_value = None

        with pytest.raises(RuntimeError, match="Failed to get OAuth token"):
            create_google_docs(
                problem_id="A",
                initial_content="",
                lang="en",
                language_count=1,
                language_frequency=Counter(["en"]),
            )

    @patch("statements_manager.src.setup_problem.get_oauth_token")
    @patch("statements_manager.src.setup_problem.build")
    def test_api_error(self, mock_build, mock_get_oauth_token):
        """API呼び出しでエラーが発生した場合のテスト"""
        mock_token = Mock()
        mock_get_oauth_token.return_value = mock_token

        mock_service = Mock()
        mock_build.return_value = mock_service

        # API呼び出しでエラーを発生させる
        mock_service.documents().create.return_value.execute.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(Exception, match="API Error"):
            create_google_docs(
                problem_id="A",
                initial_content="",
                lang="en",
                language_count=1,
                language_frequency=Counter(["en"]),
            )


class TestCreateLocalStatement:
    """create_local_statement関数のテスト"""

    def test_single_language(self):
        """単一言語の場合のファイルパス生成をテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = pathlib.Path(temp_dir)
            initial_content = "# Test Statement"
            language_frequency = Counter(["en"])

            result = create_local_statement(
                initial_content=initial_content,
                dir_path=dir_path,
                lang="en",
                language_count=1,
                language_frequency=language_frequency,
            )

            # 結果の検証
            assert result == "statement/en/statement.md"

            # ファイルが実際に作成されていることを確認
            expected_file = dir_path / "statement" / "en" / "statement.md"
            assert expected_file.exists()

            # ファイルの内容を確認
            with open(expected_file, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == initial_content

    def test_multiple_languages(self):
        """複数言語がある場合のファイルパス生成をテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = pathlib.Path(temp_dir)
            initial_content = "# Test Statement"
            language_frequency = Counter(["en", "ja"])

            result = create_local_statement(
                initial_content=initial_content,
                dir_path=dir_path,
                lang="en",
                language_count=1,
                language_frequency=language_frequency,
            )

            # 結果の検証
            assert result == "statement/en/statement.md"

            # ファイルが実際に作成されていることを確認
            expected_file = dir_path / "statement" / "en" / "statement.md"
            assert expected_file.exists()

    def test_multiple_same_language(self):
        """同じ言語が複数ある場合のファイルパス生成をテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = pathlib.Path(temp_dir)
            initial_content = "# Test Statement"
            language_frequency = Counter(["en", "en"])  # 同じ言語が2回

            result = create_local_statement(
                initial_content=initial_content,
                dir_path=dir_path,
                lang="en",
                language_count=2,  # 2番目のen
                language_frequency=language_frequency,
            )

            # 結果の検証
            assert result == "statement/en/statement_2.md"

            # ファイルが実際に作成されていることを確認
            expected_file = dir_path / "statement" / "en" / "statement_2.md"
            assert expected_file.exists()

    def test_empty_content(self):
        """空のコンテンツでファイルを作成するテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = pathlib.Path(temp_dir)
            initial_content = ""
            language_frequency = Counter(["en"])

            result = create_local_statement(
                initial_content=initial_content,
                dir_path=dir_path,
                lang="en",
                language_count=1,
                language_frequency=language_frequency,
            )

            # 結果の検証
            assert result == "statement/en/statement.md"

            # ファイルが実際に作成されていることを確認
            expected_file = dir_path / "statement" / "en" / "statement.md"
            assert expected_file.exists()

            # ファイルの内容を確認（空文字列）
            with open(expected_file, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == ""


class TestSetupProblem:
    """setup_problem関数の統合テスト"""

    def test_local_mode_success(self):
        """ローカルモードでの正常なセットアップをテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用の引数を作成
            args = Mock()
            args.working_dir = temp_dir
            args.mode = "local"
            args.id = None
            args.template = None
            args.language = ["en"]

            # テスト実行
            setup_problem(args)

            # 結果の検証
            dir_path = pathlib.Path(temp_dir)

            # problem.tomlが作成されていることを確認
            problem_toml_path = dir_path / "problem.toml"
            assert problem_toml_path.exists()

            # testsディレクトリが作成されていることを確認
            tests_dir = dir_path / "tests"
            assert tests_dir.exists()

            # statementディレクトリとファイルが作成されていることを確認
            statement_file = dir_path / "statement" / "en" / "statement.md"
            assert statement_file.exists()

            # problem.tomlの内容を確認
            import toml

            with open(problem_toml_path, "r", encoding="utf-8") as f:
                config = toml.load(f)

            assert config["id"] == dir_path.name  # ディレクトリ名がIDになる
            assert config["params_path"] == "./tests/constraints.hpp"
            assert len(config["statements"]) == 1
            assert config["statements"][0]["lang"] == "en"
            assert config["statements"][0]["path"] == "statement/en/statement.md"

    def test_with_template(self):
        """テンプレートファイルを使用したセットアップをテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テンプレートファイルを作成
            template_content = "# Template Content\n\nThis is a template."
            template_path = pathlib.Path(temp_dir) / "template.md"
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(template_content)

            # テスト用の引数を作成
            args = Mock()
            args.working_dir = temp_dir
            args.mode = "local"
            args.id = "A"
            args.template = str(template_path)
            args.language = ["en"]

            # テスト実行
            setup_problem(args)

            # 結果の検証
            dir_path = pathlib.Path(temp_dir)
            statement_file = dir_path / "statement" / "en" / "statement.md"

            # テンプレートの内容がコピーされていることを確認
            with open(statement_file, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == template_content

    def test_multiple_languages(self):
        """複数言語でのセットアップをテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用の引数を作成
            args = Mock()
            args.working_dir = temp_dir
            args.mode = "local"
            args.id = "A"
            args.template = None
            args.language = ["en", "ja"]

            # テスト実行
            setup_problem(args)

            # 結果の検証
            dir_path = pathlib.Path(temp_dir)

            # 両方の言語のファイルが作成されていることを確認
            en_file = dir_path / "statement" / "en" / "statement.md"
            ja_file = dir_path / "statement" / "ja" / "statement.md"
            assert en_file.exists()
            assert ja_file.exists()

            # problem.tomlの内容を確認
            import toml

            problem_toml_path = dir_path / "problem.toml"
            with open(problem_toml_path, "r", encoding="utf-8") as f:
                config = toml.load(f)

            assert len(config["statements"]) == 2
            assert config["statements"][0]["lang"] == "en"
            assert config["statements"][1]["lang"] == "ja"

    def test_existing_problem_toml(self):
        """problem.tomlが既に存在する場合のエラーハンドリングをテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 既存のproblem.tomlを作成
            problem_toml_path = pathlib.Path(temp_dir) / "problem.toml"
            with open(problem_toml_path, "w", encoding="utf-8") as f:
                f.write("existing content")

            # テスト用の引数を作成
            args = Mock()
            args.working_dir = temp_dir
            args.mode = "local"
            args.id = None
            args.template = None
            args.language = ["en"]

            # エラーが発生することを確認
            with pytest.raises(
                FileExistsError,
                match=re.escape(
                    f"problem.toml already exists in {pathlib.Path(temp_dir).resolve()}"
                ),
            ):
                setup_problem(args)

    @patch("statements_manager.src.setup_problem.get_login_status")
    def test_docs_mode_not_logged_in(self, mock_get_login_status):
        """Google Docsモードでログインしていない場合のエラーハンドリングをテスト"""
        # ログインしていない状態をモック
        mock_login_status = Mock()
        mock_login_status.is_logged_in = False
        mock_get_login_status.return_value = mock_login_status

        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用の引数を作成
            args = Mock()
            args.working_dir = temp_dir
            args.mode = "docs"
            args.id = None
            args.template = None
            args.language = ["en"]

            # エラーが発生することを確認
            with pytest.raises(RuntimeError, match="Authentication required"):
                setup_problem(args)

    @patch("statements_manager.src.setup_problem.get_login_status")
    @patch("statements_manager.src.setup_problem.create_google_docs")
    def test_docs_mode_success(self, mock_create_google_docs, mock_get_login_status):
        """Google Docsモードでの正常なセットアップをテスト"""
        # ログインしている状態をモック
        mock_login_status = Mock()
        mock_login_status.is_logged_in = True
        mock_get_login_status.return_value = mock_login_status

        # Google Docs作成をモック
        mock_create_google_docs.return_value = "test_doc_id"

        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用の引数を作成
            args = Mock()
            args.working_dir = temp_dir
            args.mode = "docs"
            args.id = "A"
            args.template = None
            args.language = ["en"]

            # テスト実行
            setup_problem(args)

            # 結果の検証
            dir_path = pathlib.Path(temp_dir)
            problem_toml_path = dir_path / "problem.toml"
            assert problem_toml_path.exists()

            # Google Docs作成が呼ばれていることを確認
            mock_create_google_docs.assert_called_once()

            # problem.tomlの内容を確認
            import toml

            with open(problem_toml_path, "r", encoding="utf-8") as f:
                config = toml.load(f)

            assert config["statements"][0]["path"] == "test_doc_id"
