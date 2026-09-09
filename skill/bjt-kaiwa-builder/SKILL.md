---
name: bjt-kaiwa-builder
description: Creates BJT kaiwa lessons from Japanese business vocabulary (screenshots or PDF) and optionally overlays BJT grammar patterns. Use when the user asks to make a kaiwa bài hội thoại from BJT từ vựng / cụm từ cố định, add ruby + Vietnamese translation toggles, lồng ghép ngữ pháp BJT, or export MP3/MP4 review files.
---

# BJT Kaiwa Builder

## Purpose

Create a reusable BJT conversation lesson from Japanese business vocabulary. Output is a self-contained `index.html` (dialogue + ruby toggle + VI toggle + PDF export) plus optional MP3/MP4 review files. Optionally overlay BJT J2~J3 grammar patterns on top of the vocabulary.

## Trigger Phrases

Use this skill when the user says things like:

- "làm bài kaiwa từ 37 cụm từ" / "cụm từ cố định BJT"
- "tạo hội thoại bài N của [PDF từ vựng BJT]"
- "tạo hội thoại có ルビ và dịch"
- "lồng ghép ngữ pháp BJT vào từ vựng bài N"
- "xuất mp3/mp4 để nghe lại"
- "show nội dung đọc trên màn hình" / "thêm button xuất PDF"

## Input Types

The source can be any of:

1. **Screenshots** of BJT expressions (OCR path). See [reference.md](reference.md) for the sample 37-expression set.
2. **Vocabulary PDF** organized by bài (e.g. `Thaolejp_BJT_Chinh phuc tu vung.pdf`). Extract with PyMuPDF, then locate the target bài by heading (e.g. `BÀI 1`).
3. **Grammar PDF** (e.g. `Thaolejp_BJT_Tong hop ngu phap BJT J3~J2 thuong gap.pdf`). Shared 117-pattern list. Do **not** pick favorites. Follow [grammar-coverage.md](grammar-coverage.md).

## Workflow

1. **Locate and extract source.**
   - Screenshots: read images in chronological order, OCR to extract expressions + meanings.
   - Vocab PDF: use PyMuPDF to extract the target bài's pages, then parse the numbered items (`01. 挨拶「あいさつ」...`).
   - Grammar PDF: open [grammar-coverage.md](grammar-coverage.md). Take the **next 15 unused** IDs (PDF order). Bài 4 next = `#22–36`. After the lesson, write the bài number into the Used in column.

2. **Build one continuous kaiwa.**
   - Do not make a disconnected vocabulary list.
   - Use a realistic business scene (project kickoff, client proposal, internal meeting, product launch, morning stand-up, etc.).
   - Target 15~25 dialogue lines; 25 is fine if needed to cover all target expressions.
   - Include every target vocabulary expression exactly once when possible.
   - Wrap each target vocabulary expression with `class="phrase"`, and its VI counterpart with `class="vi-phrase"`.

3. **Add ruby/furigana to every kanji.**
   - Use HTML `<ruby>漢字<rt>かな</rt></ruby>`.
   - Cover kanji in `.jp`, `.speaker`, and `.scene-title`.
   - Default ruby hidden: `<body class="hide-ruby">`. Toggle button starts as `Hiện ルビ`.

4. **Add Vietnamese translation toggle.**
   - Put each translation in `<div class="vi">...</div>`.
   - Wrap the VI equivalent of the target expression in `<span class="vi-phrase">...</span>`.
   - Style `.phrase` / `.vi-phrase` in red (`#c62828`) with a light-red background.
   - Keep translations natural Vietnamese, not word-by-word.

5. **(Optional) Overlay BJT grammar patterns.**
   - When the user asks to lồng ghép ngữ pháp, add `class="grammar"` (JP) and `class="vi-grammar"` (VI) spans.
   - Style grammar in **blue** (`#1a73e8`) with a light-blue background so it clearly differs from red vocabulary.
   - Include a legend near the header explaining both colors.
   - **Coverage (mandatory from bài 3):** 15 unused patterns from [grammar-coverage.md](grammar-coverage.md), PDF order. Do not reuse the bài 1/2 "greatest hits" set. Swap at most 2–3 if a pattern cannot fit the scene; take the next unused and mark the skipped one `hoãn`. After 117 are used once, pick the least-used IDs (review cycle).
   - Do **not** rebuild bài 1 or bài 2 just to change grammar.
   - Rewrite dialogue lines to embed each assigned pattern naturally; keep all vocabulary intact.

6. **Add PDF export.**
   - Add a `Xuất PDF` button that calls `window.print()`.
   - Add `@media print` CSS to hide `.controls`, `.legend`, remove sticky/shadow effects, and avoid splitting dialogue lines across pages.

7. **Create audio when requested.**
   - Prefer `edge-tts` over macOS `say` (more natural).
   - Voices observed on macOS: `ja-JP-KeitaNeural`, `ja-JP-NanamiNeural`.
   - Assign one voice per speaker (male speaker → Keita, female speaker → Nanami).
   - Default `rate` = `"+0%"` (normal speed). Only slow down if the user asks.
   - Apply pronunciation overrides before TTS. Known overrides:
     - `相見積もり` → `あいみつもり` (never `そうみつもり`)
   - Export MP3 into the lesson folder.

