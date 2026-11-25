# Vendored fonts

Two woff2 files, latin subset, weight 400, taken unmodified from Fontsource
5.3.0 and committed here so that `next build` makes no network request.

| File | Family | Upstream | Licence |
| --- | --- | --- | --- |
| `press-start-2p-latin-400.woff2` | Press Start 2P | [Fontsource `@fontsource/press-start-2p`](https://fontsource.org/fonts/press-start-2p) | `OFL-Press-Start-2P.txt` |
| `vt323-latin-400.woff2` | VT323 | [Fontsource `@fontsource/vt323`](https://fontsource.org/fonts/vt323) | `OFL-VT323.txt` |

Both are licensed under the SIL Open Font License 1.1, which permits bundling
and redistribution provided the licence travels with the font. It does: the two
text files above are the licences as published, including the copyright lines
and the reserved font names.

`app/layout.tsx` loads them with `next/font/local`, which hashes and fingerprints
them at build time; nothing else refers to these paths.

To update a face, download the same subset from Fontsource, replace the file,
and keep the licence file with it. Do not switch back to `next/font/google`:
that loader fetches during the build, which is what this directory exists to
avoid.
