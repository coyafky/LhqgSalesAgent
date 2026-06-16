import tempfile
import unittest
from pathlib import Path

from wrap_preview.models import ProviderConfig, WrapPreviewRequest
from wrap_preview.service import generate_wrap_preview


class StubProvider:
    calls = []

    def __init__(self, config):
        self.config = config

    def generate(self, **kwargs):
        StubProvider.calls.append(self.config.name)
        return {"data": [{"url": f"https://example.com/{self.config.name}.png"}]}


class ServiceFallbackTests(unittest.TestCase):
    def test_service_falls_back_when_provider_output_is_unusable(self):
        import wrap_preview.service as service_module

        original_provider = service_module.OpenAICompatibleProvider
        original_load_configs = service_module.load_provider_configs
        original_save = service_module.save_generated_images
        original_assert = service_module.assert_output_aspect_ratios

        def fake_load_configs(**kwargs):
            return [
                ProviderConfig(name="bad", base_url="https://bad.example/v1", api_key="x"),
                ProviderConfig(name="good", base_url="https://good.example/v1", api_key="x"),
            ]

        save_calls = []

        def fake_save(response, out_dir):
            save_calls.append(response["data"][0]["url"])
            if len(save_calls) == 1:
                raise RuntimeError("download failed")
            out_dir.mkdir(parents=True, exist_ok=True)
            image = out_dir / "image-1.png"
            image.write_bytes(b"image")
            return [image], [], 0

        service_module.OpenAICompatibleProvider = StubProvider
        service_module.load_provider_configs = fake_load_configs
        service_module.save_generated_images = fake_save
        service_module.assert_output_aspect_ratios = lambda files, target: [(300, 168)]
        self.addCleanup(setattr, service_module, "OpenAICompatibleProvider", original_provider)
        self.addCleanup(setattr, service_module, "load_provider_configs", original_load_configs)
        self.addCleanup(setattr, service_module, "save_generated_images", original_save)
        self.addCleanup(setattr, service_module, "assert_output_aspect_ratios", original_assert)

        StubProvider.calls = []
        with tempfile.TemporaryDirectory() as tmp:
            result = generate_wrap_preview(
                WrapPreviewRequest(
                    vehicle_refs=["https://example.com/car.jpg"],
                    color_refs=["https://example.com/swatch.png"],
                    out_dir=Path(tmp),
                )
            )

        self.assertEqual(StubProvider.calls, ["bad", "good"])
        self.assertEqual(result["provider"], "good")
        self.assertEqual([attempt["ok"] for attempt in result["provider_attempts"]], [False, True])
        self.assertIn("download failed", result["provider_attempts"][0]["error"])


if __name__ == "__main__":
    unittest.main()
