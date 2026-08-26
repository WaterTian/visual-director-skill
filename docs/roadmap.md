# 路线图 / Roadmap

## 中文

### 已完成

- 三个第一方模板及其最终 Prompt、效果图、SHA-256 和逐图复核。
- Visual Brief、模板/案例选择、Prompt 编译和 provider-neutral 生成请求。
- 无付费 API 的内置图片素材路线与精确画布合成。
- 文件 QC、人工视觉复核、批准门禁、资产 manifest 和安全 promotion。
- 仓库级 Skill、可构建 Plugin、确定性发布清单和自动测试。
- 公开内容白名单：研究资料、未批准候选、缓存、密钥和机器路径不进入发行版。

### 下一阶段

1. **人物角色优先**：新增一张经过实测的角色类效果图，一次只推进一张。
2. 每张新图同步更新：最终 Prompt、效果图、尺寸、SHA-256、输入角色、QC 和案例目录。
3. 增加角色连续性检查：脸部、发型、服装结构、左右细节、手部和多视图比例。
4. 在第二台物理电脑完成 Plugin 安装、识别、Prompt-only 和 no-paid-API 验收。
5. 达到以上门槛后再扩展海报、信息图和 UI，不提前声明未经实测的模板。

### 完成定义

一个新模板只有同时满足以下条件才进入公开“已验收”范围：

- Prompt 已针对明确视觉目标优化；
- 至少一张效果图通过文件和视觉 QC；
- Prompt 与图片哈希写入 manifest；
- 正常路径和失败路径测试通过；
- 中英文公开说明已更新。

## English

### Completed

- Three first-party templates with final prompts, images, SHA-256 records, and per-image review.
- Visual Brief, template/example selection, prompt compilation, and provider-neutral generation requests.
- A no-paid-API built-in material route with exact-canvas composition.
- File QC, human visual review, approval gates, asset manifests, and safe promotion.
- Repo-scoped skill, buildable plugin, deterministic release manifest, and automated tests.
- A public-content allowlist excluding research material, rejected candidates, caches, secrets, and machine paths.

### Next

1. Prioritize character work and complete one new reviewed character asset at a time.
2. For every accepted image, update the final prompt, image, dimensions, SHA-256, input roles, QC, and catalog record together.
3. Expand character-continuity checks for face, hair, costume construction, left-right details, hands, and multi-view proportions.
4. Verify plugin installation, discovery, prompt-only behavior, and the no-paid-API boundary on a second physical computer.
5. Add poster, infographic, and UI templates only after equivalent generation and review evidence exists.

### Definition of done

A template becomes publicly “reviewed” only when its prompt is optimized for a clear visual objective, at least one result passes file and visual QC, hashes are recorded, success and failure paths are tested, and bilingual public documentation is updated.
