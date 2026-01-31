"""Baidu AI Text Translation API client."""

import re
import requests


class BaiduClient:
    """Client for Baidu AI Text Translation services."""

    def __init__(self, api_key: str, app_id: str):
        """Initialize the Baidu client.

        Args:
            api_key: API authentication key (Bearer token)
            app_id: App ID for the translation service
        """
        self.api_key = api_key
        self.app_id = app_id
        self.base_url = "https://fanyi-api.baidu.com/ait/api/aiTextTranslate"

    def detect_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters.

        Args:
            text: Text to check

        Returns:
            True if text contains Chinese characters
        """
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df]')
        return bool(chinese_pattern.search(text))

    def detect_non_english(self, text: str) -> bool:
        """Check if text contains non-English characters that need translation.

        Detects: Chinese, Japanese, Korean, Russian, Arabic, Thai, Vietnamese,
        and other non-Latin scripts.

        Args:
            text: Text to check

        Returns:
            True if text contains significant non-English content
        """
        # Remove code blocks, URLs, file paths to avoid false positives
        clean_text = re.sub(r'```[\s\S]*?```', '', text)  # code blocks
        clean_text = re.sub(r'`[^`]+`', '', clean_text)    # inline code
        clean_text = re.sub(r'https?://\S+', '', clean_text)  # URLs
        clean_text = re.sub(r'[A-Za-z]:\\[\w\\/.]+', '', clean_text)  # Windows paths
        clean_text = re.sub(r'/[\w/.-]+', '', clean_text)  # Unix paths

        # Unicode ranges for various non-English scripts
        non_english_patterns = [
            r'[\u4e00-\u9fff]',          # Chinese (CJK Unified)
            r'[\u3400-\u4dbf]',          # Chinese (CJK Extension A)
            r'[\u3040-\u309f]',          # Japanese Hiragana
            r'[\u30a0-\u30ff]',          # Japanese Katakana
            r'[\uac00-\ud7af]',          # Korean Hangul
            r'[\u0400-\u04ff]',          # Cyrillic (Russian, etc.)
            r'[\u0600-\u06ff]',          # Arabic
            r'[\u0e00-\u0e7f]',          # Thai
            r'[\u1e00-\u1eff]',          # Vietnamese (Latin Extended)
            r'[\u0370-\u03ff]',          # Greek
            r'[\u0590-\u05ff]',          # Hebrew
            r'[\u0900-\u097f]',          # Hindi (Devanagari)
            r'[\u0980-\u09ff]',          # Bengali
            r'[\u0c00-\u0c7f]',          # Telugu
            r'[\u0b80-\u0bff]',          # Tamil
        ]

        combined_pattern = '|'.join(non_english_patterns)
        matches = re.findall(combined_pattern, clean_text)

        # Consider it non-English if there are significant non-English characters
        return len(matches) > 2

    def _get_lang_code(self, lang: str) -> str:
        """Convert language name to Baidu API language code.

        Args:
            lang: Language name (e.g., 'English', 'Chinese')

        Returns:
            Baidu API language code
        """
        lang_map = {
            'english': 'en',
            'chinese': 'zh',
            'japanese': 'ja',
            'korean': 'ko',
            'russian': 'ru',
            'arabic': 'ar',
            'thai': 'th',
            'vietnamese': 'vi',
            'french': 'fr',
            'german': 'de',
            'spanish': 'es',
            'portuguese': 'pt',
            'italian': 'it',
        }
        return lang_map.get(lang.lower(), 'en')

    def translate(self, text: str, target_lang: str) -> str:
        """Translate text to target language using Baidu AI Translation API.

        Args:
            text: Text to translate
            target_lang: Target language ('English' or 'Chinese')

        Returns:
            Translated text

        Raises:
            Exception: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Detect source language
        if self.detect_chinese(text):
            from_lang = "zh"
        else:
            from_lang = "auto"

        to_lang = self._get_lang_code(target_lang)

        payload = {
            "appid": self.app_id,
            "from": from_lang,
            "to": to_lang,
            "q": text,
            "model_type": "llm"
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # Handle Baidu API response format
            # Some errors return "code" and "msg"
            code = result.get("code")
            if code is not None and code != 0:
                error_msg = result.get("msg", "Unknown error")
                raise Exception(f"Baidu API error: {error_msg}")

            # Extract translated text from response
            # Format 1: {"trans_result": [...], "from": "...", "to": "..."}
            # Format 2: {"data": {"trans_result": [...]}}
            trans_result = result.get("trans_result")
            if not trans_result:
                data = result.get("data", {})
                trans_result = data.get("trans_result")

            if not trans_result:
                raise Exception("No translation result returned")

            # Combine all translated segments
            translated_parts = [item.get("dst", "") for item in trans_result]
            return "\n".join(translated_parts)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Baidu Translation API error: {e}")
        except (KeyError, IndexError, TypeError) as e:
            raise Exception(f"Invalid Baidu API response format: {e}")
