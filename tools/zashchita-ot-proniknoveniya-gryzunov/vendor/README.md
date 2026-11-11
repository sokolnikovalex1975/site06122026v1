# Build-time geometry helpers

These four modules are copied without modification from the Computer Anatomy skill's `kit/`: `iso-kit.mjs`, `audit.mjs`, `lathe.mjs`, `tube.mjs`. They are build-time dependencies for the illustrative building, not client-side libraries.

The authored scene is `../build_contours.mjs`. It records the actual solids, settles their painter's order, and supports `node build_contours.mjs --audit`; the browser receives only the pre-rendered SVG and the small, independent `contours.js` controller.
