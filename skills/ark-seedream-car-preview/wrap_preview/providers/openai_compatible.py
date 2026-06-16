from __future__ import annotations

import json
import uuid
import urllib.error
import urllib.request

from ..models import ProviderConfig
from .errors import ProviderConfigurationError, ProviderError


class OpenAICompatibleProvider:
    def __init__(self, config: ProviderConfig):
        self.config = config

    def generate(
        self,
        *,
        prompt: str,
        refs: list[str],
        size: str,
        quality: str,
        response_format: str,
    ) -> dict:
        if not self.config.api_key:
            raise ProviderConfigurationError(f"Missing API key for provider {self.config.name!r}")

        endpoint = f"{self.config.base_url.rstrip('/')}{self.config.endpoint_path}"

        if self.config.content_type == "multipart/form-data":
            return self._post_multipart(endpoint, prompt, refs, size, quality, response_format)
        else:
            return self._post_json(endpoint, prompt, refs, size, quality, response_format)

    def _post_json(
        self,
        url: str,
        prompt: str,
        refs: list[str],
        size: str,
        quality: str,
        response_format: str,
    ) -> dict:
        effective_response_format = self.config.response_format or response_format
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "response_format": effective_response_format,
        }
        if refs:
            if self.config.request_style == "single_image":
                payload["image"] = refs[0]
            elif self.config.request_style == "extra_body":
                extra_body: dict[str, object] = {"image": refs[0]}
                if self.config.watermark:
                    extra_body["watermark"] = True
                payload["extra_body"] = extra_body
            else:
                payload["image"] = refs
                if self.config.watermark:
                    payload["watermark"] = True
        elif self.config.watermark:
            payload["watermark"] = True
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self._send_request(url, body, "application/json")

    def _post_multipart(
        self,
        url: str,
        prompt: str,
        refs: list[str],
        size: str,
        quality: str,
        response_format: str,
    ) -> dict:
        boundary = str(uuid.uuid4())
        lines: list[bytes] = []

        def add_field(name: str, value: str) -> None:
            lines.append(f"--{boundary}".encode())
            lines.append(f'Content-Disposition: form-data; name="{name}"'.encode())
            lines.append(b"")
            lines.append(value.encode("utf-8"))

        add_field("model", self.config.model)
        add_field("prompt", prompt)

        if refs:
            add_field("image", refs[0])

        if self.config.watermark:
            add_field("watermark", "true")

        # size and quality are sent as form fields for the edits endpoint
        if size:
            add_field("size", size)
        if quality:
            add_field("quality", quality)

        add_field("response_format", self.config.response_format or response_format)

        lines.append(f"--{boundary}--".encode())
        lines.append(b"")

        body = b"\r\n".join(lines)
        content_type = f"multipart/form-data; boundary={boundary}"
        return self._send_request(url, body, content_type)

    def _send_request(self, url: str, body: bytes, content_type: str) -> dict:
        headers = {
            "Accept": "application/json",
            "Content-Type": content_type,
        }
        if self.config.auth_scheme == "raw":
            headers["Authorization"] = self.config.api_key
        else:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        req = urllib.request.Request(url, method="POST", headers=headers, data=body)
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace")
            raise ProviderError(f"{self.config.name} image generation failed ({err.code}): {detail}") from err
        except Exception as err:
            raise ProviderError(f"{self.config.name} image generation failed: {err}") from err