8. **Create video when requested.**
   - Use the shared script `tu vung/source code/build_mp4.py --lesson "bài <N>"`.
   - macOS system volume is often full. Set `TMPDIR` to `tu vung/.tmp` on `/Volumes/DATA` before PyMuPDF / edge-tts / ffmpeg. Use `/usr/local/bin/python3` (has `edge-tts`, Pillow).
   - Slide-style MP4 (1920×1080): **two dialogue turns per slide** (田中 then 鈴木). Odd last line may stand alone.
   - Each turn: speaker name, **JP with ルビ**, English, Vietnamese. Leave extra space under the speaker name (`sp_size * 1.55` + full ruby gap) so ルビ does not sit on the name. Separate the two turns with a divider and ~22px padding.
   - While one speaker is talking, that turn stays full-color; the other turn is dimmed. Each clip duration is exactly that speaker's TTS (`ffprobe` + ffmpeg `-t`). Do **not** mux two MP3s onto one still image and do **not** use `-shortest` (it leaves silent video tail).
   - Do **not** add a "Cách đọc" block. Readings appear as ruby above kanji.
   - Put English in `<div class="en">` with `en-phrase` / `en-grammar` (same red/blue highlights). Strip HTML with `html.unescape` so `M&amp;A` becomes `M&A` on slides.
   - Preserve highlight colors: red vocab, blue grammar.
   - Use font `/Library/Fonts/Arial Unicode.ttf` on macOS.
   - JP line spacing: ~1.35× base + ~0.48× for ルビ. VI/EN 行間 ≈ 1.35×.
   - After concat, `ffprobe` the final MP3 and MP4; durations must match within ~0.2s.
   - Successful `mp4` stage auto-runs `clean` (see step 10). Do **not** rebuild bài 1 or bài 2 unless the user asks.

9. **(Optional) Push to GitHub.**
   - When the user asks to push, clone the target repo, create/checkout the branch (e.g. `bjt450-kotoba`), copy files into a `bai<N>/` folder, commit, and push. Requires `git_write` permission. Push only `index.html` + final MP3 + final MP4.

10. **Clean artifacts (mandatory after a successful build).**
    - Keep only: `index.html`, final MP3, final MP4, `segments.json`, `_ja.txt`.
    - Delete `tts_parts_edge_tokyo_multi_voice/`, `mp4_slides_edge_tokyo_multi_voice/`, `concat.txt`, `.DS_Store`, and one-off helpers (`source code/_*.py`, `.tmp/*.py`, `.tmp/*.txt`). Keep the empty `.tmp/` folder as `TMPDIR`.
    - The builder itself lives in `source code/build_mp4.py`, not per bài. `mp4` already calls `clean`; or run `--lesson "bài N" clean`.

## Output Layout

For vocabulary-PDF inputs, output next to (sibling of) the PDF folder:

```
tu vung/
├── tai lieu tu vung/                              (source PDF folder)
│   └── *.pdf
├── skill/bjt-kaiwa-builder/                       (this skill + grammar-coverage.md)
├── source code/
│   └── build_mp4.py                               (shared MP3/MP4 builder)
└── bài <N>/
    ├── index.html
    ├── segments.json
    ├── kaiwa_bai<N>_reading_edge_tokyo_multi_voice.mp3
    ├── kaiwa_bai<N>_reading_edge_tokyo_multi_voice.mp4
    └── kaiwa_bai<N>_reading_edge_tokyo_multi_voice_ja.txt
```

`tts_parts_*` and `mp4_slides_*` are build-only; delete them after MP4 succeeds.

Build from the shared script, pointing at the lesson folder (`TMPDIR` on DATA):

```
export TMPDIR="/Volumes/DATA/TN/2 TIENG NHAT/THAOJP/BJT/cụm từ cố định/tu vung/.tmp"
/usr/local/bin/python3 "source code/build_mp4.py" --lesson "bài 4" parse tts mp3 slides mp4
```

## Quality Checks

Run these before declaring done:

- `.line` count matches dialogue line count (typically 15~25).
- `.phrase` count = `.vi-phrase` count = number of target vocabulary items.
- If grammar overlay: `.grammar` count = `.vi-grammar` count = 15 assigned IDs from [grammar-coverage.md](grammar-coverage.md).
- After a new lesson, update the Used in column for those 15 IDs.
- No stray Kanji outside `<ruby>` in `.jp`, `.speaker`, `.scene-title`.
- Open/read one generated slide to verify font rendering.
- Verify one slide with a highlighted VI phrase preserves spaces around the red text.
- For grammar overlay: verify one slide shows both red (vocab) and blue (grammar) highlights.
- Verify JP slides show ルビ over kanji, no "Cách đọc" box, and an English line above Vietnamese.
- After MP4 build, `ffprobe` to confirm video+audio duration match.

## Reference

For CSS palette, HTML skeleton, the sample 37 expressions, sample 50-word bài 1, and the `build_mp4.py` layout, see [reference.md](reference.md). For the 117-pattern checklist, see [grammar-coverage.md](grammar-coverage.md).
