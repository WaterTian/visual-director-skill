# Exploded Product Diagram / 产品分解结构图 — ORBITAL FRAME ONE

- 状态 / Status: `approved_public_gallery`
- 生成方式 / Generation path: Codex built-in ImageGen
- 付费 API / Paid API: no
- 输入图片 / Input images: none
- 外部产品或商标参考 / External product or trademark reference: no
- 第一方原创 / First-party original: yes
- 图片 / Image: `gallery/images/exploded-product-diagram-orbital-frame-one.png`
- 图片 SHA-256 / Image SHA-256: `4a578b623e20895aa6873f084f18c5e0e86bd93ce511c1a8ac44ed1f0360bc41`

## 中文说明

这张产品分解结构图使用完全虚构的混合现实工作眼镜，不使用外部产品、商标、品牌或图片。图像模型只生成可审查的硬件分层与材质；任何需要逐字准确的标题、部件名称和引线，都应在后续使用确定性排版生成，而不是交给图像模型伪造文字。

## English notes

This exploded product diagram uses a wholly fictional mixed-reality work visor without external products, trademarks, brands, or images. Image generation owns the reviewable hardware hierarchy and materials only. Any title, component name, or leader line that requires exact wording should be added later through deterministic composition rather than generated pseudo-text.

## Generation prompt / 生成 Prompt

```text
Use case: product-mockup
Asset type: publication-quality Visual Director template showcase; a technical exploded-product poster without typography
Primary request: Create one original, physically plausible exploded-view product visualization of a fictional premium mixed-reality work visor called ORBITAL FRAME ONE. It must read as a real industrial-design and engineering presentation, not a cartoon, an illustration, a toy, or a copy of an existing consumer headset.

Scene/backdrop: a clean vertical 4:5 studio poster on a pale warm-gray to very subtle ice-blue gradient background, with abundant uncluttered negative space around the central assembly. No desk, human, room, landscape, packaging, or decorative objects.

Subject: exactly one wearable mixed-reality work visor shown in a centered, front-facing, vertically stacked exploded arrangement. The fictional device has a slim asymmetric graphite-anodized magnesium outer visor shell with a softly smoked translucent front window, two small muted-green tracking apertures near the outer corners, a dark micro-perforated speaker band, and a restrained woven charcoal headband. It has no branding and no visible lettering.

Structure: show these nine coherent functional layers in clear top-to-bottom order with even vertical separation and aligned center axis: (1) graphite front shell with translucent window, (2) optical-sensor subassembly, (3) black magnesium internal frame, (4) dark green multilayer mainboard, (5) paired pancake-optic modules with faint blue-violet anti-reflective coating, (6) two compact dark battery modules positioned symmetrically beside the central stack, (7) slim acoustic and cooling subassembly, (8) woven charcoal rear headband and adjustment cradle, (9) soft charcoal facial-interface cushion. Each layer must belong unmistakably to the same device and preserve believable scale, fastening logic, cable routing, and left-right symmetry. Keep the eight principal vertical layers centered; only the two battery modules may float symmetrically at the same level as their intended connection point.

Style/medium: premium photorealistic industrial-design visualization, physically based product rendering with camera-real material response. Crisp machined-metal edges, honest matte polymer, fine woven textile fibers, subtle gasket texture, believable circuit-board solder points, controlled translucent optics, and restrained engineering realism. No futuristic fantasy machinery, no exposed impossible mechanisms, no toy plastic, no glossy chrome overload.

Composition/framing: full device and every exploded layer visible from top to bottom within the portrait canvas. Camera is centered and nearly orthographic with a very mild 85 mm product-photography perspective; strict axial alignment, calm visual rhythm, and generous margins. Use soft floorless studio depth with faint ambient occlusion and tiny contact shadows under each layer; do not add arrows, leader lines, diagrams, panels, borders, captions, icons, or UI.

Lighting/mood: large diffused studio key from upper-left, soft cool fill from upper-right, subtle rim light to make the layers readable without glowing effects. Quiet, precise, premium, technically credible.

Color palette: graphite, deep charcoal, muted forest green, smoked graphite translucency, faint cool blue-violet optical reflections, and restrained warm-gray background.

Text: none.
Constraints: exactly one original fictional wearable device; exactly nine clearly distinguishable functional layers; one pair of optical modules; two symmetric battery modules; all parts fully visible; no loose screws, duplicate components, floating unrelated fragments, people, hands, logos, trademarks, readable text, watermark, signature, border, poster title, labels, or reference to real products or companies.
Avoid: cartoon, anime, illustration, doll-like render, fantasy armor, cyberpunk neon, copied consumer-headset silhouette, white plastic headset styling, distorted lenses, impossible cable routing, asymmetric optic modules, excessive glowing, clutter, cropped parts, extra straps, extra batteries, mislabeled parts, pseudo-text, and watermark.
```

## 画布修正 / Canvas-correction edit

The first generation passed the visual content check but was narrower than 4:5. The published image is the following identity-locked horizontal outpaint.

```text
Use case: precise canvas correction.
Input image: the supplied photorealistic exploded-view image of one fictional mixed-reality work visor is the edit target.
Primary request: expand the canvas horizontally to a true 4:5 vertical aspect ratio by naturally outpainting only the pale warm-gray and faint ice-blue studio background at the far left and far right. Preserve the centered, vertically stacked exploded device as a single coherent object with more outer breathing room.

Hard invariant: keep the original device and every existing layer exactly unchanged—same graphite front shell, sensor assembly, black internal frame, dark green mainboard, dual optical modules, two battery modules, acoustic-cooling strip, woven headband, facial cushion, all cables, all fasteners, all materials, scale, axial alignment, vertical spacing, shadows, and optical reflections. Do not redraw, replace, alter, rescale, mirror, crop, add, remove, re-order, or re-pose any device part. Do not add labels or visual marks.

Background extension: continue the existing soft gradient and floorless studio depth into the new outer areas. Match background grain, quiet vignette, light direction, and color perfectly; no side panels, borders, frame, poster graphics, arrows, diagrams, text, logos, watermark, or decorative objects.

Output: a true 4:5 portrait canvas with the entire exploded device fully visible, centered, and unchanged. Exactly one original fictional device, no people, no hands, no brand, no readable text, no extra modules, and no cropped parts. Change only the horizontal canvas extent and newly created outer background.
```

## 复核 / Review

- 1122 × 1402 PNG/RGB，比例 0.8003，符合 4:5 / valid 4:5.
- 恰好一套虚构设备；九个可辨结构层与一对对称电池模块均完整可见 / Exactly one fictional device; all nine distinguishable layers and the symmetric battery pair are completely visible.
- 外壳、传感器、框架、主板、双光学模组、散热声学层、头带和面罩在形态与装配关系上连贯可信 / Shell, sensors, frame, mainboard, dual optics, acoustic-cooling layer, headband, and cushion have coherent shapes and plausible assembly relations.
- 金属、聚合物、织物、镜片和电路板呈现为真实工业产品材质；无卡通、玩具或插画质感 / Metal, polymer, textile, optics, and board materials read as real industrial product surfaces, not cartoon, toy, or illustration.
- 无可见文字、logo、商标、水印、人物、重复设备或无关漂浮零件 / No visible text, logo, trademark, watermark, people, duplicate device, or unrelated floating fragments.
