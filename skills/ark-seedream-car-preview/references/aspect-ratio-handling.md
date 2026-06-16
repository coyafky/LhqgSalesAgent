# Aspect Ratio Handling — Provider Quirks & Dimension Calculation

Recorded: 2026-06-12  
Source: Session generating B-110 (灰蒙绿) on customer car image (270×148 JPEG)

## The Problem

`wrap_preview/dimensions.py` line 48–55 enforces:

```python
def aspect_ratio_matches(actual, target, tolerance=0.01):
    return abs(aspect_ratio(actual) - aspect_ratio(target)) <= tolerance
```

If the generated image's width/height ratio deviates from the input vehicle image's ratio by more than 0.01, `gen.py` raises `RuntimeError` and refuses to send the result. This is the single most common failure mode when `--size auto` delegates aspect ratio to the model.

## Detection

Before any generation, get the car image dimensions:

```bash
identify /path/to/customer-car.jpg
# or
python3 -c "from PIL import Image; img = Image.open('/path/to/customer-car.jpg'); print(f'{img.size[0]}x{img.size[1]}')"
```

Calculate target ratio: `width / height` (float).

## Dimension Calculation Strategy

When `--size auto` or the default chain fails with the "aspect ratio does not match" error:

1. **Goal**: find `W` and `H` (both positive integers) such that `|W/H - target_ratio| ≤ 0.01`.
2. **Preferred**: pick from sizes the provider supports (will typically be ≥ 1024 on each side for gpt-image-2 models).
3. **Provider constraint**: some providers (e.g. 4sapi_primary) require both W and H divisible by 16. Others (e.g. apiyi_primary) don't care but may output slightly different dimensions — as long as the output ratio still passes the 0.01 check, it's fine.

### Worked example: 270×148 input

| Target ratio | 270 ÷ 148 = **1.824324...** |
|---|---|

Candidate explicit sizes:

| W      | H     | W÷H        | δ         | Divisible by 16? | Works on |
|--------|-------|------------|-----------|-------------------|----------|
| 1824   | 1000  | 1.8240     | 0.0003 ✅ | W✅ H❌           | apiyi    |
| 1808   | 992   | 1.8226     | 0.0017 ✅ | W✅ H✅           | apiyi, 4sapi |
| 1840   | 1008  | 1.8254     | 0.0011 ✅ | W✅ H✅           | apiyi, 4sapi |
| auto   | auto  | (varies)   | often ❌ | —                 | unreliable |

## Provider Quirks

### 4sapi_primary (`gpt-image-2`)
- **Constraint**: `Invalid size 'WxH' — Width and height must both be divisible by 16.`
- **Auth**: bearer token
- **Response format**: b64_json (preferred)
- **Watermark**: false
- **Behavior**: strict about input dimensions but honors `--size` exactly.

### apiyi_primary (`gpt-image-2-all`)
- **Endpoint**: `/images/edits` (auto-detected, `multipart/form-data`)
- **Constraint**: No divisible-by-16 requirement.
- **Auth**: bearer token
- **Response format**: b64_json
- **Watermark**: false
- **Behavior**: May output slightly different dimensions than requested (e.g. requested 1824×1000, output 1693×929 — ratio 1.8224 vs target 1.8243, δ=0.0019 ✅). The ratio must still pass the 0.01 tolerance check against the *input vehicle image*, not against what was requested.

### xinghu_third (`gpt-image-2`)
- **Constraint**: Returns `url` format, has watermark overlay.
- **Request style**: `extra_body` — `image` 和 `watermark` 放在 JSON 的 `extra_body` 对象内，不在顶层。
- **`image` 格式**: 单个字符串（base64 data URL 或网络 URL），不是数组。
- **Response format**: url (not b64_json — scripts handle this but URL download may be fragile).
- **Watermark**: true — avoid if possible; watermark degrades customer-facing preview.
- **Transient failure**: 偶发 "Remote end closed connection without response"（~10% 请求）。provider chain 会自动回退到下一顺位，不需要额外处理。
- **Behavior with custom sizes**: When given a non-standard size (e.g. 1824×1000), may succeed or fail intermittently. On success, outputs dimensions close to the request (e.g. 1693×929 matching the 1.8243 input ratio within tolerance). On failure, falls through to the next provider in chain.

### relay_backup (example.com)
- **Has API key**: false — currently unusable. Skipped during chain.

## Procedure When `--size auto` Fails

1. Check the output error for the actual generated dimensions vs expected ratio.
2. Run `identify` on the input image to confirm dimensions.
3. If the model output a different aspect ratio, calculate matching dimensions as above.
4. Retry with `--size WxH` using a provider that supports the chosen dimensions.
5. If the 4sapi provider fails due to divisibility, fall through to apiyi or use the divisible-by-16 candidate from the table.

## Pitfall: Don't send failed output

The `dimensions.py` check exists for a reason — a 4:3 generated image on a 16:9 input car photo will look stretched or cropped. Always verify the output passes the check, and never manually bypass the `RuntimeError` guard.

## Related

- `wrap_preview/dimensions.py` — the tolerance and check logic
- `gen.py` — calls `assert_output_aspect_ratios()` after generation
- SKILL.md → `## 比例处理（aspect ratio matching）`
