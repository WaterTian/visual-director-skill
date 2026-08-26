# 安装与验证 / Installation and Verification

## 中文

### 方式一：仓库级 Skill

这是开发阶段最简单的方式，不修改全局 Codex 配置。

```bash
git clone https://github.com/WaterTian/visual-director-skill.git
cd visual-director-skill
uv run python -m unittest discover -s tests -v
codex
```

Codex 从仓库目录启动后会发现 `.agents/skills/visual-director/`。先做一个不生图的验证：

> 使用 $visual-director，把“原创成年角色的 16:9 角色设定表”整理成 Visual Brief 和 Prompt。不要生图，不要调用付费 API。

预期结果：Codex 读取 Skill，明确目标、尺寸、身份锚点、版式、禁止项和验收标准；没有生成图片或产生 API 调用。

### 方式二：本地 Plugin

Plugin 适合跨项目使用。以下命令会修改当前用户的 Codex Plugin 配置；执行前应确认这是你要安装的仓库。

```bash
uv run python scripts/build-plugin-package.py
codex plugin marketplace add .
codex plugin list --available --json
codex plugin add visual-director@visual-director
codex plugin list --json
```

安装成功后新开 Codex 任务，再显式调用 `$visual-director`。Codex 官方说明要求安装 Plugin 后开启新任务，才能使用新加入的 Skill 或工具。参见 [OpenAI Plugins](https://developers.openai.com/codex/plugins)。

### 验证清单

1. 全部单元测试通过。
2. `codex plugin list --json` 显示 `visual-director` 已安装。
3. 新任务可以识别 `$visual-director`。
4. Prompt-only 验证不会生成图片。
5. `plugins/visual-director/` 中没有密钥、个人绝对路径、研究资料或未批准图片。
6. `runtime/data/cases.json` 只包含九个已批准第一方案例。

### 升级与卸载

重新拉取代码并运行测试后，删除旧的本地构建目录，再重新构建和安装。不要覆盖已有构建包来掩盖差异。

```bash
codex plugin remove visual-director@visual-director
codex plugin marketplace remove visual-director
```

卸载 Plugin 不会删除你在项目中创建的 Brief、候选图或正式资产。

## English

### Option 1: repository-scoped skill

This is the simplest development setup and does not modify global Codex configuration.

```bash
git clone https://github.com/WaterTian/visual-director-skill.git
cd visual-director-skill
uv run python -m unittest discover -s tests -v
codex
```

Codex discovers `.agents/skills/visual-director/` when launched from the repository. Start with a prompt-only check:

> Use $visual-director to turn “a 16:9 character sheet for an original adult character” into a Visual Brief and prompt. Do not generate an image or call a paid API.

Expected result: Codex loads the skill and defines intent, dimensions, identity anchors, layout, exclusions, and acceptance checks without generating an image.

### Option 2: local plugin

Use the plugin when the workflow should be available across projects. These commands change the current user's Codex plugin configuration; review the repository before installing it.

```bash
uv run python scripts/build-plugin-package.py
codex plugin marketplace add .
codex plugin list --available --json
codex plugin add visual-director@visual-director
codex plugin list --json
```

Start a new Codex task after installation, then invoke `$visual-director`. Official OpenAI documentation notes that newly installed plugins become available to new tasks: [OpenAI Plugins](https://developers.openai.com/codex/plugins).

### Verification checklist

1. The full unit-test suite passes.
2. `codex plugin list --json` reports `visual-director` as installed.
3. A new task recognizes `$visual-director`.
4. The prompt-only check does not generate an image.
5. `plugins/visual-director/` contains no secrets, machine-specific paths, research material, or unapproved images.
6. `runtime/data/cases.json` contains only the nine approved first-party examples.

### Upgrade and removal

Pull the new version and rerun tests, then remove the old local build before rebuilding and reinstalling. Do not overwrite an existing package to hide differences.

```bash
codex plugin remove visual-director@visual-director
codex plugin marketplace remove visual-director
```

Removing the plugin does not delete Briefs, candidates, or formal assets created in a project.
