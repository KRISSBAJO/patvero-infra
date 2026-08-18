import json


DEFAULT_STT_LANGUAGE = "en"

_STT_LANGUAGE_BY_CAPTION_LANGUAGE = {
    "en-US": "en",
    "en-GB": "en",
    "es-ES": "es",
    "fr-FR": "fr",
    "de-DE": "de",
    "pt-BR": "pt",
    "it-IT": "it",
    "nl-NL": "nl",
    "pl-PL": "pl",
    "ar-SA": "ar",
    "hi-IN": "hi",
    "ja-JP": "ja",
    "ko-KR": "ko",
    "zh-CN": "zh",
    "tr-TR": "tr",
    "uk-UA": "uk",
}


def language_from_job_metadata(metadata: str | None) -> str:
    """Return a provider-supported language without trusting dispatch metadata."""
    if not metadata:
        return DEFAULT_STT_LANGUAGE

    try:
        payload = json.loads(metadata)
    except (json.JSONDecodeError, TypeError):
        return DEFAULT_STT_LANGUAGE

    if not isinstance(payload, dict):
        return DEFAULT_STT_LANGUAGE

    caption_language = payload.get("captionLanguage")
    if not isinstance(caption_language, str):
        return DEFAULT_STT_LANGUAGE

    return _STT_LANGUAGE_BY_CAPTION_LANGUAGE.get(
        caption_language,
        DEFAULT_STT_LANGUAGE,
    )
