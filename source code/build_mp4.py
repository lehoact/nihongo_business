#!/usr/bin/env python3
"""Parse BJT kaiwa HTML → TTS MP3 + slide MP4.

Shared builder. Lives in `tu vung/source code/`. Lesson artifacts stay in `bài N/`.

Usage (from `tu vung/` or `source code/`):
  python3 build_mp4.py --lesson "bài 1" [parse] [tts] [mp3] [slides] [mp4] [clean]
  python3 build_mp4.py --lesson "bài 3" parse tts mp3 slides mp4
"""

from __future__ import annotations

import asyncio
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

VOICE_BY_SPEAKER = {
    "田中": "ja-JP-KeitaNeural",
    "鈴木": "ja-JP-NanamiNeural",
}

TTS_OVERRIDES = [
    ("相見積もり", "あいみつもり"),
]

FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
LINE_SPACING_RATIO = 1.35
RUBY_SIZE_RATIO = 0.42
RUBY_GAP_RATIO = 0.48

W, H = 1920, 1080
BG = (247, 243, 232)
CARD = (255, 253, 248)
INK = (23, 35, 60)
MUTED = (104, 112, 131)
LINE_C = (231, 220, 196)
PHRASE = (198, 40, 40)
GRAMMAR = (26, 115, 232)
SPKR_C = (31, 111, 235)

PATHS: "Paths | None" = None

SPAN_RE = re.compile(r'<span class="(phrase|grammar|vi-phrase|vi-grammar|en-phrase|en-grammar)">(.*?)</span>', re.S)
RUBY_RE = re.compile(r"<ruby>(.*?)<rt>(.*?)</rt></ruby>", re.S)


@dataclass
class Paths:
    root: Path
    html: Path
    segments: Path
    reading: Path
    tts_dir: Path
    slides_dir: Path
    mp3_out: Path
    mp4_out: Path


@dataclass
class Tok:
    base: str
    reading: str
    kind: str


def lesson_stem(lesson_dir: Path) -> str:
    m = re.search(r"(\d+)", lesson_dir.name)
    return f"bai{m.group(1)}" if m else "bai"


def resolve_lesson(raw: Path) -> Path:
    candidates = [raw]
    if not raw.is_absolute():
        tu_vung = Path(__file__).resolve().parent.parent
        candidates.append(tu_vung / raw)
    for cand in candidates:
        resolved = cand.resolve()
        if resolved.is_dir() and (resolved / "index.html").exists():
            return resolved
    tried = ", ".join(str(c.resolve()) for c in candidates)
    raise SystemExit(f"lesson folder not found (need index.html): {raw}\ntried: {tried}")


def make_paths(lesson_dir: Path) -> Paths:
    root = lesson_dir.resolve()
    prefix = f"kaiwa_{lesson_stem(root)}_reading_edge_tokyo_multi_voice"
    return Paths(
        root=root,
        html=root / "index.html",
        segments=root / "segments.json",
        reading=root / f"{prefix}_ja.txt",
        tts_dir=root / "tts_parts_edge_tokyo_multi_voice",
        slides_dir=root / "mp4_slides_edge_tokyo_multi_voice",
        mp3_out=root / f"{prefix}.mp3",
        mp4_out=root / f"{prefix}.mp4",
    )


def parse_cli(argv: list[str]) -> tuple[Path, list[str]]:
    lesson: Path | None = None
    stages: list[str] = []
    known = {"parse", "tts", "mp3", "slides", "mp4", "clean"}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--lesson", "-l"):
            if i + 1 >= len(argv):
                raise SystemExit("Usage: python3 build_mp4.py --lesson <bài N> [parse] [tts] [mp3] [slides] [mp4] [clean]")
            lesson = Path(argv[i + 1])
            i += 2
            continue
        if arg in known:
            stages.append(arg)
            i += 1
            continue
        if lesson is None:
            lesson = Path(arg)
            i += 1
            continue
        stages.append(arg)
        i += 1
    if lesson is None:
        raise SystemExit("Usage: python3 build_mp4.py --lesson <bài N> [parse] [tts] [mp3] [slides] [mp4] [clean]")
    return resolve_lesson(lesson), stages or ["parse"]


