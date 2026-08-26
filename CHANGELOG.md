# Changelog / 变更记录

This project follows semantic versioning. / 本项目遵循语义化版本号。

## 0.5.0 - 2026-08-26

Adds a reviewed, grounded realistic-motion editorial workflow. / 新增已验收的可信写实动态编辑摄影工作流。

### Added / 新增

- `realistic-motion-editorial` template with one fictional adult, visible full body, a physically credible planted-foot motion, modest unbranded workwear, rain-wet urban material, and natural mixed light. / 新增 `realistic-motion-editorial` 模板，包含一位虚构成年主体、完整可见全身、可信的落地动作、端庄无品牌工作服、雨后城市材质和自然混合光。
- Character routing for motion editorial, full-body movement, dancer photography, and grounded-action requests. / 新增针对动态编辑、全身动态、舞者摄影和可信动作请求的人物路由。
- Final prompt, approved vertical image, SHA-256 records, bilingual review, selector fixture, and ranking coverage. / 新增最终 Prompt、批准的竖幅效果图、SHA-256、中英文复核、选择器夹具和排序覆盖。

### Quality boundary / 质量边界

- The public result uses no reference image, no real-person likeness, no paid API, no visible brand, no text, and no sports-advertising or superhero treatment. / 公开结果不使用参考图、真人相似性、付费 API、可见品牌或文字，也不采用体育广告化或英雄式表达。

## 0.4.0 - 2026-08-26

Adds a reviewed quiet, non-sexualized editorial-portrait workflow. / 新增已验收的静谧、非性感化编辑人像工作流。

### Added / 新增

- `quiet-editorial-portrait` template with a fictional adult subject, modest layered wardrobe, natural seated body language, muted interior, soft side light, and 9:16 negative space. / 新增 `quiet-editorial-portrait` 模板，包含虚构成年主体、端庄叠穿、自然坐姿、低饱和室内、柔侧光和 9:16 留白。
- Character routing for quiet editorial, interior portrait, seated portrait, and natural-light portrait requests. / 新增针对静谧编辑、室内人像、坐姿人像和自然光人像请求的人物路由。
- Final prompt, approved 9:16 image, SHA-256 records, bilingual review, and fixture coverage. / 新增最终 Prompt、批准的 9:16 效果图、SHA-256、中英文复核和测试夹具。

### Quality boundary / 质量边界

- The public result uses a clearly adult fictional identity and excludes real-person references, childlike appearance, sexualized styling, copied identity, brands, visible text, and paid APIs. / 公开结果使用明确的虚构成年身份，排除真人参考、幼态外观、性感化表达、复制身份、品牌、可见文字和付费 API。

## 0.3.0 - 2026-08-26

Adds a reviewed photorealistic exploded-product workflow. / 新增已验收的写实产品分解结构工作流。

### Added / 新增

- `exploded-product-diagram` template with a fictional mixed-reality work visor, a nine-layer component hierarchy, and an original 4:5 product visual. / 新增 `exploded-product-diagram` 模板，包含虚构混合现实工作眼镜、九层部件层级和原创 4:5 产品效果图。
- Product routing for exploded-view, teardown, and internal-structure requests. / 新增针对爆炸图、拆解和内部结构请求的产品路由。
- Bilingual prompt and review record that separates generated hardware structure from deterministic text and leader-line composition. / 新增中英文 Prompt 与复核记录，明确生成硬件结构和确定性文字、引线排版的边界。

### Quality boundary / 质量边界

- The first narrow candidate remained private; only the corrected 1122 × 1402 image entered the public gallery. / 首张窄画布候选保留在私下目录，公开 Gallery 只收录修正后的 1122 × 1402 效果图。
- The public image contains no external product, trademark, brand, real-person reference, copied prompt, or paid API dependency. / 公开效果图不含外部产品、商标、品牌、真人参考、复制 Prompt 或付费 API 依赖。

## 0.2.0 - 2026-08-26

Adds a reviewed photorealistic multi-look character workflow. / 新增已验收的写实多穿搭人物工作流。

### Added / 新增

- `realistic-fashion-lookbook` template with a new fictional adult identity, six complete full-body looks, and a deterministic 2 × 3 editorial grid. / 新增 `realistic-fashion-lookbook` 模板，使用全新虚构成年人物、六套完整全身穿搭和确定性 2 × 3 编辑网格。
- Final generation and canvas-correction prompts, approved 4:5 image, SHA-256 records, bilingual review, catalog routing, and tests. / 新增最终生成与画布修正 Prompt、批准的 4:5 效果图、SHA-256、中英文复核、目录路由和测试。
- `Fashion` style and scene routing for realistic wardrobe and lookbook requests. / 新增用于写实穿搭与 Lookbook 请求的 `Fashion` 风格和场景路由。

### Quality boundary / 质量边界

- The first narrow candidate remained private; only the corrected 1122 × 1402 result entered the public gallery. / 首张窄画布候选保留在私下目录，公开 Gallery 只收录修正后的 1122 × 1402 结果。
- No external image, real-person reference, paid API, visible brand, or copied prompt was used. / 不使用外部图片、真人参考、付费 API、可见品牌或复制 Prompt。

## 0.1.0 - 2026-08-26

First public, installable, and verifiable Visual Director baseline. / 首个可公开安装和验证的 Visual Director 基线。

### Included / 已包含

- Three reviewed first-party workflows: Character Design Sheet, Realistic Photography, and Product Commerce Visual. / 三个已验收第一方方向：角色设定表、真实人物摄影、商品商业视觉。
- Final prompts, approved images, SHA-256 records, input roles, and per-image review. / 最终 Prompt、批准效果图、SHA-256、输入角色和逐图复核。
- Visual Brief, explainable template/example selection, CompiledPrompt, and provider-neutral GenerationRequest contracts. / Visual Brief、可解释模板/案例选择、CompiledPrompt 与 provider-neutral 请求契约。
- Built-in image-material route, exact-canvas composition, file QC, visual review, approval gates, and safe promotion. / 内置图片素材路线、精确画布合成、文件 QC、视觉复核、批准门禁和安全 promotion。
- Repo-scoped Skill, buildable Plugin, deterministic release manifest, and automated tests. / 仓库级 Skill、可构建 Plugin、确定性发布清单与自动测试。
- Bilingual public README, installation, architecture, workflow, roadmap, gallery, and prompt records. / 中英文 README、安装、架构、工作流、路线图、Gallery 和 Prompt 记录。

### Public boundary / 公开边界

- No paid-API configuration or call is included. / 不包含付费 API 配置或调用。
- Public catalogs contain approved first-party content only. / 公开目录只包含已批准第一方内容。
- Research material, rejected candidates, caches, secrets, and machine-specific paths are excluded. / 排除研究资料、失败候选、缓存、密钥和机器路径。
- Gallery raster images remain in the public repository but are not bundled into the lean Plugin runtime. / Gallery 栅格图保留在公开仓库，不进入精简 Plugin 运行时。
