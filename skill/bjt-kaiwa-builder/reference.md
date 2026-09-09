# BJT Kaiwa Builder Reference

## HTML Skeleton

```html
<body class="hide-ruby">
  <main>
    <header>
      <h1>BJT Kaiwa - Bài N (Từ vựng X + Ngữ pháp Y)</h1>
      <p class="subtitle">Bối cảnh hội thoại...</p>
      <div class="legend">
        <span><span class="swatch phrase">từ vựng</span> Từ vựng bài N</span>
        <span><span class="swatch grammar">ngữ pháp</span> Ngữ pháp BJT</span>
      </div>
      <div class="controls">
        <button id="toggleRuby">Hiện ルビ</button>
        <button id="toggleTranslation" class="secondary">Ẩn dịch</button>
        <button id="exportPdf" class="secondary">Xuất PDF</button>
      </div>
    </header>

    <section>
      <div class="scene-title"><ruby>場面<rt>ばめん</rt></ruby>: ...</div>
      <div class="dialogue">
        <div class="line">
          <div class="speaker"><ruby>田中<rt>たなか</rt></ruby></div>
          <div>
            <div class="jp">...<span class="phrase">...</span>...<span class="grammar">...</span>...</div>
            <div class="en">...<span class="en-phrase">...</span>...<span class="en-grammar">...</span>...</div>
            <div class="vi">...<span class="vi-phrase">...</span>...<span class="vi-grammar">...</span>...</div>
          </div>
        </div>
        <!-- more .line divs -->
      </div>
    </section>
  </main>
</body>
```

## CSS Palette (canonical)

```css
:root {
  --bg: #f7f3e8;
  --card: #fffdf8;
  --ink: #17233c;
  --muted: #687083;
  --line: #e7dcc4;
  --accent: #1f6feb;
  --phrase: #c62828;
  --phrase-bg: #fff2f2;
  --grammar: #1a73e8;
  --grammar-bg: #e8f0fe;
}

.phrase, .vi-phrase, .en-phrase {
  color: var(--phrase);
  background: var(--phrase-bg);
  border-radius: 8px;
  padding: 0 3px;
  font-weight: 850;
}

.grammar, .vi-grammar, .en-grammar {
  color: var(--grammar);
  background: var(--grammar-bg);
  border-radius: 8px;
  padding: 0 3px;
  font-weight: 850;
}

body.hide-ruby rt,
body.hide-translation .vi { display: none; }
```

## Sample 37 Expressions (screenshot source)

Use this list when the user refers to the first fixed-expression lesson from screenshots.

1. 二の足を踏む: Do dự, chần chừ
2. 足で稼ぐ: Tự đi lại/tự tìm kiếm bằng hành động thực tế
3. 相見積もりをとる: Lấy báo giá từ nhiều bên để so sánh
4. 勝手がわからない: Chưa quen cách làm
5. 粉骨砕身: Dốc hết sức lực
6. 個別ミーティング: Họp riêng
7. ポテンシャル: Tiềm năng
8. 打ち上げ: Tiệc liên hoan
9. うちうち: Nội bộ
10. 乾杯の音頭: Lời dẫn nâng ly
11. 顔を立てる: Giữ thể diện
12. 立役者: Người có công lớn
13. 大したもんだわ: Đáng nể thật
14. 年功序列: Chế độ thâm niên
15. ギリギリの線: Mức giới hạn cuối
16. 施主: Chủ đầu tư
17. ヒビが入る: Bị rạn nứt
18. 気を引き締める: Siết chặt tinh thần
19. 回覧を見る: Xem tài liệu lưu hành
20. こっちの島: Nhóm/bộ phận bên này
21. 消費が冷え込む: Tiêu dùng chững lại
22. セールスポイント: Điểm bán hàng nổi bật
23. 必要最小限に絞る: Thu gọn tối thiểu
24. 押し詰まる: Gần sát hạn
25. 段取りをする: Sắp xếp quy trình
26. 取り込み中: Đang bận
27. OL: Nữ nhân viên văn phòng
28. じゃ、その線で: Cứ theo hướng đó
29. 2本立て: Hai phương án song song
30. 外回り: Đi làm việc bên ngoài
31. さしでがましい: Đường đột
32. 申し上げるまでもありませんが: Không cần phải nói cũng biết
33. 何なりと: Bất cứ điều gì
34. まとめ役をする: Đóng vai trò điều phối
35. めどがつく: Thấy được hướng hoàn thành
36. 勝負の決め手: Yếu tố quyết thắng thua
37. 詰め / 最後の詰め: Khâu chốt cuối

## Sample Bài 1 (PDF vocab source, 50 words)

Bài 1 of `Thaolejp_BJT_Chinh phuc tu vung.pdf` (pages 5~14) contains 50 words:

