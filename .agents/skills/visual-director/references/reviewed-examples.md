# Reviewed Examples / 已验收案例

Use this reference when a nearby visual example would improve template or composition choice. / 当相近效果图有助于选择模板或构图时使用本说明。

- `data/templates.json` contains the reviewed first-party template summaries. / 保存已验收第一方模板摘要。
- `data/cases.json` maps each reviewed example to a local Prompt and Gallery image. / 将每个案例映射到本地 Prompt 与效果图。
- `gallery/gallery-manifest.json` is the publication allowlist with image and Prompt hashes. / 是包含图片与 Prompt 哈希的发布白名单。

Run:

```bash
uv run python scripts/search-cases.py --id 1 --full-prompt
uv run python scripts/search-cases.py --id 4 --full-prompt
uv run python scripts/search-cases.py --id 5 --full-prompt
uv run python scripts/search-cases.py --id 6 --full-prompt
uv run python scripts/search-cases.py --id 7 --full-prompt
uv run python scripts/search-cases.py --id 8 --full-prompt
uv run python scripts/search-cases.py --id 9 --full-prompt
uv run python scripts/search-cases.py --id 10 --full-prompt
uv run python scripts/search-cases.py --id 11 --full-prompt
uv run python scripts/select-cases.py examples/hero-brief.json --top 3
```

The selector uses local text and metadata only. Open the returned image paths and visually reject incompatible examples before generation. The compiler may adopt generic composition, camera, lighting, material, typography, and style cues that also occur in the Brief. It must not copy the example subject, identity, brand, logo, visible text, or watermark. / 选择器只使用本地文字与元数据；生图前必须打开返回图片人工比较。编译器只能采用 Brief 同样需要的通用构图、相机、光线、材质、字体和风格线索，不得复制案例主体、身份、品牌、logo、可见文字或水印。

When the reviewed example belonging to the selected template is within ten score points of the strongest generic match, it is placed first so the selected workflow remains directly inspectable; lower-quality examples are not promoted. / 当所选模板自己的已验收案例与最高通用匹配的分差不超过十分时，它会被排在首位，以便直接检查该工作流；质量较低的案例不会被强行提升。

The plugin runtime may omit gallery raster images to keep installation lean. In that environment, use the prompt metadata for selection and inspect images from the checked-out public repository when visual comparison is required. / 为减小安装包，Plugin 运行时可以不含 Gallery 栅格图；需要视觉比较时应查看已检出的公开仓库图片。
