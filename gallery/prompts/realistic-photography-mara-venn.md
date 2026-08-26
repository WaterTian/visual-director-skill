# Realistic Photography / 真实人物摄影 — MARA VENN

- 状态 / Status: `approved_public_gallery`
- 生成方式 / Generation path: Codex built-in ImageGen
- 付费 API / Paid API: no
- 身份参考 / Identity reference: `gallery/images/character-design-sheet-mara-venn.png`
- 参考角色 / Reference role: project-created identity and wardrobe reference, not an edit target
- 真人参考 / Real-person reference: no
- 第一方原创 / First-party original: yes
- 图片 / Image: `gallery/images/realistic-photography-mara-venn.png`
- 图片 SHA-256 / Image SHA-256: `654ea248670e831a599f14ddd4c79c709c2d1be4bd2bbb1c7fc1ce6af0aaa6ae`

## 中文说明

这张 4:5 环境人物摄影把同一原创角色转化为可信的真人摄影表达。Prompt 锁定面部、疤痕、发型、左侧铜色发束、服装、围巾、无线电和成年年龄，并单独约束双手、视线、自然肤质、空间肤色与稀疏环境。

## English notes

This 4:5 environmental portrait translates the same original character into believable live-action photography. The prompt locks face, scar, hair, copper streak, wardrobe, scarf, radio, and adult age while separately constraining hands, gaze, natural skin texture, spatial skin color, and the sparse environment.

## Generation prompt / 生成 Prompt

```text
Use case: photorealistic-natural
Asset type: publication-quality Realistic Photography template showcase for the open-source Visual Director project; environmental character portrait
Input images: Image 1 is a character identity and wardrobe reference sheet only, not an edit target. Translate the same original fictional adult character MARA VENN into believable live-action photography while preserving her identity anchors and outfit design.
Primary request: Create one cinematic but natural environmental portrait of MARA VENN working as a field signal scout at a quiet remote communications outpost. The image should feel like an authentic editorial photograph of a real adult professional caught between tasks, not cosplay, not a fashion campaign, and not science-fiction concept art.
Character identity: same 26-year-old adult woman from Image 1; tall athletic build; medium-dark warm brown skin; oval face; amber-brown eyes; small straight scar through her left eyebrow; short asymmetrical black coiled bob; same small copper-colored hair streak on her anatomical left as established by the reference sheet. Preserve recognizable facial proportions, hair silhouette, skin tone, calm intelligence, and adult age.
Wardrobe invariants: same cropped rust-orange weatherproof jacket with its single asymmetrical diagonal clasp; same fitted graphite high-neck field suit; same muted teal signal scarf tucked at her anatomical left collar/shoulder; same charcoal practical boots if visible; same slim rectangular radio at her anatomical left hip; same small copper ear cuff. Translate materials realistically—weathered waxed technical fabric, matte stretch field suit, soft woven scarf, worn anodized radio housing. Do not redesign or add armor, logos, random straps, or weapons.
Scene/backdrop: a restrained high-desert communications outpost just after sunrise; weathered pale concrete shelter, one slim unbranded antenna mast and a distant muted sandstone horizon. Keep the environment sparse and credible, with no vehicles, crowds, city skyline, fantasy machinery, or decorative clutter.
Pose/action: three-quarter body portrait. She stands beside the shelter in a relaxed natural stance, body turned about 30 degrees away from camera. Her gaze is slightly off-camera toward the horizon, thoughtful and alert. Her left hand loosely holds a small folded field map at waist level; her right hand naturally rests beside the radio. Both hands must be clearly visible and anatomically correct, with natural finger spacing and plausible grip. No direct eye contact, no heroic power pose.
Style/medium: ultra-photorealistic documentary editorial photography with natural imperfections. Real pores, fine facial hair, subtle under-eye texture, small expression lines, realistic lips, individual coiled hair strands, slight dust and wear on jacket cuffs. No beauty retouching, no waxy or airbrushed skin, no CGI sheen.
Composition/framing: true 4:5 vertical environmental portrait, knees to head visible with comfortable headroom; subject slightly off-center using the antenna and shelter edge as quiet geometric balance. Face and both hands remain important and readable.
Camera: natural eye-level 50 mm documentary perspective, f/4 look, face and both hands within usable focus, gentle background separation, no artificial fisheye or excessive bokeh.
Lighting/mood: soft low sunrise key from camera-left, neutral open-sky fill, subtle warm rim on hair and jacket, realistic shadow direction. Calm, capable, observant, understated. Skin color must remain spatially even across forehead, cheeks, nose, chin, neck, and under-jaw without orange patches or gray neck mismatch.
Color palette: rust orange, graphite, muted teal, warm brown skin, pale concrete, dusty sandstone sky; cinematic but restrained, natural white balance, no teal-orange blockbuster grade.
Text: none.
Constraints: exactly one adult person; preserve reference identity and wardrobe; two normal arms and two normal hands; five fingers per visible hand; one folded map; one radio; no extra people, letters, numbers, signs, badges, emblems, watermark, or signature.
Avoid: childlike appearance, different ethnicity, different face, long hair, missing copper streak, wrong-side scarf or radio, glamour makeup, sexualized pose, cleavage, smooth plastic skin, oversharpened pores, dead-eyed stare, direct camera gaze, malformed or hidden hands, extra fingers, fused fingers, duplicated limbs, floating objects, cosplay styling, cyberpunk neon, fantasy armor, weapons, branded equipment, text, logo, watermark.
```

