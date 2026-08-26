# 路线图 / Roadmap

## 中文

### 已完成

- 十个第一方模板及其最终 Prompt、效果图、SHA-256 和逐图复核。
- 新增写实时装 Lookbook，验证同一成年人物在六套穿搭中的身份、人体和完整全身一致性。
- 新增产品分解结构图，验证虚构硬件的九层部件层级、装配关系和无伪文字边界。
- 新增静谧编辑人像，验证成年身份、端庄穿搭、坐姿人体、自然室内光和非性感化边界。
- 新增写实动态编辑摄影，验证成年全身动作、落地重心、完整手脚、端庄无品牌服装和雨后城市摄影质感。
- 新增写实手作纪实人像，验证成年人手部操作、单一陶碗、完整坐姿、工作服、自然窗光和工作室材质。
- 新增写实音乐排练纪实人像，验证人物与大提琴的复杂交互、完整乐器结构、完整手脚和自然排练环境。
- 新增成熟年龄纪实人像，验证自然年龄特征、完整站姿、双手与环境接触、实用服装和非宣传式户外语境。
- Visual Brief、模板/案例选择、Prompt 编译和 provider-neutral 生成请求。
- 无付费 API 的内置图片素材路线与精确画布合成。
- 文件 QC、人工视觉复核、批准门禁、资产 manifest 和安全 promotion。
- 仓库级 Skill、可构建 Plugin、确定性发布清单和自动测试。
- 公开内容白名单：研究资料、未批准候选、缓存、密钥和机器路径不进入发行版。

### 下一阶段

1. **人物角色优先**：继续选择与现有设定表、环境肖像和时装 Lookbook 明显不同的写实人物方向，一次只推进一张；产品方向仅在用户明确指定时扩展。
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

- Ten first-party templates with final prompts, images, SHA-256 records, and per-image review.
- A realistic fashion lookbook validating one adult identity, anatomy, and complete full-body framing across six outfits.
- An exploded product diagram validating nine-layer hierarchy, assembly plausibility, and a no-pseudo-text boundary for fictional hardware.
- A quiet editorial portrait validating adult identity, modest styling, seated anatomy, natural interior light, and a non-sexualized presentation boundary.
- A realistic motion editorial validating adult full-body action, grounded balance, complete hands and shoes, modest unbranded workwear, and rain-wet urban photographic texture.
- A documentary craft portrait validating adult hands-on work, one clay bowl, complete seated anatomy, workwear, natural window light, and workshop materials.
- A documentary music-rehearsal portrait validating a person's complex cello interaction, complete instrument structure, complete hands and shoes, and a natural rehearsal context.
- A mature documentary portrait validating natural age detail, complete standing anatomy, hand-to-environment contact, practical wardrobe, and a non-promotional outdoor context.
- Visual Brief, template/example selection, prompt compilation, and provider-neutral generation requests.
- A no-paid-API built-in material route with exact-canvas composition.
- File QC, human visual review, approval gates, asset manifests, and safe promotion.
- Repo-scoped skill, buildable plugin, deterministic release manifest, and automated tests.
- A public-content allowlist excluding research material, rejected candidates, caches, secrets, and machine paths.

### Next

1. Continue character work with realistic directions that differ clearly from the existing design sheet, environmental portrait, and fashion lookbook, one reviewed asset at a time; expand product work only when the user explicitly directs it.
2. For every accepted image, update the final prompt, image, dimensions, SHA-256, input roles, QC, and catalog record together.
3. Expand character-continuity checks for face, hair, costume construction, left-right details, hands, and multi-view proportions.
4. Verify plugin installation, discovery, prompt-only behavior, and the no-paid-API boundary on a second physical computer.
5. Add poster, infographic, and UI templates only after equivalent generation and review evidence exists.

### Definition of done

A template becomes publicly “reviewed” only when its prompt is optimized for a clear visual objective, at least one result passes file and visual QC, hashes are recorded, success and failure paths are tested, and bilingual public documentation is updated.