アイコン, 挨拶, 相手, IT, ID, 相見積もり, アウトソーシング, アウトレット, 青写真, あおり, あおる, 赤字, 上がる, 商い, アクション, アクセス, 揚げ足を取る, 上げる, 朝一, 足が出る, 足踏み, 足元にも及ばない, 足を運ぶ, 足を引っ張る, 遊び, 頭打ち, 頭が痛い, 頭が切れる, 頭金, 頭割り, ～当たり, 悪化, 圧縮, ～宛, 当て, 宛先, 宛名, アドレス, アバウト, アピール, アプリケーション, アポ, 甘い, 洗い出し, 洗い出す, 予め, 改めて, 改める, 粗利益, アレンジ.

## Grammar overlay (117, checklist)

Do **not** reuse the old 15 "greatest hits" for every bài. Follow [grammar-coverage.md](grammar-coverage.md).

- Bài 1 and bài 2 already used: `#5,8,10,11,18,19,52,57,58,59,67,69,103,107,112` (do not rebuild).
- `#55 ～次第` = alias of `#5`.
- Bài 3 used: `#1,2,3,4,6,7,9,12,13,14,15,16,17,20,21`.
- **Bài 4 next 15:** `#22,23,24,25,26,27,28,29,30,31,32,33,34,35,36`.
- Later bài: next 15 unused IDs in PDF order. After all 117 appear once, pick least-used IDs.

## Audio/Video Notes

- edge-tts is a Python package: `pip install --user edge-tts`. List voices with `python3 -m edge_tts --list-voices | grep ja-JP`.
- On macOS the two available voices are `ja-JP-KeitaNeural` (M) and `ja-JP-NanamiNeural` (F).
- Default `rate="+0%"`, `pitch="+0Hz"`. Only slow down if the user asks.
- Font `/Library/Fonts/Arial Unicode.ttf` handles Japanese kanji, kana, and Vietnamese diacritics without missing-glyph boxes.
- 行間 (line spacing) for JP, VI, and readings blocks: **1.35× font size** (baseline-to-baseline). Compute via `int(font.size * 1.35)`, not from glyph bounding boxes.
- Video JP uses the same `<ruby>` markup as HTML: draw `rt` above each kanji unit. Do not add a "Cách đọc" footer.
- Add `<div class="en">` with `en-phrase` / `en-grammar`. Slide order: JP (ruby) → EN → VI.
- Speaker-name gap: after the name use `sp_size * 1.55`, then a full ruby gap before the JP line. Between two turns: ~22px + divider + ~22px.
- Decode entities with `html.unescape` when stripping tags (`M&amp;A` → `M&A`).
- Sync: one clip per spoken line, ffmpeg `-t <tts_duration>`. Never `-shortest` on a looped still + concatenated pair audio.
- After a successful `mp4` build the script deletes `tts_parts_*`, `mp4_slides_*`, and `concat.txt`. Keep `index.html` / MP3 / MP4 / `segments.json` / `_ja.txt`.
- Set `TMPDIR` to `tu vung/.tmp` on the DATA volume. Do not leave helper scripts in `.tmp/` or `source code/_*.py`.

## `build_mp4.py` Layout

The shared build script lives in `tu vung/source code/build_mp4.py`. It takes a lesson folder and writes MP3/MP4 + generated artifacts into that folder:

```
python3 "source code/build_mp4.py" --lesson "bài 2" [parse] [tts] [mp3] [slides] [mp4]
```

Stages can be composed:
- `parse` — HTML → `segments.json` + `_ja.txt`
- `tts` — one MP3 per segment via edge-tts (skips existing files)
- `mp3` — concat per-segment MP3s via `ffmpeg -f concat -c copy`
- `slides` — render 1920×1080 PNG per pair (2 câu/slide)
- `mp4` — mỗi câu một clip: cùng layout 2 câu, câu đang nói đậm / câu kia mờ, duration = đúng file TTS (`-t`), rồi concat; sau đó tự `clean`
- `clean` — xóa `tts_parts_*`, `mp4_slides_*`, `concat.txt`

Key parsing tricks:
- Line-splitter regex: `<div class="line">(.*?)(?=<div class="line">|</section>)` (avoids nested-div headache).
- To extract both `.phrase` and `.grammar` ranges in the same pass, pass a list of class names and match `<span class="(cls1|cls2)">...</span>`. Track them into separate range lists but share the same `text` counter so positions line up.
- Kana extraction: iterate `<ruby>(.*?)<rt>(.*?)</rt></ruby>` matches; append `base` to display, `reading` to kana, and any bare text between matches to both.

## Git Push Workflow

When the user asks to push the lesson:

- Target repo: `https://github.com/lehoact/nihongo_business.git`
- Branch convention: `bjt<total_words>-kotoba` (e.g. `bjt450-kotoba`) — shared across bài in that vocabulary series.
- Folder convention: `bai<N>/` at repo root.
- Push these three files: `index.html`, `kaiwa_bai<N>_reading_edge_tokyo_multi_voice.mp3`, `kaiwa_bai<N>_reading_edge_tokyo_multi_voice.mp4`.
- Requires `git_write` and `full_network` permissions.
- Commit message template: `Add BJT bai <N>: kaiwa <lines> câu (<vocab> từ vựng + <grammar> ngữ pháp)`.

## Known Pronunciation Overrides

- `相見積もり` must be read as `あいみつもり`, not `そうみつもり`. Replace in the TTS text before synthesis.
