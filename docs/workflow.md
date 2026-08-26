# 生产工作流与质量门禁 / Production Workflow and Quality Gates

## 中文

### 1. 建立 Visual Brief

```bash
uv run python scripts/validate-brief.py tests/fixtures/hero-brief.json
```

Brief 至少要明确：目标、尺寸、格式、主体、逐字文字、必须出现项、禁止项、构图、材质、参考图角色和验收标准。

### 2. 选择方向并编译 Prompt

```bash
uv run python scripts/select-template.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/select-cases.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/compile-prompt.py \
  tests/fixtures/hero-brief.json \
  --output work/compiled-prompt.json
```

选择器只使用七个已验收第一方案例。分数用于缩小范围，不替代人工打开效果图比较。编译器只采用与 Brief 相符的通用结构线索，不复制案例主体、品牌或可见文字。

### 3. 生成

默认路线不要求付费 API。需要精确 Hero 画布时：

```bash
uv run python scripts/run-free-exact-pipeline.py \
  tests/fixtures/hero-brief.json \
  --output-dir work/hero-run \
  --project-root . \
  --authorized-by current-user-request
```

第一阶段写出一个透明素材请求。当前 Codex 任务的内置图片能力将原始透明素材保存到请求指定路径后，再用同一入口加 `--material` 恢复。确定性合成负责最终像素和文字，原始素材保持不变。

### 4. QC 与视觉复核

```bash
uv run python scripts/inspect-asset.py \
  tests/fixtures/hero-brief.json path/to/candidate.png \
  --output work/qc-report.json
```

门禁顺序：

1. **输入门禁**：需求和参考图角色明确。
2. **文件门禁**：格式、尺寸、比例、透明度和文件可读性正确。
3. **内容门禁**：主体、数量、身份、几何和逐字文字正确，无水印或虚构品牌。
4. **视觉门禁**：构图、人体、材质、光线、边缘、文字和品牌一致性通过近看。
5. **落盘门禁**：视觉复核、独立批准和候选哈希全部匹配。

文件检查通过后仍是 `review_required`。只有人工逐项复核通过，manifest 才能成为 `qc_passed`；正式落盘还需要独立批准。

### 5. Promotion

```bash
uv run python scripts/promote-asset.py \
  path/to/candidate.png path/to/formal-asset.png \
  work/asset-manifest-reviewed.json work/qc-reviewed.json path/to/approval.json \
  --manifest-output path/to/formal-asset.manifest.json
```

默认不覆盖已存在的正式资产，不删除候选原图，也不使用缩放或压缩掩盖失败。

## English

### 1. Create the Visual Brief

```bash
uv run python scripts/validate-brief.py tests/fixtures/hero-brief.json
```

At minimum, define intent, dimensions, format, subject, verbatim text, required and forbidden content, composition, materials, reference roles, and acceptance criteria.

### 2. Select and compile

```bash
uv run python scripts/select-template.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/select-cases.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/compile-prompt.py \
  tests/fixtures/hero-brief.json \
  --output work/compiled-prompt.json
```

The selector uses only seven reviewed first-party examples. Scores narrow the decision; they do not replace opening and comparing the images. The compiler adopts only generic structure cues supported by the Brief and does not copy subjects, brands, or visible copy.

### 3. Generate

The default route does not require a paid API. For an exact Hero canvas:

```bash
uv run python scripts/run-free-exact-pipeline.py \
  tests/fixtures/hero-brief.json \
  --output-dir work/hero-run \
  --project-root . \
  --authorized-by current-user-request
```

The first stage writes one transparent-material request. After the current Codex task's built-in image capability saves the original material at the requested path, resume the same entry point with `--material`. Deterministic composition owns final pixels and typography while preserving the source material.

### 4. QC and visual review

Quality gates run in order: input, file, content, visual, then landing. A file-level pass still produces `review_required`. Every human visual check must pass before the manifest can become `qc_passed`, and formal landing requires a separate approval.

### 5. Promotion

Promotion refuses existing destinations by default, preserves the candidate, and verifies hashes. Do not use resizing or compression to disguise a failed candidate.
