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
        self.api_key = api_key.strip()
        self.app_id = app_id.strip()
        self.base_url = "https://fanyi-api.baidu.com/ait/api/aiTextTranslate"

    def detect_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters."""
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df]')
        return bool(chinese_pattern.search(text))

    def detect_non_english(self, text: str) -> bool:
        """Check if text contains non-English characters that need translation."""
        # Same detection logic as before
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df]')
        return bool(chinese_pattern.search(text))

    def translate(self, text: str, target_lang: str) -> tuple[str, dict]:
        """Translate text to target language using Baidu AI Text Translate API.

        Args:
            text: Text to translate
            target_lang: Target language ('English' or 'Chinese')

        Returns:
            Tuple of (Translated text, Usage dict or None)
        """
        # Detect languages
        from_lang = 'auto'
        if target_lang.lower() == 'chinese':
            to_lang = 'zh'
        else:
            to_lang = 'en'

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "appid": self.app_id,
            "from": from_lang,
            "to": to_lang,
            "q": text
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Handle errors
            if "error_code" in result and result["error_code"] != 0:
                 # Note: Success usually implies no error_code or error_code=0, but check docs if available.
                 # The failure case had error_code: 54001.
                 # The success case had no error_code in my debug output? 
                 # Wait, looking at debug output: {"from":"zh","to":"en","trans_result":[{"src":"你好","dst":"Hello"}]}
                 # It doesn't have error_code on success.
                raise Exception(f"Baidu API error: {result['error_code']} - {result.get('error_msg')}")

            # Extract result
            trans_result = result.get("trans_result", [])
            translated_lines = [item["dst"] for item in trans_result]
            
            return "\n".join(translated_lines), None

        except requests.exceptions.RequestException as e:
            raise Exception(f"Baidu Translation API error: {e}")
        except (KeyError, IndexError, ValueError) as e:
            raise Exception(f"Invalid Baidu API response: {e}")
