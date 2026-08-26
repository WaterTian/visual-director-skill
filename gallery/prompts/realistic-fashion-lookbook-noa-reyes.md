# Realistic Fashion Lookbook / 写实时装 Lookbook — NOA REYES

- 状态 / Status: `approved_public_gallery`
- 生成方式 / Generation path: Codex built-in ImageGen
- 付费 API / Paid API: no
- 输入图片 / Input images: none
- 真人参考 / Real-person reference: no
- 第一方原创 / First-party original: yes
- 图片 / Image: `gallery/images/realistic-fashion-lookbook-noa-reyes.png`
- 图片 SHA-256 / Image SHA-256: `1a04934321777072af1f321f8caece2207723371d50eb53a7614e3d74015c845`

## 中文说明

这张写实时装 Lookbook 使用全新虚构成年人物，不依赖真人或外部参考图。Prompt 将同一人物身份、六套穿搭、完整全身、2 × 3 网格、自然皮肤与无文字要求分别锁定，重点验证单张图中的跨格身份一致性和服装可读性。

## English notes

This realistic fashion lookbook uses a new fictional adult identity without a real-person or external image reference. The prompt locks identity, six wardrobe capsules, complete full-body framing, a 2 × 3 grid, natural skin, and the no-text requirement separately, with emphasis on cross-cell identity consistency and readable styling.

## Generation prompt / 生成 Prompt

```text
Create a premium photorealistic fashion lookbook contact sheet showing exactly six full-body appearances of the same fictional adult woman, NOA REYES, age 29. She has a consistent oval face, warm medium-olive skin with natural pores and subtle tonal variation, dark brown almond-shaped eyes, straight dark-brown shoulder-length hair with a center part, an athletic-average build, and a calm self-assured expression. This is one identity repeated across six wardrobe looks, not six different women.

Canvas and layout: vertical 4:5 image, clean 2-column by 3-row editorial grid, one full-body figure centered in each cell, equal figure scale, aligned floor line, generous cream-colored negative space, balanced margins, no overlapping figures, no inset portraits, no captions or decorative graphics. Every figure must be visible from the top of the head to both shoes, with both hands readable and naturally posed.

Six distinct realistic wardrobe capsules, ordered left-to-right and top-to-bottom:
1. Minimal office: charcoal relaxed blazer, ivory knit top, tailored black trousers, black leather loafers.
2. Weekend denim: indigo straight-leg jeans, crisp white shirt with rolled sleeves, tan belt, clean white sneakers.
3. Rainy-day utility: matte olive field jacket, dark straight trousers, practical ankle boots, folded compact umbrella held naturally in one hand.
4. Monochrome evening: elegant long-sleeve black midi dress, restrained silver earrings, low black heels.
5. Athletic travel: navy technical jacket, heather-gray fitted T-shirt, tapered travel pants, understated trainers, small cross-body bag.
6. Soft knit casual: oatmeal cardigan over a muted sage top, cream wide-leg trousers, brown suede flats.

Pose direction: six subtle, believable catalog poses with small variations in weight shift and arm position. Keep the face, hair length, age, skin tone, body proportions, height, and facial features identical in all six cells. Natural adult anatomy, correct hands and fingers, plausible fabric drape, grounded feet, accurate footwear, realistic seams and materials.

Photography: high-end contemporary fashion catalog photographed in a real studio, 65 mm lens perspective, camera near waist height, soft large-window key light from camera-left, broad white fill, gentle floor contact shadows, restrained contrast, neutral color science, crisp clothing texture, authentic skin texture, minimal makeup, no glossy beauty retouching. Seamless warm ivory backdrop and pale stone studio floor.

The final result must look like a professionally art-directed fashion editorial contact sheet assembled from six consistent studio photographs. No illustration, no cartoon, no anime, no 3D render, no doll or plastic skin, no painterly effect, no fantasy styling, no sexualized styling, no exposed lingerie, no celebrity likeness, no brand marks, no logos, no readable text, no watermark, no border, no duplicated outfit, no cropped head or feet, no extra people, no extra limbs, no fused fingers, no distorted face, no mirrored asymmetry, no background props except the umbrella and cross-body bag specified above.
```

## 画布修正 / Canvas-correction edit

The first generation passed the content review but produced a canvas narrower than 4:5. The published image is the following identity-locked horizontal outpaint.

```text
Use case: precise canvas correction.
Input image: the supplied six-panel photorealistic fashion lookbook is the edit target.
Primary request: Expand the canvas horizontally to a true 4:5 vertical aspect ratio by naturally outpainting additional warm-ivory studio background only at the far left and far right. Preserve the complete 2-column by 3-row layout, equal cells, all six full-body figures, their scale, their vertical positions, the center seam, floor lines, and the existing warm studio lighting. The result must remain a clean symmetrical fashion catalog contact sheet with more outer breathing room.

Hard invariant: keep every depiction of NOA REYES exactly as in the input—same six faces and expressions, hair, age, skin tone, body proportions, pose, hands, fingers, clothing, shoes, umbrella, cross-body bag, fabric details, shadows, and cell placement. Do not redraw, beautify, re-pose, replace, mirror, crop, stretch, add, or remove any person or garment. Do not change the internal grid or introduce gutters between existing panels.

Background extension: continue the existing seamless warm ivory wall and pale stone floor into the new side areas with matching grain, perspective, tone, floor height, and soft contact-light behavior. No borders, matte bars, frames, captions, decorative graphics, props, seams, or gradients that were not already present.

Output: true 4:5 portrait canvas; exactly six full-body appearances of the same fictional adult woman; no text, logo, signature, watermark, extra people, extra limbs, cropped head, or cropped shoes. Change only the horizontal canvas extent and newly outpainted outer background.
```

## 复核 / Review

- 1122 × 1402 PNG/RGB，比例 0.8003，符合 4:5 / valid 4:5.
- 恰好六个格子，每格一位完整全身人物，2 × 3 顺序清楚 / Exactly six cells with one complete full-body figure per cell in a clear 2 × 3 order.
- 六格保持同一成年人物的脸型、发型、肤色、年龄和身体比例 / Face, hair, skin tone, age, and body proportions remain recognizably consistent across all six cells.
- 六套服装差异明确，主要服装、鞋履和指定配件均可读 / All six wardrobe capsules are distinct and their principal garments, footwear, and specified accessories are readable.
- 手、腿和鞋部完整可信，无额外人物、重复肢体或明显粘连 / Hands, legs, and shoes are complete and plausible, with no extra people, duplicated limbs, or obvious fusions.
- 呈现为自然影棚摄影，肤质和布料真实，无卡通、插画、3D 或玩偶质感 / The result reads as natural studio photography with believable skin and fabric, not cartoon, illustration, 3D, or doll imagery.
- 无可见文字、品牌、logo、签名或水印 / No visible text, brand, logo, signature, or watermark.
