# 路线图 / Roadmap

## 中文

### 已完成

- 十四个第一方模板及其最终 Prompt、效果图、SHA-256 和逐图复核。
- 新增写实时装 Lookbook，验证同一成年人物在六套穿搭中的身份、人体和完整全身一致性。
- 新增产品分解结构图，验证虚构硬件的九层部件层级、装配关系和无伪文字边界。
- 新增静谧编辑人像，验证成年身份、端庄穿搭、坐姿人体、自然室内光和非性感化边界。
- 新增写实动态编辑摄影，验证成年全身动作、落地重心、完整手脚、端庄无品牌服装和雨后城市摄影质感。
- 新增写实手作纪实人像，验证成年人手部操作、单一陶碗、完整坐姿、工作服、自然窗光和工作室材质。
- 新增写实音乐排练纪实人像，验证人物与大提琴的复杂交互、完整乐器结构、完整手脚和自然排练环境。
- 新增成熟年龄纪实人像，验证自然年龄特征、完整站姿、双手与环境接触、实用服装和非宣传式户外语境。
- 新增写实发型变化咨询板，验证十二格中同一成年身份、影棚条件和人像构图稳定，且仅发型发生受控变化。
- 新增概念海报视觉底板，验证单一视觉锚点、受控纸材与色彩层级、标题安全区，以及生成视觉与确定性文字排版的边界。
- 新增暖调影棚编辑人像，验证虚构成年男性的清晰双眼、自然年龄细节、皮肤胡须和服装材质、可控暖色，以及非广告化表达。
- 新增极简落地编辑人像，验证虚构成年女性的完整双手与双膝、可信坐姿、端庄叠穿、皮肤与织物细节、安静留白和非性感化边界。
- Visual Brief、模板/案例选择、Prompt 编译和 provider-neutral 生成请求。
- 无付费 API 的内置图片素材路线与精确画布合成。
- 文件 QC、人工视觉复核、批准门禁、资产 manifest 和安全 promotion。
- 仓库级 Skill、可构建 Plugin、确定性发布清单和自动测试。
- 公开内容白名单：研究资料、未批准候选、缓存、密钥和机器路径不进入发行版。

### 下一阶段

1. **人物角色优先**：继续选择与现有设定表、环境肖像、时装 Lookbook、暖调影棚和落地编辑人像明显不同的写实方向；一次只推进一张，产品方向仅在用户明确指定时扩展。
2. **每图闭环**：每张新图同步更新最终 Prompt、效果图、尺寸、SHA-256、输入角色、QC、独立批准和案例目录；任何一项缺失都不进入公开 Gallery。
3. **连续性检查**：增加角色连续性检查，覆盖脸部、发型、服装结构、左右细节、手部和多视图比例；将测量和人工视觉判断分开记录。
4. **可移植验证**：在第二台物理电脑完成 Plugin 构建、安装、发现、Prompt-only 和 no-paid-API 验收，并记录实际环境与结果。
5. **谨慎扩展**：在上述门槛稳定后，再分别验证海报、信息图和 UI；每个新方向先有可公开的实测资产，再写入已验收范围。

### 完成定义

一个新模板只有同时满足以下条件才进入公开“已验收”范围：

- Prompt 已针对明确视觉目标优化；
- 至少一张效果图通过文件和视觉 QC；
- Prompt 与图片哈希写入 manifest；
- 正常路径和失败路径测试通过；
- 中英文公开说明已更新。

## English

### Completed

- Fourteen first-party templates with final prompts, images, SHA-256 records, and per-image review.
- A realistic fashion lookbook validating one adult identity, anatomy, and complete full-body framing across six outfits.
- An exploded product diagram validating nine-layer hierarchy, assembly plausibility, and a no-pseudo-text boundary for fictional hardware.
- A quiet editorial portrait validating adult identity, modest styling, seated anatomy, natural interior light, and a non-sexualized presentation boundary.
- A realistic motion editorial validating adult full-body action, grounded balance, complete hands and shoes, modest unbranded workwear, and rain-wet urban photographic texture.
- A documentary craft portrait validating adult hands-on work, one clay bowl, complete seated anatomy, workwear, natural window light, and workshop materials.
- A documentary music-rehearsal portrait validating a person's complex cello interaction, complete instrument structure, complete hands and shoes, and a natural rehearsal context.
- A mature documentary portrait validating natural age detail, complete standing anatomy, hand-to-environment contact, practical wardrobe, and a non-promotional outdoor context.
- A realistic hairstyle variation board validating one adult identity, studio conditions, and portrait framing across twelve cells while hairstyle alone changes in a controlled way.
- A concept poster visual plate validating one clear visual anchor, disciplined paper material and color hierarchy, typography-safe zones, and the boundary between generated visual material and deterministic text layout.
- A tonal studio editorial portrait validating a fictional adult man's clear eyes, natural age detail, skin, beard and wardrobe material, controlled warm color, and a non-advertising boundary.
- A minimal floor editorial portrait validating a fictional adult woman's complete hands and knees, credible seated pose, modest layered wardrobe, skin and textile detail, calm negative space, and a non-sexualized boundary.
- Visual Brief, template/example selection, prompt compilation, and provider-neutral generation requests.
- A no-paid-API built-in material route with exact-canvas composition.
- File QC, human visual review, approval gates, asset manifests, and safe promotion.
- Repo-scoped skill, buildable plugin, deterministic release manifest, and automated tests.
- A public-content allowlist excluding research material, rejected candidates, caches, secrets, and machine paths.

### Next

1. **Prioritize characters:** continue with realistic directions that differ clearly from the existing design sheet, environmental portrait, fashion lookbook, tonal studio, and floor editorial work. Advance one reviewed asset at a time; expand product work only when the user explicitly directs it.
2. **Close every image:** update the final Prompt, image, dimensions, SHA-256, input roles, QC, independent approval, and catalog record together. A missing item blocks entry to the public Gallery.
3. **Check continuity:** expand character-continuity checks for face, hair, costume construction, left-right details, hands, and multi-view proportions; record measured checks separately from human visual judgment.
4. **Verify portability:** on a second physical computer, build and install the Plugin, verify discovery and prompt-only behavior, confirm the no-paid-API boundary, and record the actual environment and result.
5. **Expand deliberately:** validate posters, infographics, and UI separately after the above gates are stable. Each new direction needs a public, tested asset before it enters the reviewed scope.

### Definition of done

A template becomes publicly “reviewed” only when its prompt is optimized for a clear visual objective, at least one result passes file and visual QC, hashes are recorded, success and failure paths are tested, and bilingual public documentation is updated.
