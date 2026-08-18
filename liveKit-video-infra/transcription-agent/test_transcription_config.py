import json
import unittest

from transcription_config import language_from_job_metadata


class TranscriptionConfigTests(unittest.TestCase):
    def test_maps_ui_locale_to_provider_language(self) -> None:
        self.assertEqual(
            language_from_job_metadata(json.dumps({"captionLanguage": "es-ES"})),
            "es",
        )
        self.assertEqual(
            language_from_job_metadata(json.dumps({"captionLanguage": "pt-BR"})),
            "pt",
        )

    def test_rejects_unknown_or_malformed_metadata(self) -> None:
        self.assertEqual(language_from_job_metadata("not-json"), "en")
        self.assertEqual(
            language_from_job_metadata(json.dumps({"captionLanguage": "xx-XX"})),
            "en",
        )
        self.assertEqual(language_from_job_metadata(None), "en")


if __name__ == "__main__":
    unittest.main()