## 画布修正 / Canvas-correction edit

The first generation preserved the character but produced a canvas narrower than 4:5. The published image is the following identity-locked horizontal outpaint.

```text
Use case: precise-object-edit
Asset type: corrected publication-quality realistic environmental portrait
Input images: Image 1 is the edit target—the just-generated photorealistic MARA VENN desert communications-outpost portrait.
Primary request: Expand the composition horizontally to a true 4:5 vertical editorial portrait. Reveal additional natural environment on both the left and right sides so the frame feels less narrow and has balanced breathing room. Keep the subject at the same apparent scale or very slightly smaller; retain the knees-to-head three-quarter framing, both complete hands, the folded map, and the radio.
Hard invariant: preserve MARA VENN exactly—same face identity, adult age, medium-dark warm brown skin, facial proportions, amber-brown eyes, left-eyebrow scar, short black coiled bob, copper hair streak, calm off-camera gaze, pose, hand anatomy, finger positions, body proportions, rust jacket, graphite field suit, teal scarf, diagonal clasp, radio, map, lighting direction, skin texture, and natural documentary realism. Do not change, beautify, re-pose, mirror, redesign, or replace the person.
Background extension: continue the existing pale concrete shelter, sparse unbranded antenna mast, high-desert horizon, ground, sunrise light, perspective, depth of field, and color grade seamlessly into the added side areas. Do not add people, vehicles, signs, buildings, equipment clusters, text, logos, or clutter.
Composition: true 4:5 vertical canvas, visually balanced environmental portrait with more context and comfortable negative space; no matte borders, no letterboxing, no stretched content, no crop of head, elbows, hands, map, radio, knees, or jacket.
Constraints: exactly one adult person; both hands anatomically correct and fully visible; no text, letters, numbers, watermark, or signature. Change only canvas width and naturally outpainted side environment; keep everything else unchanged as closely as possible.
```

## 复核 / Review

- 1122 × 1402 PNG/RGB，比例 0.8003，符合 4:5 / valid 4:5.
- 身份、年龄、面部、头发、疤痕、服装、色板、无线电和地图与角色设定表一致 / Identity and wardrobe remain consistent with the project-created character sheet.
- 双手可见，人体与握持可信，无重复肢体或粘连手指 / Both hands are visible with plausible anatomy and grip.
- 皮肤纹理自然，面部与颈部肤色空间一致，无塑料磨皮 / Natural skin texture and spatially consistent face and neck color.
- 一名成年人、一张地图、一个无线电；无文字、logo、商标或水印 / One adult, one map, one radio, and no visible text or marks.
