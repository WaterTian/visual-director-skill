---
name: visual-director
description: Create, refine, or review bitmap image assets by turning a visual request into a structured brief, precise prompt, authorized generation plan, and quality-gated result. Use for product visuals, character work, photography, posters, infographics, UI imagery, illustration, and scenes; do not use for code-native SVG or ordinary CSS-only changes.
---

# Visual Director / 视觉导演

Turn the user's intent into a reviewable visual contract before generation. Preserve exact wording, dimensions, reference roles, brand constraints, output paths, and approval gates. / 生图前先把用户意图整理为可复核的视觉契约，并保留逐字文案、尺寸、参考图角色、品牌约束、输出路径和批准门禁。

## Route / 路由

- **Create / 创建**: build a Visual Brief, compile one coherent prompt, generate only when requested, then review the result. / 建立 Brief、编译单一完整 Prompt，仅在用户要求时生图，随后复核。
- **Edit / 编辑**: inspect every input image and separate invariants from allowed changes. / 检查每张输入图，区分不变量与允许修改项。
- **Review / 复核**: compare the supplied asset with the Brief; do not replace it unless requested. / 对照 Brief 检查现有资产，未经要求不生成替代图。
- **Prompt only / 仅 Prompt**: return a reusable prompt and assumptions without generating an image. / 只交付可复用 Prompt 和假设，不生图。

Read [visual-brief.md](references/visual-brief.md) for ambiguous or repeatable requests. Read [reviewed-examples.md](references/reviewed-examples.md) before selecting examples. Read [generation-handoff.md](references/generation-handoff.md) before generation. Read [exact-canvas-composition.md](references/exact-canvas-composition.md) when final pixels must be exact. Read [quality-gates.md](references/quality-gates.md) before accepting or landing an asset.

## Workflow / 工作流

1. Inspect project-local brand and output configuration. The user's current explicit request remains authoritative. / 读取项目品牌与输出配置，当前用户请求始终优先。
2. Normalize goal, audience, deliverable, exact content, art direction, composition, references, forbidden details, and acceptance criteria. / 规范目标、受众、交付规格、逐字内容、视觉方向、构图、参考图、禁止项与验收项。
3. Choose the closest reviewed first-party template and inspect up to three local examples. Scores shortlist; they do not prove visual similarity. / 选择最近的已验收第一方模板并查看最多三个本地案例；分数只用于初筛。
4. Compile one prompt with concrete subject, composition, camera, light, materials, exact text, dimensions, must-include items, and exclusions. Transfer only generic cues supported by the Brief. / 编译一个具体 Prompt，只采用 Brief 已支持的通用结构线索。
5. For edits, treat the input as the sole visual authority unless style transfer is explicitly requested. / 编辑任务默认以输入图为唯一视觉权威。
6. Generate only with current authorization. Keep provider details outside the reusable Brief unless required. / 仅在当前授权下生成，非必要不把 provider 写入可复用 Brief。
7. Check every hard requirement, then perform visual review. Iterate on the failed constraint rather than adding generic quality words. / 先检查硬约束，再做视觉复核；针对失败项迭代。
8. Keep failed candidates separate. Formal landing requires passed gates and explicit approval. / 失败候选隔离保存，正式落盘必须通过门禁并获得明确批准。

When repository scripts are available, prefer their validator, selector, compiler, QC, and supported composition routes. The exact-canvas pipeline can request one built-in transparent material without a paid API, but still requires current authorization. / 仓库脚本可用时，优先使用其中的校验、选择、编译、QC 和已支持合成路线；内置透明素材路线不需要付费 API，但仍需当前授权。

## Boundaries / 边界

- Never store secrets or machine-specific absolute paths in reusable files. / 不在可复用文件中保存密钥或机器绝对路径。
- Do not treat an example as proof that a result is reproducible. / 不把案例视为可复现性的证明。
- Do not crop, upscale, compress, or overwrite merely to make a failed candidate appear compliant. / 不用裁切、放大、压缩或覆盖来伪装通过。
- Only reviewed first-party templates, prompts, and gallery assets belong in the public catalog. / 公开目录只允许已验收的第一方模板、Prompt 和效果图。
