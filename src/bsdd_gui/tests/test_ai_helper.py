"""
Tests for the AiHelper module (tool/ai_helper.py).

Covers the pure-Python helpers on AiHelper, AiClassDescription, and
AiPropertyDescription that do not require a live OpenAI connection.
The generate_class_definition method is tested with a mocked client.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from bsdd_gui.tool import AiHelper
from bsdd_gui.tool.ai_helper import AiClassDescription, AiPropertyDescription


# ---------------------------------------------------------------------------
# AiHelper
# ---------------------------------------------------------------------------


class TestAiHelper:
    def test_get_model_returns_string(self):
        assert isinstance(AiHelper.get_model(), str)

    def test_get_model_value(self):
        assert AiHelper.get_model() == "gpt-5-nano"

    def test_get_output_tokens_returns_int(self):
        assert isinstance(AiHelper.get_output_tokens(), int)

    def test_get_output_tokens_positive(self):
        assert AiHelper.get_output_tokens() > 0


# ---------------------------------------------------------------------------
# AiClassDescription — build_class_instructions
# ---------------------------------------------------------------------------


class TestAiClassDescriptionBuildInstructions:
    def test_english_returns_non_empty_string(self):
        result = AiClassDescription.build_class_instructions("English", 3)
        assert isinstance(result, str) and result

    def test_german_returns_non_empty_string(self):
        result = AiClassDescription.build_class_instructions("German", 3)
        assert isinstance(result, str) and result

    def test_sentence_count_embedded_in_english(self):
        result = AiClassDescription.build_class_instructions("English", 7)
        assert "7" in result

    def test_sentence_count_embedded_in_german(self):
        result = AiClassDescription.build_class_instructions("German", 5)
        assert "5" in result

    def test_unsupported_language_raises_value_error(self):
        with pytest.raises(ValueError):
            AiClassDescription.build_class_instructions("French", 3)


# ---------------------------------------------------------------------------
# AiClassDescription — build_user_input
# ---------------------------------------------------------------------------


class TestAiClassDescriptionBuildUserInput:
    def test_json_text_appears_in_output(self):
        json_text = '{"Code": "Wall"}'
        result = AiClassDescription.build_user_input(json_text, "English")
        assert json_text in result

    def test_german_variant_contains_json(self):
        json_text = '{"Code": "Wand"}'
        result = AiClassDescription.build_user_input(json_text, "German")
        assert json_text in result


# ---------------------------------------------------------------------------
# AiClassDescription — generate_class_definition
# ---------------------------------------------------------------------------


class TestAiClassDescriptionGenerate:
    def test_no_api_key_returns_none(self):
        result = AiClassDescription.generate_class_definition('{"Code": "Wall"}', api_key=None)
        assert result is None

    def test_returns_text_from_mock_client(self):
        content = MagicMock()
        content.type = "output_text"
        content.text = "A wall is a structural element."
        item = MagicMock()
        item.content = [content]
        resp = MagicMock()
        resp.output = [item]

        mock_client = MagicMock()
        mock_client.responses.create.return_value = resp

        result = AiClassDescription.generate_class_definition(
            '{"Code": "Wall"}',
            api_key="test-key",
            client=mock_client,
        )
        assert result == "A wall is a structural element."

    def test_api_exception_returns_none(self):
        mock_client = MagicMock()
        mock_client.responses.create.side_effect = Exception("connection error")

        result = AiClassDescription.generate_class_definition(
            '{"Code": "Wall"}',
            api_key="test-key",
            client=mock_client,
        )
        assert result is None

    def test_empty_output_uses_fallback(self):
        resp = MagicMock()
        resp.output = []
        resp.output_text = "fallback text"
        mock_client = MagicMock()
        mock_client.responses.create.return_value = resp

        result = AiClassDescription.generate_class_definition(
            '{"Code": "Wall"}',
            api_key="test-key",
            client=mock_client,
        )
        assert result == "fallback text"


# ---------------------------------------------------------------------------
# AiPropertyDescription — build_class_instructions
# ---------------------------------------------------------------------------


class TestAiPropertyDescriptionBuildInstructions:
    def test_english_returns_non_empty_string(self):
        result = AiPropertyDescription.build_class_instructions("English", 3)
        assert isinstance(result, str) and result

    def test_german_returns_non_empty_string(self):
        result = AiPropertyDescription.build_class_instructions("German", 3)
        assert isinstance(result, str) and result

    def test_unsupported_language_raises_value_error(self):
        with pytest.raises(ValueError):
            AiPropertyDescription.build_class_instructions("Spanish", 3)
