# Exact Canvas Composition / 精确画布合成

Use this route when final bitmap dimensions must be exact but the authorized image capability supplies visual material at an uncontrolled size. / 当最终位图必须精确，而生图能力不能保证尺寸时使用。

1. Preserve the original generated material and record SHA-256, dimensions, alpha state, provider, and model when known. / 保留原始素材并记录哈希、尺寸、透明度和已知生成信息。
2. Prefer one isolated layer with genuine transparency and no text. / 优先生成真正透明、无文字的独立素材层。
3. For a supported landscape Hero, use `run-free-exact-pipeline.py`. The first run creates an authorization-gated material request; resume with `--material` after the built-in image capability saves the original. / 已支持的横向 Hero 使用该入口，先建立需授权素材请求，保存原图后用 `--material` 恢复。
4. For other layouts, confirm a `CompositionPlan` that records canvas, source hashes, crop, fit boxes, and text layers. / 其他版式需确认记录画布、来源哈希、裁切、适配框和文字层的计划。
5. Do not overwrite source or output. Preserve the `CompositionRecord` and describe the result as a composed asset. / 不覆盖来源或输出，保留合成记录，并明确称为合成资产。
6. Run file QC and visual review against the final Brief. / 最终结果仍需按 Brief 完成文件与视觉复核。
