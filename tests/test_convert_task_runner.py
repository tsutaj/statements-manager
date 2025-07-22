from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from statements_manager.src.convert_task_runner import ContentsStatus, ConvertTaskRunner
from statements_manager.src.execute_config import (
    ProblemConfig,
    ProblemSetConfig,
    StatementConfig,
)
from statements_manager.src.statement_location_mode import StatementLocationMode


class TestDocsContentsSuggestions:
    """Google Docs提案の取り扱いをテスト"""

    @pytest.fixture
    def mock_problemset_config(self):
        """テスト用のProblemSetConfigをモック"""
        config = MagicMock(spec=ProblemSetConfig)
        config.encoding = "utf-8"

        # ProblemConfigのモック
        problem_config = MagicMock(spec=ProblemConfig)
        statement_config = MagicMock(spec=StatementConfig)
        statement_config.path = "test_document_id"
        statement_config.mode = StatementLocationMode.DOCS
        problem_config.statement = statement_config

        config.get_problem.return_value = problem_config
        return config

    def create_mock_document(self, elements):
        """Google Docs document構造を作成"""
        return {"body": {"content": [{"paragraph": {"elements": elements}}]}}

    def normal_element(self, text):
        """通常のテキスト要素"""
        return {"textRun": {"content": text}}

    def insertion_element(self, text):
        """挿入提案付きの要素"""
        return {"textRun": {"content": text, "suggestedInsertionIds": ["suggestion-1"]}}

    def deletion_element(self, text):
        """削除提案付きの要素"""
        return {"textRun": {"content": text, "suggestedDeletionIds": ["suggestion-1"]}}

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_no_suggestions(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """提案なし: 正常に処理される"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # 提案なしのdocument
        mock_document = self.create_mock_document(
            [self.normal_element("Normal text without suggestions")]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # ConvertTaskRunnerを初期化
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = False

        # 正常に処理されることを確認
        status, content = runner.get_docs_contents("test_problem")
        assert status == ContentsStatus.OK
        assert content == "Normal text without suggestions"

        # 警告やエラーログがないことを確認
        assert "proposed element" not in caplog.text

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_insertion_suggestions_without_fail_flag(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """insertion提案ありで--fail-on-suggestionsなし: 警告のみ"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # insertion提案ありのdocument
        mock_document = self.create_mock_document(
            [
                self.normal_element("Normal text"),
                self.insertion_element("Suggested insertion"),
            ]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # ConvertTaskRunnerを初期化（fail_on_suggestions=False）
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = False

        # 正常に処理されることを確認
        status, content = runner.get_docs_contents("test_problem")
        assert status == ContentsStatus.OK
        assert content == "Normal text"  # 提案された部分は除外される

        # 警告ログが出力されることを確認
        assert (
            "proposed element for addition (ignored in rendering): Suggested insertion"
            in caplog.text
        )
        assert "ERROR" not in caplog.text

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_deletion_suggestions_without_fail_flag(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """deletion提案ありで--fail-on-suggestionsなし: 警告のみ"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # deletion提案ありのdocument
        mock_document = self.create_mock_document(
            [
                self.normal_element("Normal text"),
                self.deletion_element("Text to delete"),
            ]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # ConvertTaskRunnerを初期化（fail_on_suggestions=False）
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = False

        # 正常に処理されることを確認
        status, content = runner.get_docs_contents("test_problem")
        assert status == ContentsStatus.OK
        assert content == "Normal textText to delete"  # deletion提案は内容を含む

        # 警告ログが出力されることを確認
        assert "proposed element for deletion: Text to delete" in caplog.text
        assert "ERROR" not in caplog.text

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_insertion_suggestions_with_fail_flag(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """insertion提案ありで--fail-on-suggestions: エラー"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # insertion提案ありのdocument
        mock_document = self.create_mock_document(
            [
                self.normal_element("Normal text"),
                self.insertion_element("Suggested insertion"),
            ]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # ConvertTaskRunnerを初期化（fail_on_suggestions=True）
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = True

        # エラーが発生することを確認
        with pytest.raises(
            ValueError, match="Unresolved suggestions found in Google Docs"
        ):
            runner.get_docs_contents("test_problem")

        # エラーログが出力されることを確認
        assert (
            "proposed element for addition (failed due to --fail-on-suggestions): "
            "Suggested insertion" in caplog.text
        )
        assert "Failed: unresolved suggestions found in Google Docs" in caplog.text

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_deletion_suggestions_with_fail_flag(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """deletion提案ありで--fail-on-suggestions: エラー"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # deletion提案ありのdocument
        mock_document = self.create_mock_document(
            [
                self.normal_element("Normal text"),
                self.deletion_element("Text to delete"),
            ]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # ConvertTaskRunnerを初期化（fail_on_suggestions=True）
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = True

        # エラーが発生することを確認
        with pytest.raises(
            ValueError, match="Unresolved suggestions found in Google Docs"
        ):
            runner.get_docs_contents("test_problem")

        # エラーログが出力されることを確認
        assert (
            "proposed element for deletion (failed due to --fail-on-suggestions): Text to delete"
            in caplog.text
        )
        assert "Failed: unresolved suggestions found in Google Docs" in caplog.text

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_both_suggestions_with_fail_flag(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """両方の提案ありで--fail-on-suggestions: エラー"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # 両方の提案ありのdocument
        mock_document = self.create_mock_document(
            [
                self.normal_element("Normal text"),
                self.insertion_element("Suggested insertion"),
                self.deletion_element("Text to delete"),
            ]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # ConvertTaskRunnerを初期化（fail_on_suggestions=True）
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = True

        # エラーが発生することを確認
        with pytest.raises(
            ValueError, match="Unresolved suggestions found in Google Docs"
        ):
            runner.get_docs_contents("test_problem")

        # 両方のエラーログが出力されることを確認
        assert (
            "proposed element for addition (failed due to --fail-on-suggestions): "
            "Suggested insertion" in caplog.text
        )
        assert (
            "proposed element for deletion (failed due to --fail-on-suggestions): Text to delete"
            in caplog.text
        )
        assert "Failed: unresolved suggestions found in Google Docs" in caplog.text

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_no_suggestions_with_fail_flag_enabled(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """提案なしで--fail-on-suggestions有効: 正常に処理される"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # 提案なしのdocument
        mock_document = self.create_mock_document(
            [self.normal_element("Normal text without suggestions")]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # ConvertTaskRunnerを初期化（fail_on_suggestions=True）
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = True

        # 正常に処理されることを確認（エラーにならない）
        status, content = runner.get_docs_contents("test_problem")
        assert status == ContentsStatus.OK
        assert content == "Normal text without suggestions"

        # エラーログがないことを確認
        assert "Failed: unresolved suggestions found in Google Docs" not in caplog.text

    @patch("statements_manager.src.convert_task_runner.build")
    @patch("statements_manager.src.utils.create_token")
    def test_complex_document_with_mixed_suggestions(
        self, mock_token, mock_build, mock_problemset_config, caplog
    ):
        """複雑なドキュメント（通常テキスト + 各種提案）での動作確認"""
        # Mock setup
        mock_token.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # 複雑なdocument
        mock_document = self.create_mock_document(
            [
                self.normal_element("Start of document"),
                self.insertion_element("First suggestion"),
                self.normal_element(" middle text "),
                self.deletion_element("text to remove"),
                self.normal_element(" end of document"),
            ]
        )
        mock_service.documents().get().execute.return_value = mock_document

        # fail_on_suggestions=Falseでテスト
        runner = ConvertTaskRunner(mock_problemset_config)
        runner.fail_on_suggestions = False

        status, content = runner.get_docs_contents("test_problem")
        assert status == ContentsStatus.OK
        # insertion提案は除外され、deletion提案のテキストは含まれる
        assert content == "Start of document middle text text to remove end of document"

        # 警告ログが出力されることを確認
        assert (
            "proposed element for addition (ignored in rendering): First suggestion"
            in caplog.text
        )
        assert "proposed element for deletion: text to remove" in caplog.text
