# Generation Handoff / 生图交接

Use the handoff contract when image generation runs outside the deterministic core. / 当生图发生在确定性核心之外时使用该契约。

1. Build and validate a provider-neutral `GenerationRequest`. / 建立并校验 provider-neutral 请求。
2. Load a validated `ProviderCapabilities` record. Block exact-size authorization when the capability is incompatible or unverified, unless the current request explicitly allows one documented built-in exception. / 能力不兼容或未验证时阻止精确尺寸授权；只有当前请求可允许一次有记录的内置例外。
3. Prepare a project-relative candidate path. Leave the handoff pending without current authorization. / 候选路径必须为项目相对路径；没有当前授权时保持等待状态。
4. Generate once with the recorded prompt, references, and invariants. Stop after failure or timeout unless a retry is explicitly authorized. / 按记录参数生成一次；失败或超时后没有新授权不得重试。
5. Preserve the original and record normalized provider, model when known, timestamp, dimensions, SHA-256, and local input hashes for edits. / 保留原图，并记录规范化生成信息；编辑任务还要记录输入哈希。
6. A completed handoff proves execution, not quality. Run file QC and visual review next. / 完成交接只证明执行过，不能证明质量通过。

The current public configuration supports the Codex built-in image path and a deterministic mock adapter. It includes no paid-API configuration. / 当前公开配置只支持 Codex 内置图片路线和确定性 mock，不包含付费 API 配置。
