# 架构与数据流 / Architecture and Data Flow

## 中文

Visual Director 分为四层：

1. **意图层**：`VisualBrief` 保存目标、受众、尺寸、逐字文案、视觉方向、参考图角色和验收项。
2. **决策层**：模板选择器和案例选择器只读取第一方目录，输出可解释分数与最多三个已验收案例。
3. **执行层**：Prompt 编译器生成 provider-neutral 请求；生成可以交给当前 Codex 的内置图片能力或外部 handoff，核心不保存密钥。
4. **质量层**：文件 QC、人工视觉复核、批准记录和 promotion 共同决定候选是否能成为正式资产。

```text
VisualBrief
  ├─ TemplateSelection
  ├─ CaseSelection
  └─ CompiledPrompt
         ↓
  GenerationRequest / MaterialRequest
         ↓
  Candidate + QCReport + VisualReview
         ↓
  Approval → AssetManifest → Formal Asset
```

### 关键边界

- `data/templates.json` 与 `data/cases.json` 只包含已批准第一方内容。
- Prompt 编译不会自动生图；生成是独立、需授权的阶段。
- Edit 以输入图为唯一视觉权威，案例默认只作审计。
- 精确尺寸无法由生成能力保证时，使用透明素材与 `CompositionPlan` 合成，不伪装成原始生成尺寸。
- 候选、QC、批准和正式资产使用 SHA-256 串联，默认禁止覆盖。
- Plugin 包含运行时和 Skill，不包含 Gallery 栅格图；公开仓库中的 Gallery 负责展示和人工对比。

### 可移植性

核心不写死 API Key、用户目录或项目资产路径。项目专属品牌规则和输出目录由 Visual Brief 或项目配置提供。仓库级 Skill 用于开发，Plugin 用于跨项目分发。

## English

Visual Director has four layers:

1. **Intent:** `VisualBrief` captures the goal, audience, dimensions, verbatim copy, art direction, reference roles, and acceptance checks.
2. **Decision:** template and example selectors read only the first-party catalogs and return explainable scores with at most three reviewed examples.
3. **Execution:** the compiler creates a provider-neutral request. Generation can use the image capability available in the current Codex session or an external handoff; the core stores no keys.
4. **Quality:** file QC, human visual review, approval records, and promotion determine whether a candidate can become a formal asset.

### Boundaries

- `data/templates.json` and `data/cases.json` contain approved first-party material only.
- Prompt compilation never generates an image automatically; generation is a separate authorized stage.
- For edits, the input image is the sole visual authority and examples are audit-only by default.
- When exact pixels cannot be guaranteed, a transparent material and `CompositionPlan` create a disclosed composed asset.
- Candidate, QC, approval, and formal-asset records are linked with SHA-256; overwrite is disabled by default.
- The plugin contains the runtime and skill but not gallery raster images. The public repository gallery supports display and visual comparison.

### Portability

The core does not hard-code API keys, user directories, or project asset paths. Project-specific brand rules and output paths come from the Visual Brief or project configuration. Use the repo-scoped skill for development and the plugin for distribution across projects.
