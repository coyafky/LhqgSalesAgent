# Provider API Contracts

Last updated: 2026-06-15 (v4 — xinghu image-to-image is the primary provider)
Source: xinghu gpt-image-2 image-to-image contract: https://xinghuapi.apifox.cn/8703402m0

## Overview

The active workflow is image-to-image. A customer vehicle image is required and must be sent to the provider. Do not call any text-to-image-only endpoint for this skill.

All active providers use the same endpoint and content type for image-to-image generation:

- **Endpoint**: `POST /images/generations`
- **Content-Type**: `application/json`

The only difference is how `image` is structured in the JSON body. The provider chain must place `xinghu_primary` first.

## Provider-by-Provider Contract

### xinghu_primary (gpt-image-2) — primary
- **Provider docs**: `https://xinghuapi.apifox.cn/8703402m0`
- **Base URL**: `https://xinghuapi.com/v1`
- **Endpoint**: `POST /images/generations`
- **Content-Type**: `application/json`
- **`image` format**: Single customer vehicle data URL string inside `extra_body.image` (`extra_body` style)
- **`watermark`**: Inside `extra_body.watermark`, not at payload top level
- **Auth**: Bearer token
- **Watermark**: Yes (configured)
- **Response**: `url`
- **Critical rule**: if `extra_body.image` is absent, the provider may behave like text-to-image. Treat that as a failed configuration.
- **Status**: Primary image-to-image provider for customer car recolor previews

### 4sapi_primary (gpt-image-2)
- **`image` format**: JSON array `["data:...,", "data:..."]` (`refs_array` style)
- **Auth**: Bearer token
- **Watermark**: None
- **Response**: `b64_json`
- **Size constraint**: Width **and** height must both be divisible by 16
- **Status**: ✅ Correct — `refs_array` style works

### xinghu_third (legacy name)
- **`image` format**: Single data URL string inside `extra_body.image` (`extra_body` style)
- **`watermark`**: Inside `extra_body.watermark`, not at payload top level
- **Auth**: Bearer token
- **Watermark**: Yes (configured)
- **Response**: `url` (not b64_json)
- **Size constraint**: On `--size auto` tends to 3:2 or 4:3; custom sizes accepted but may be slightly modified (e.g. request 1824×1000 → output 1693×929)
- **Stability**: Occasional "Remote end closed connection without response" (~10%)
- **Status**: ✅ Fixed — `extra_body` style now correctly sends `image` and `watermark` inside the nested object. Previously sent them at payload top level, which was silently ignored by xinghu, degrading to pure text-to-image.

### apiyi_primary (gpt-image-2-all)
- **`image` format**: JSON array `["data:...,", "data:..."]` (`refs_array` style)
- **Auth**: Bearer token
- **Watermark**: None
- **Response**: `b64_json`
- **Size constraint**: No divisible-by-16 requirement; output may differ slightly from requested size but aspect ratio is preserved within tolerance (e.g. request 1824×1000 → output 1693×929)
- **Status**: ✅ Works with `refs_array` style via `/images/generations` + JSON
- **⚠️ Key management**: apiyi's key MUST be its own valid key (`sk-Nznb...`). Do NOT use 4sapi's key (`sk-Jq8...`) — apiyi returns 401. The `--base-url` fallback path in `config.py` searches for API keys in a specific order (`4S_API_KEY` before `APIYI_API_KEY`), so using `--base-url` with apiyi's URL may accidentally pick up 4sapi's key. Always use the chain path for apiyi.
- **Note on `/images/edits`**: apiyi also exposes `POST /images/edits` with `multipart/form-data`, but this requires an "image2Enterprise" enterprise-group API key. Our tests confirmed it's unnecessary — `/images/generations` + JSON works fine with the regular key.

### relay_backup
- No valid API key (placeholder). Skipped during chain.

## Root Cause of the Feishu apiyi Failure

The user reported that on Feishu, apiyi "clearly did not receive the correct reference image". Investigation found:

1. **Wrong API key was the cause**, not endpoint format. `.env.local` entry for `WRAP_PROVIDER_APIYI_PRIMARY_API_KEY` was using 4sapi's key.
2. apiyi returned 401 for every request. Chain fell through to xinghu, which at that time also had the `extra_body` bug.
3. With both primary and secondary providers failing, xinghu degraded to pure text-to-image, generating a different vehicle from the prompt.

**Both issues were fixed this session**:
- xinghu: `request_style=extra_body` sends `image`/`watermark` in the correct location
- apiyi: Key confirmed as `sk-Nznb...` and verified working

## Architecture (added this session)

`ProviderConfig` gained two new fields:

| Field | Default | Purpose |
|-------|---------|---------|
| `endpoint_path` | `/images/generations` | API path override for future providers |
| `content_type` | `application/json` | Content-Type override for future providers |

`openai_compatible.py` dispatches based on `content_type`:
- `application/json` → `_post_json()` (current flow for all active providers)
- `multipart/form-data` → `_post_multipart()` (retained for future use)
