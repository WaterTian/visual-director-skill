# Quality Gates / 质量门禁

Evaluate in order; a later visual impression cannot cancel an earlier hard failure. / 必须按顺序检查，后续观感不能抵消前面的硬失败。

1. **Input / 输入**: deliverable, dimensions, subject, exact text, required and forbidden content, and reference roles are known. / 规格、主体、逐字文字、必需项、禁止项与参考角色明确。
2. **File / 文件**: format, width, height, ratio, transparency, mode, and readability match the Brief. / 格式、尺寸、比例、透明度、色彩模式和可读性正确。
3. **Content / 内容**: identity, geometry, count, placement, and text match; no watermark or invented brand appears. / 身份、几何、数量、位置和文字正确，无水印或虚构品牌。
4. **Visual / 视觉**: composition, anatomy, perspective, lighting, materials, edges, typography, and brand consistency withstand close inspection. / 构图、人体、透视、光线、材质、边缘、文字和品牌一致性经得起近看。
5. **Landing / 落盘**: record prompt version, references, generation metadata, checks, reviewer, and exceptions. Promotion requires `qc_passed` plus separate approval and hash verification. / 记录 Prompt、参考、生成信息、检查、审核人和例外；promotion 需要通过状态、独立批准和哈希校验。

Keep failed candidates separate and overwrite disabled by default. / 失败候选隔离保存，默认禁止覆盖。
