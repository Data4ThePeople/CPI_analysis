# Hero image prompts: The CPI Hot Air Balloon

Target: 1680x1080 landscape. Generate wide (3:2 or 16:10). The backdrop is
only the scene; our data balloon (`images/cpi-september-2026-balloon-cutout.png`,
transparent) is laid over the empty sky in the center afterward, so the
prompt asks for open sky in the middle and no balloon there.

## Prompt 1 (recommended): dawn over an ordinary American town

Photorealistic wide landscape photograph at dawn, shot from a low hill looking
out over an ordinary American small town: rows of modest houses and rooftops,
a gas station canopy glowing at the edge of a two-lane road, power lines,
trees with early fall color. Soft golden light on the horizon fading to pale
blue overhead, light haze in the low areas. The upper two-thirds of the frame
is open, empty sky, with nothing in the center of the frame. Two or three
small, distant hot air balloons near the far left and right edges only. Calm,
quiet, slightly nostalgic mood. Natural colors, shallow contrast, 35mm lens,
no people in focus. No text, no readable signs, no prices, no logos.

## Prompt 2 (variant): open sky over farmland

Photorealistic wide photograph of a clear early-morning sky over flat
Midwestern farmland and a distant highway, soft warm light near the horizon,
pale blue sky above, a few thin wispy clouds. The center of the frame is open,
empty sky. A few tiny hot air balloons far in the distance near the edges.
Calm and still. Natural colors, 24mm lens. No text, no signs, no logos.

## Chosen

Prompt 1, generated in Gemini by Eric. Backdrop: images/cpi-september-2026-hero-source.jpg
(2752x1536). scripts/build.py center-crops it to 1680x1080 and lays the
balloon cutout (images/cpi-september-2026-balloon-cutout.png) over the sky,
650px tall, centered, with a soft shadow, after cropping to the top 82% of the photo (sky plus a strip of town).
Alt (under 500 characters): see hero_alt in POST.md.
