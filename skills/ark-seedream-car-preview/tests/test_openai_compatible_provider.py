import json
import unittest

from wrap_preview.models import ProviderConfig
from wrap_preview.providers.openai_compatible import OpenAICompatibleProvider


class RecordingProvider(OpenAICompatibleProvider):
    def __init__(self, config):
        super().__init__(config)
        self.last_url = ""
        self.last_payload = {}
        self.last_multipart_body = b""
        self.last_content_type = ""

    def _send_request(self, url, body, content_type):
        self.last_url = url
        self.last_content_type = content_type
        if content_type.startswith("application/json"):
            self.last_payload = json.loads(body.decode("utf-8"))
        else:
            self.last_multipart_body = body
        return {"data": [{"url": "https://example.com/image.png"}]}


class OpenAICompatibleProviderTests(unittest.TestCase):
    def test_json_generations_endpoint_default(self):
        """default config sends JSON to /images/generations"""
        provider = RecordingProvider(
            ProviderConfig(name="test", base_url="https://api.example.com/v1", api_key="key")
        )
        provider.generate(
            prompt="p", refs=["img1"], size="auto", quality="high", response_format="b64_json"
        )
        self.assertIn("/images/generations", provider.last_url)
        self.assertEqual(provider.last_payload["prompt"], "p")
        self.assertEqual(provider.last_payload["image"], ["img1"])

    def test_edits_multipart_endpoint_for_apiyi(self):
        """multipart fallback still targets configured edits endpoint"""
        provider = RecordingProvider(
            ProviderConfig(
                name="apiyi_primary",
                base_url="https://api.apiyi.com/v1",
                api_key="key",
                endpoint_path="/images/edits",
                content_type="multipart/form-data",
            )
        )
        provider.generate(
            prompt="p", refs=["vehicle-ref", "swatch-ref"], size="1024x1024", quality="high", response_format="url"
        )
        self.assertIn("/images/edits", provider.last_url)
        self.assertIn("multipart/form-data", provider.last_content_type)

    def test_refs_array_with_watermark(self):
        provider = RecordingProvider(
            ProviderConfig(
                name="test",
                base_url="https://api.example.com/v1",
                api_key="key",
                request_style="refs_array",
                watermark=True,
            )
        )
        provider.generate(
            prompt="p", refs=["img1"], size="1024x1024", quality="high", response_format="url"
        )
        self.assertEqual(provider.last_url, "https://api.example.com/v1/images/generations")
        self.assertEqual(provider.last_payload["prompt"], "p")
        self.assertEqual(provider.last_payload["image"], ["img1"])
        self.assertTrue(provider.last_payload["watermark"])

    def test_extra_body_request_style(self):
        provider = RecordingProvider(
            ProviderConfig(
                name="xinghu_primary",
                base_url="https://xinghuapi.com/v1",
                api_key="key",
                request_style="extra_body",
                watermark=True,
                response_format="url",
            )
        )
        provider.generate(
            prompt="p", refs=["vehicle-ref", "swatch-ref"], size="1024x1024", quality="high", response_format="b64_json"
        )
        self.assertEqual(provider.last_url, "https://xinghuapi.com/v1/images/generations")
        self.assertNotIn("image", provider.last_payload)
        self.assertEqual(provider.last_payload["extra_body"]["image"], "vehicle-ref")
        self.assertTrue(provider.last_payload["extra_body"]["watermark"])
        self.assertEqual(provider.last_payload["response_format"], "url")


if __name__ == "__main__":
    unittest.main()
