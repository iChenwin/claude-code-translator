"""Qianwen API client for translation using OpenAI-compatible API."""

import re
import requests
import json


class QianwenClient:
    """Client for Qianwen API translation services."""

    def __init__(self, base_url: str, api_key: str, model: str):
        """Initialize the Qianwen client.

        Args:
            base_url: API base URL
            api_key: API authentication key
            model: Model name to use for translation
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model

    def detect_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters.

        Args:
            text: Text to check

        Returns:
            True if text contains Chinese characters
        """
        # Unicode ranges for Chinese characters
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
        # (more than 2 characters to avoid false positives from symbols)
        return len(matches) > 2

    def translate(self, text: str, target_lang: str) -> str:
        """Translate text to target language using Qianwen API.

        Args:
            text: Text to translate
            target_lang: Target language ('English' or 'Chinese')

        Returns:
            Translated text

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        system_prompt = f"""You are a professional translator. Translate the following text to {target_lang}.
Rules:
1. Only output the translated text, no explanations
2. Preserve code blocks, file paths, and technical terms as-is
3. Maintain the original formatting and structure
4. If the text is already in {target_lang}, return it unchanged"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            usage = result.get("usage", {})
            return result["choices"][0]["message"]["content"].strip(), usage
        except requests.exceptions.RequestException as e:
            raise Exception(f"Translation API error: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid API response format: {e}")
