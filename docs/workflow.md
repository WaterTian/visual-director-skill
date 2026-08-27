# 生产工作流与质量门禁 / Production Workflow and Quality Gates

## 中文

### 1. 建立 Visual Brief

```bash
uv run python scripts/validate-brief.py tests/fixtures/hero-brief.json
```

Brief 至少要明确：目标、尺寸、格式、主体、逐字文字、必须出现项、禁止项、构图、材质、参考图角色和验收标准。

这一步只建立可审计的生产契约，不会生图。`references` 中的图片必须标明角色；编辑任务默认将输入图视为唯一视觉权威。

### 2. 选择方向并编译 Prompt

```bash
uv run python scripts/select-template.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/select-cases.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/compile-prompt.py \
  tests/fixtures/hero-brief.json \
  --output work/compiled-prompt.json
```

选择器只使用十七个已验收第一方案例。分数用于缩小范围，不替代人工打开效果图比较。编译器只采用与 Brief 相符的通用结构线索，不复制案例主体、品牌或可见文字。

### 3. 授权生成或 handoff

默认路线不要求付费 API；脚本会准备 provider-neutral handoff，而当前 Codex 任务的内置图片能力或用户明确授权的外部路径负责实际生成。未经当前授权，不应生成或替换任何图片。

需要精确 Hero 画布时：

```bash
uv run python scripts/run-free-exact-pipeline.py \
  tests/fixtures/hero-brief.json \
  --output-dir work/hero-run \
  --project-root . \
  --authorized-by current-user-request
```

第一阶段写出一个透明素材请求。当前 Codex 任务的内置图片能力将原始透明素材保存到请求指定路径后，再用同一入口加 `--material` 恢复。确定性合成负责最终像素和文字，原始素材保持不变。生成图中的文字不是精确文案的来源；精确文案只由确定性排版写入。

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
4. **人工内容与视觉门禁**：逐项检查主体、构图、人体、材质、光线、边缘、文字和品牌边界。
5. **落盘门禁**：视觉复核、独立批准和候选哈希全部匹配。

文件检查通过后仍是 `review_required`。视觉复核必须由审阅者把每个要求写入 `visual-review.json`，再用以下命令合并：

```bash
uv run python scripts/apply-visual-review.py \
  work/qc-report.json work/visual-review.json \
  --output work/qc-reviewed.json
```

只有人工逐项复核通过，QC 才能成为 `qc_passed`；正式落盘还需要独立批准。

### 5. Promotion

```bash
uv run python scripts/promote-asset.py \
  path/to/candidate.png path/to/formal-asset.png \
  work/asset-manifest-reviewed.json work/qc-reviewed.json path/to/approval.json \
  --manifest-output path/to/formal-asset.manifest.json
```

默认不覆盖已存在的正式资产，不删除候选原图，也不使用缩放或压缩掩盖失败。Promotion 成功后还应把正式文件、Prompt 哈希和案例记录同步写入公开白名单；未写入白名单的文件不属于 Gallery。

## English

### 1. Create the Visual Brief

```bash
uv run python scripts/validate-brief.py tests/fixtures/hero-brief.json
```

At minimum, define intent, dimensions, format, subject, verbatim text, required and forbidden content, composition, materials, reference roles, and acceptance criteria.

This step creates an auditable production contract only; it does not generate an image. Every image in `references` must state its role, and an edit treats its supplied input as the sole visual authority by default.

### 2. Select and compile

```bash
uv run python scripts/select-template.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/select-cases.py tests/fixtures/hero-brief.json --top 3
uv run python scripts/compile-prompt.py \
  tests/fixtures/hero-brief.json \
  --output work/compiled-prompt.json
```

The selector uses only seventeen reviewed first-party examples. Scores narrow the decision; they do not replace opening and comparing the images. The compiler adopts only generic structure cues supported by the Brief and does not copy subjects, brands, or visible copy.

### 3. Authorized generation or handoff

The default route does not require a paid API. Scripts prepare a provider-neutral handoff; the current Codex task's built-in image capability or an explicitly authorized external path performs actual generation. Do not generate or replace an image without current authorization.

For an exact Hero canvas:

```bash
uv run python scripts/run-free-exact-pipeline.py \
  tests/fixtures/hero-brief.json \
  --output-dir work/hero-run \
  --project-root . \
  --authorized-by current-user-request
```

The first stage writes one transparent-material request. After the current Codex task's built-in image capability saves the original material at the requested path, resume the same entry point with `--material`. Deterministic composition owns final pixels and typography while preserving the source material. Generated lettering is never the source of exact copy; deterministic layout owns exact text.

### 4. QC and visual review

Quality gates run in order: input, file, human content-and-visual review, then landing. A file-level pass still produces `review_required`. The reviewer records evidence for each requirement in `visual-review.json`, then applies it explicitly:

```bash
uv run python scripts/apply-visual-review.py \
  work/qc-report.json work/visual-review.json \
  --output work/qc-reviewed.json
```

Every human visual check must pass before QC can become `qc_passed`, and formal landing requires a separate approval. After promotion, add the formal file, Prompt hash, and case record to the publication allowlist; an unmanifested file is not a Gallery asset.

### 5. Promotion

Promotion refuses existing destinations by default, preserves the candidate, and verifies hashes. Do not use resizing or compression to disguise a failed candidate.