def _strip_tags(raw: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", raw))


def _strip_ruby(html: str) -> str:
    return re.sub(r"<rt>.*?</rt>", "", html, flags=re.S)


def _extract_with_ranges(
    html_frag: str, span_classes: list[str]
) -> tuple[str, dict[str, list[tuple[int, int]]]]:
    text = ""
    ranges: dict[str, list[tuple[int, int]]] = {c: [] for c in span_classes}
    alt = "|".join(re.escape(c) for c in span_classes)
    pattern = re.compile(rf'<span class="({alt})">(.*?)</span>', re.S)
    pos = 0
    for m in pattern.finditer(html_frag):
        text += _strip_tags(html_frag[pos : m.start()])
        content = _strip_tags(m.group(2))
        start = len(text)
        text += content
        ranges[m.group(1)].append((start, len(text)))
        pos = m.end()
    text += _strip_tags(html_frag[pos:])
    return text, ranges


def tokenize_html(html: str, kind: str = "plain") -> list[Tok]:
    tokens: list[Tok] = []
    pos = 0
    for m in SPAN_RE.finditer(html):
        tokens.extend(tokenize_plain(html[pos : m.start()], kind))
        inner_kind = m.group(1)
        if inner_kind.startswith("vi-") or inner_kind.startswith("en-"):
            inner_kind = inner_kind.split("-", 1)[1]
        tokens.extend(tokenize_plain(m.group(2), inner_kind))
        pos = m.end()
    tokens.extend(tokenize_plain(html[pos:], kind))
    return [t for t in tokens if t.base]


def tokenize_plain(html: str, kind: str) -> list[Tok]:
    tokens: list[Tok] = []
    pos = 0
    for m in RUBY_RE.finditer(html):
        before = _strip_tags(html[pos : m.start()])
        if before:
            tokens.append(Tok(before, "", kind))
        tokens.append(Tok(_strip_tags(m.group(1)), _strip_tags(m.group(2)), kind))
        pos = m.end()
    after = _strip_tags(html[pos:])
    if after:
        tokens.append(Tok(after, "", kind))
    return tokens


def parse_html() -> list[dict]:
    html = PATHS.html.read_text(encoding="utf-8")
    scene_m = re.search(r'<div class="scene-title">(.*?)</div>', html, re.S)
    scene = _strip_tags(_strip_ruby(scene_m.group(1))).strip() if scene_m else ""

    line_pattern = re.compile(
        r'<div class="line">(.*?)(?=<div class="line">|</section>)', re.S
    )
    segments: list[dict] = []
    for i, frag in enumerate(line_pattern.findall(html)):
        speaker_m = re.search(r'<div class="speaker">(.*?)</div>', frag, re.S)
        jp_m = re.search(r'<div class="jp">(.*?)</div>', frag, re.S)
        vi_m = re.search(r'<div class="vi">(.*?)</div>', frag, re.S)
        en_m = re.search(r'<div class="en">(.*?)</div>', frag, re.S)
        if not (speaker_m and jp_m and vi_m):
            continue

        speaker = _strip_tags(_strip_ruby(speaker_m.group(1))).strip()
        jp_html = jp_m.group(1)
        jp_stripped = _strip_ruby(jp_html)
        jp_text, jp_ranges = _extract_with_ranges(jp_stripped, ["phrase", "grammar"])
        vi_text, vi_ranges = _extract_with_ranges(vi_m.group(1), ["vi-phrase", "vi-grammar"])
        en_text, en_ranges = ("", {"en-phrase": [], "en-grammar": []})
        if en_m:
            en_text, en_ranges = _extract_with_ranges(en_m.group(1), ["en-phrase", "en-grammar"])

        tts_text = jp_text
        for src, dst in TTS_OVERRIDES:
            tts_text = tts_text.replace(src, dst)

        segments.append(
            {
                "idx": i,
                "scene": scene,
                "speaker": speaker,
                "voice": VOICE_BY_SPEAKER.get(speaker, "ja-JP-NanamiNeural"),
                "jp": jp_text.strip(),
                "jp_html": jp_html,
                "jp_phrase": jp_ranges["phrase"],
                "jp_grammar": jp_ranges["grammar"],
                "tts_text": tts_text.strip(),
                "vi": vi_text.strip(),
                "vi_phrase": vi_ranges["vi-phrase"],
                "vi_grammar": vi_ranges["vi-grammar"],
                "en": en_text.strip(),
                "en_phrase": en_ranges["en-phrase"],
                "en_grammar": en_ranges["en-grammar"],
            }
        )
    return segments


def write_reading_txt(segments: list[dict]) -> None:
    lines = []
    if segments and segments[0].get("scene"):
        lines.append(segments[0]["scene"])
        lines.append("")
    for s in segments:
        lines.append(f"[{s['speaker']}] {s['jp']}")
        lines.append("")
    PATHS.reading.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run_parse() -> list[dict]:
    if not PATHS.html.exists():
        raise SystemExit(f"missing {PATHS.html}")
    segments = parse_html()
    PATHS.segments.write_text(
        json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_reading_txt(segments)
    n_phrase = sum(len(s["jp_phrase"]) for s in segments)
    n_grammar = sum(len(s["jp_grammar"]) for s in segments)
    n_en = sum(1 for s in segments if s.get("en"))
    print(
        f"parsed {len(segments)} lines, "
        f"{n_phrase} phrase, {n_grammar} grammar, {n_en} en → {PATHS.segments.name}"
    )
    return segments


def load_segments() -> list[dict]:
    if PATHS.segments.exists():
        return json.loads(PATHS.segments.read_text(encoding="utf-8"))
    return run_parse()


async def tts_one(text: str, voice: str, out_path: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+0%", pitch="+0Hz")
    await communicate.save(str(out_path))


async def run_tts(segments: list[dict]) -> None:
    PATHS.tts_dir.mkdir(exist_ok=True)
    for s in segments:
        out = PATHS.tts_dir / f"{s['idx']:03d}_{s['speaker']}.mp3"
        if out.exists() and out.stat().st_size > 0:
            print(f"skip existing {out.name}")
            continue
        print(f"tts #{s['idx']:02d} {s['speaker']} {s['voice']}")
        await tts_one(s["tts_text"], s["voice"], out)


def _ffmpeg_concat(files: list[Path], out_path: Path) -> None:
    concat = out_path.parent / "concat.txt"
    concat.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in files), encoding="utf-8"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat),
        "-c",
        "copy",
        "-fflags",
        "+genpts",
        "-avoid_negative_ts",
        "make_zero",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def run_mp3(segments: list[dict]) -> None:
    files = [PATHS.tts_dir / f"{s['idx']:03d}_{s['speaker']}.mp3" for s in segments]
    missing = [p for p in files if not p.exists()]
    if missing:
        raise SystemExit(f"missing TTS files: {missing[0].name}")
    _ffmpeg_concat(files, PATHS.mp3_out)
    print(f"wrote {PATHS.mp3_out.name}")


def load_font(size: int):
    from PIL import ImageFont

    return ImageFont.truetype(FONT_PATH, size)


def line_step(font, ratio: float = LINE_SPACING_RATIO) -> int:
    return int(font.size * ratio)


def measure(draw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def build_runs(
    text: str,
    phrase_hl: list[tuple[int, int]],
    grammar_hl: list[tuple[int, int]],
) -> list[tuple[str, str]]:
    marks: list[tuple[int, int, str]] = []
    for s, e in phrase_hl:
        marks.append((s, e, "phrase"))
    for s, e in grammar_hl:
        marks.append((s, e, "grammar"))
    marks.sort(key=lambda x: x[0])
    runs: list[tuple[str, str]] = []
    pos = 0
    for s, e, kind in marks:
        if pos < s:
            runs.append((text[pos:s], "plain"))
        runs.append((text[s:e], kind))
        pos = e
    if pos < len(text):
        runs.append((text[pos:], "plain"))
    return runs or [(text, "plain")]


def wrap_runs(draw, runs: list[tuple[str, str]], font, max_width: int) -> list[list[tuple[str, str]]]:
    lines: list[list[tuple[str, str]]] = [[]]
    cur_w = 0
    for text, kind in runs:
        buf = ""
        for ch in text:
            w, _ = measure(draw, buf + ch, font)
            if cur_w + w > max_width and (buf or lines[-1]):
                if buf:
                    lines[-1].append((buf, kind))
                    buf = ""
                lines.append([])
                cur_w = 0
            buf += ch
        if buf:
            w, _ = measure(draw, buf, font)
            lines[-1].append((buf, kind))
            cur_w += w
    return [ln for ln in lines if ln]


def tok_width(draw, tok: Tok, font, rt_font) -> int:
    w, _ = measure(draw, tok.base, font)
    if tok.reading:
        rw, _ = measure(draw, tok.reading, rt_font)
        w = max(w, rw)
    return w


def wrap_tokens(draw, tokens: list[Tok], font, rt_font, max_width: int) -> list[list[Tok]]:
    lines: list[list[Tok]] = [[]]
    cur_w = 0
    for tok in tokens:
        w = tok_width(draw, tok, font, rt_font)
        if cur_w + w > max_width and lines[-1]:
            lines.append([])
            cur_w = 0
        lines[-1].append(tok)
        cur_w += w
    return [ln for ln in lines if ln]


def draw_runs_line(draw, runs, x: int, y: int, font, default_fill) -> None:
    colors = {
        "plain": default_fill,
        "phrase": PHRASE,
        "grammar": GRAMMAR,
    }
    for text, kind in runs:
        fill = colors.get(kind, default_fill)
        w, h = measure(draw, text, font)
        draw.text((x, y), text, font=font, fill=fill)
        x += w


def draw_ruby_line(draw, tokens: list[Tok], x: int, y: int, font, rt_font, default_fill) -> None:
    colors = {
        "plain": default_fill,
        "phrase": PHRASE,
        "grammar": GRAMMAR,
    }
    ruby_gap = int(font.size * RUBY_GAP_RATIO)
    for tok in tokens:
        fill = colors.get(tok.kind, default_fill)
        bw, bh = measure(draw, tok.base, font)
        rw = measure(draw, tok.reading, rt_font)[0] if tok.reading else 0
        box_w = max(bw, rw)
        if tok.reading:
            draw.text(
                (x + max(0, (box_w - rw) // 2), y - ruby_gap),
                tok.reading,
                font=rt_font,
                fill=fill if tok.kind != "plain" else MUTED,
            )
        draw.text((x + max(0, (box_w - bw) // 2), y), tok.base, font=font, fill=fill)
        x += box_w


def pair_segments(segments: list[dict]) -> list[list[dict]]:
    """Two dialogue turns per slide (田中+鈴木). Last odd line stays alone."""
    pairs: list[list[dict]] = []
    i = 0
    while i < len(segments):
        if i + 1 < len(segments):
            pairs.append([segments[i], segments[i + 1]])
            i += 2
        else:
            pairs.append([segments[i]])
            i += 1
    return pairs


def _draw_utterance(
    draw, seg: dict, x: int, y: int, max_w: int, compact: bool, dim: bool = False
) -> int:
    jp_size = 64
    en_size = 40
    vi_size = 42
    sp_size = 40
    jp_fill = (170, 176, 186) if dim else INK
    en_fill = (176, 182, 190) if dim else (55, 72, 92)
    vi_fill = (176, 182, 190) if dim else (57, 65, 80)
    sp_fill = (170, 176, 186) if dim else SPKR_C

    speaker_font = load_font(sp_size)
    draw.text((x, y), seg["speaker"], font=speaker_font, fill=sp_fill)
    y += int(sp_size * 1.55)

    jp_font = load_font(jp_size)
    rt_font = load_font(max(16, int(jp_font.size * RUBY_SIZE_RATIO)))
    tokens = tokenize_html(seg.get("jp_html") or seg["jp"])
    if dim:
        tokens = [Tok(t.base, t.reading, "plain") for t in tokens]
    jp_lines = wrap_tokens(draw, tokens, jp_font, rt_font, max_w)
    jp_step = line_step(jp_font) + int(jp_font.size * RUBY_GAP_RATIO)
    y += int(jp_font.size * RUBY_GAP_RATIO)
    for ln in jp_lines:
        draw_ruby_line(draw, ln, x, y, jp_font, rt_font, jp_fill)
        y += jp_step

    y += 8
    draw.line((x, y, x + max_w, y), fill=LINE_C, width=2)
    y += 12

    vi_font = load_font(vi_size)
    if dim:
        vi_runs = [(seg["vi"], "plain")]
    else:
        vi_runs = build_runs(seg["vi"], seg["vi_phrase"], seg["vi_grammar"])
    vi_lines = wrap_runs(draw, vi_runs, vi_font, max_w)
    vi_step = line_step(vi_font)
    for ln in vi_lines:
        draw_runs_line(draw, ln, x, y, vi_font, vi_fill)
        y += vi_step

    if seg.get("en"):
        y += 4
        en_font = load_font(en_size)
        if dim:
            en_runs = [(seg["en"], "plain")]
        else:
            en_runs = build_runs(seg["en"], seg.get("en_phrase") or [], seg.get("en_grammar") or [])
        en_lines = wrap_runs(draw, en_runs, en_font, max_w)
        en_step = line_step(en_font)
        for ln in en_lines:
            draw_runs_line(draw, ln, x, y, en_font, en_fill)
            y += en_step
    return y


def render_slide(segs: list[dict], out_path: Path, active: int | None = None) -> None:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    pad = 40
    draw.rounded_rectangle((pad, pad, W - pad, H - pad), radius=28, fill=CARD)

    title_font = load_font(26)
    scene = segs[0].get("scene") or ""
    draw.text((pad + 32, pad + 22), scene, font=title_font, fill=MUTED)

    inner_x = pad + 32
    inner_max_w = W - pad * 2 - 64
    y = pad + 70
    compact = len(segs) > 1
    for i, seg in enumerate(segs):
        if i:
            y += 22
            draw.line((inner_x, y, inner_x + inner_max_w, y), fill=LINE_C, width=2)
            y += 22
        dim = active is not None and i != active
        y = _draw_utterance(draw, seg, inner_x, y, inner_max_w, compact, dim=dim)

    img.save(out_path)


def run_slides(segments: list[dict]) -> None:
    PATHS.slides_dir.mkdir(exist_ok=True)
    for i, pair in enumerate(pair_segments(segments)):
        out = PATHS.slides_dir / f"{i:03d}.png"
        render_slide(pair, out)
        print(f"slide {out.name} ({'+'.join(s['speaker'] for s in pair)})")


def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(r.stdout.strip())


def run_mp4(segments: list[dict]) -> None:
    PATHS.slides_dir.mkdir(exist_ok=True)
    parts: list[Path] = []
    for i, pair in enumerate(pair_segments(segments)):
        for j, seg in enumerate(pair):
            png = PATHS.slides_dir / f"{i:03d}_{j}.png"
            render_slide(pair, png, active=j)
            mp3 = PATHS.tts_dir / f"{seg['idx']:03d}_{seg['speaker']}.mp3"
            if not mp3.exists():
                raise SystemExit(f"missing {mp3.name}")
            dur = _probe_duration(mp3)
            part = PATHS.slides_dir / f"{i:03d}_{j}.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-framerate",
                    "30",
                    "-i",
                    str(png),
                    "-i",
                    str(mp3),
                    "-c:v",
                    "libx264",
                    "-tune",
                    "stillimage",
                    "-c:a",
                    "aac",
                    "-pix_fmt",
                    "yuv420p",
                    "-t",
                    f"{dur:.3f}",
                    str(part),
                ],
                check=True,
                capture_output=True,
            )
            parts.append(part)
            print(f"part {part.name} {seg['speaker']} ({dur:.1f}s)")
    _ffmpeg_concat(parts, PATHS.mp4_out)
    print(f"wrote {PATHS.mp4_out.name}")


def run_clean() -> None:
    """Remove rebuildable intermediates; keep HTML / MP3 / MP4 / segments / _ja.txt."""
    for path in (PATHS.tts_dir, PATHS.slides_dir):
        if path.exists():
            shutil.rmtree(path)
            print(f"removed {path.name}/")
    leftover = PATHS.root / "concat.txt"
    if leftover.exists():
        leftover.unlink()
        print("removed concat.txt")


def main() -> None:
    global PATHS
    lesson, stages = parse_cli(sys.argv[1:])
    PATHS = make_paths(lesson)
    print(f"lesson {PATHS.root}")

    if "parse" in stages:
        segments = run_parse()
    else:
        segments = load_segments() if set(stages) - {"clean"} else []

    if "tts" in stages:
        asyncio.run(run_tts(segments))
    if "mp3" in stages:
        run_mp3(segments)
    if "slides" in stages:
        run_slides(segments)
    if "mp4" in stages:
        run_mp4(segments)
        run_clean()
    elif "clean" in stages:
        run_clean()


if __name__ == "__main__":
    main()
