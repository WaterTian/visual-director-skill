# Project Instructions / 项目说明

## Goal / 目标

Build a portable Visual Director Skill that turns visual intent into a structured Brief, reviewed template choice, precise prompt, authorized generation path, quality evidence, and an approval-gated formal asset. / 构建可移植的 Visual Director Skill，将视觉意图转成结构化 Brief、已验收模板选择、精确 Prompt、需授权生成路线、质量证据和受批准门禁保护的正式资产。

## Authority / 权威文件

- Public position and quick start / 公开定位与快速开始：`README.md`
- Architecture / 架构：`docs/architecture.md`
- Workflow / 工作流：`docs/workflow.md`
- Current roadmap / 当前路线图：`docs/roadmap.md`
- Skill behavior / Skill 行为：`.agents/skills/visual-director/SKILL.md`
- Machine contracts / 机器契约：`schemas/`
- First-party catalog / 第一方目录：`data/templates.json`, `data/cases.json`
- Publication allowlist / 发布白名单：`gallery/gallery-manifest.json`

When files conflict, prefer the more specific machine contract and the user's current explicit request. / 文件冲突时优先采用更具体的机器契约和当前用户明确要求。

## Invariants / 不变量

- Public content must be project-created, refined, generated, reviewed, and approved. Research material, copied catalogs, rejected candidates, and caches stay out of public Git. / 公开内容必须由本项目创建、优化、生成、复核并批准；研究资料、复制目录、失败候选和缓存不得进入公开 Git。
- Do not use a paid API for project tests or image production. / 项目测试和图片生产不得使用付费 API。
- Keep prompt compilation separate from generation. Generation needs current authorization. / Prompt 编译与生图分离，生图需要当前授权。
- For edits, the input image is the sole visual authority by default. / 编辑任务默认以输入图为唯一视觉权威。
- Failed candidates never replace formal assets. File QC and visual review must both pass, followed by separate approval. / 失败候选不得替换正式资产；文件与视觉复核均通过后仍需独立批准。
- Preserve original files and hashes; do not hide failure with resizing, compression, or overwrite. / 保留原图和哈希，不用缩放、压缩或覆盖掩盖失败。
- Keep secrets, machine-specific paths, and global Codex configuration out of commits. / 不提交密钥、机器路径或全局 Codex 配置。
- Preserve formal authorship metadata; do not repeat author identity across ordinary documentation. / 保持正式作者元数据，不在普通文档反复显示作者身份。
- Character work is the next priority. Complete, review, and save one new image before starting the next. / 下一阶段优先人物角色；每次完成、复核并保存一张后再进入下一张。

## Completion gate / 完成门槛

Every change must have an observable output, aligned schema/example/implementation, success and failure tests for new scripts, updated bilingual public documentation when behavior changes, and a clean publication audit. / 每项变更必须有可观察输出，schema、示例与实现一致，新脚本具备正常和失败测试，行为变化时更新中英文公开文档，并通过公开内容审计。

Run before publication: / 发布前运行：

```bash
uv run python -m unittest discover -s tests -v
uv run python scripts/build-plugin-package.py
```
