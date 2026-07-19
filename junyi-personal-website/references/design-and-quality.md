# Original design and quality review

## Build a design direction from attributes

Ask for three to five brand attributes with behavioral meaning, such as `calm, candid, evidence-led, warm, precise`. Translate them into visible decisions. Do not use a named company's or creator's interface as the design brief.

Create two or three directions that differ in layout rhythm, typography, imagery, and density—not merely button color. Show a small style tile or first screen before building the whole site.

## Token system

Define and reuse:

- foreground, muted, background, surface, border, brand, accent, success, warning, and error colors;
- body, display, mono (if needed), weights, line heights, and maximum reading width;
- spacing scale, radii, shadows, borders, breakpoints, and motion duration;
- default, hover, active, focus, disabled, error, and loading states.

Color must retain readable contrast. Never use color alone to communicate status. Avoid decorative motion that obscures content or ignores reduced-motion preferences.

## Responsive review matrix

Review at least one representative viewport in each class:

| Class | What to inspect |
|---|---|
| Mobile | navigation, text wrapping, touch targets, fixed CTA overlap, image crop, form keyboard |
| Tablet | awkward intermediate columns, line length, card wrapping, landscape layout |
| Desktop | maximum width, empty space, visual hierarchy, hover/focus, large-image quality |

Also test long names, long Chinese/English strings, 200% zoom, missing images, slow loading, and keyboard-only navigation.

## HTML and metadata baseline

- correct document language and one descriptive H1 per page;
- semantic landmarks and logical heading order;
- descriptive link text and form labels;
- useful alt text for meaningful images and empty alt for decorative images;
- `title`, meta description, viewport, canonical URL for production, favicon, and social preview metadata;
- responsive images or appropriately sized assets; explicit image dimensions when practical;
- no private local paths, test copy, secret, or inaccessible interaction.

Automated validation finds omissions, not visual truth. Pair it with rendered screenshots and interaction tests.
