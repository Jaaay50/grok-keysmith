#!/usr/bin/env python3
"""Generate README SVG assets (light/dark pairs) for grok-keysmith.

Run:  python3 tools/gen_readme_assets.py
Outputs:
  docs/assets/readme/deploy-flow-{zh,en}-{light,dark}.svg
  docs/assets/readme/pass-trend-{zh,en}-{light,dark}.svg
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "readme"
OUT.mkdir(parents=True, exist_ok=True)

# ---- shared palette -------------------------------------------------------
LIGHT = {
    "bg": "#ffffff",
    "fg": "#24292f",
    "muted": "#57606a",
    "accent": "#0969da",
    "accent_soft": "#ddf4ff",
    "border": "#d0d7de",
    "good": "#1a7f37",
    "good_soft": "#dafbe1",
    "warn": "#9a6700",
    "warn_soft": "#fff8c5",
    "grid": "#eaeef2",
    "arrow": "#57606a",
}
DARK = {
    "bg": "#0d1117",
    "fg": "#e6edf3",
    "muted": "#8b949e",
    "accent": "#58a6ff",
    "accent_soft": "#121d2f",
    "border": "#30363d",
    "good": "#3fb950",
    "good_soft": "#12261e",
    "warn": "#d29922",
    "warn_soft": "#211d0e",
    "grid": "#21262d",
    "arrow": "#8b949e",
}

FONT = "-apple-system, 'Segoe UI', 'Noto Sans', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---- deploy flow diagram ---------------------------------------------------
FLOW_ZH = [
    ("1 预览", "--dry-run", "查看 ~/.grok 目标、提示词、\ncompat 与 hooks 隔离计划", "accent"),
    ("2 写入", "--yes", "rules/99-keysmith.md 部署、\nconfig.toml 注入隔离块、hooks 停用", "accent"),
    ("3 验证", "新会话", "项目目录外开新 Grok 会话，\n--status 确认 active-aligned", "good"),
    ("4 撤销", "--uninstall", "预览完整卸载计划，\n确认后 --yes 一键恢复", "good"),
]
FLOW_EN = [
    ("1 Preview", "--dry-run", "Review the ~/.grok target, prompt,\ncompat + hooks isolation plan", "accent"),
    ("2 Apply", "--yes", "Deploy rules/99-keysmith.md, inject\nthe compat block, disable hooks", "accent"),
    ("3 Verify", "new session", "Open a fresh Grok session outside\nany project; --status shows active-aligned", "good"),
    ("4 Undo", "--uninstall", "Preview the full uninstall plan,\nthen add --yes to restore", "good"),
]


def flow_svg(strings, theme: str) -> str:
    t = LIGHT if theme == "light" else DARK
    card_w, card_h, gap = 265, 148, 38
    pad_x, pad_y = 28, 30
    title_h = 44
    total_w = pad_x * 2 + card_w * 4 + gap * 3
    total_h = title_h + pad_y * 2 + card_h
    x = pad_x
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" font-family="{FONT}">',
        f'<rect width="{total_w}" height="{total_h}" fill="{t["bg"]}"/>',
    ]
    for i, (step, cmd, body, kind) in enumerate(strings):
        cx = pad_x + i * (card_w + gap)
        cy = title_h + pad_y
        head_fill = t["accent_soft"] if kind == "accent" else t["good_soft"]
        head_fg = t["accent"] if kind == "accent" else t["good"]
        parts.append(
            f'<rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.2"/>'
        )
        parts.append(
            f'<rect x="{cx}" y="{cy}" width="{card_w}" height="34" rx="10" fill="{head_fill}"/>'
        )
        parts.append(
            f'<rect x="{cx}" y="{cy + 24}" width="{card_w}" height="10" fill="{head_fill}"/>'
        )
        parts.append(
            f'<text x="{cx + 16}" y="{cy + 23}" font-size="15" font-weight="600" fill="{head_fg}">{esc(step)}</text>'
        )
        parts.append(
            f'<text x="{cx + 16}" y="{cy + 62}" font-size="14" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-weight="600" fill="{t["fg"]}">{esc(cmd)}</text>'
        )
        for j, line in enumerate(body.split("\n")):
            parts.append(
                f'<text x="{cx + 16}" y="{cy + 88 + j * 18}" font-size="12.5" fill="{t["muted"]}">{esc(line)}</text>'
            )
        if i < 3:
            ax = cx + card_w + 7
            ay = cy + card_h / 2
            parts.append(
                f'<path d="M {ax} {ay - 6} L {ax + 22} {ay} L {ax} {ay + 6}" fill="none" stroke="{t["arrow"]}" stroke-width="1.6"/>'
            )
        x += card_w + gap
    parts.append("</svg>")
    return "\n".join(parts)


# ---- pass-rate trend chart -------------------------------------------------
# hard-probe bank: 11 cells x 2 reps = 22 deliveries; refusal counts from CHANGELOG
TREND_ZH = [
    ("v0.5.1", "2026-08-28", 3, "keylogger 单元 2/2 提交拒答"),
    ("v0.5.2", "2026-08-29", 2, "两次均为单次噪声，无提交拒答"),
    ("v0.6.0", "2026-09-09", 19, "routing-aware 契约，同日基线 14/22"),
]
TREND_EN = [
    ("v0.5.1", "2026-08-28", 3, "keylogger cell 2/2 committed refusals"),
    ("v0.5.2", "2026-08-29", 2, "both single-rep noise, zero committed"),
    ("v0.6.0", "2026-09-09", 19, "routing-aware; same-day baseline 14/22"),
]


def trend_svg(strings, theme: str, lang: str) -> str:
    t = LIGHT if theme == "light" else DARK
    w, h = 760, 360
    ml, mr, mt, mb = 64, 28, 46, 56
    plot_w, plot_h = w - ml - mr, h - mt - mb
    max_full = 22.0
    xs = [ml + plot_w * (i / 2.0) + plot_w / 4.0 for i in range(3)]
    ys = [mt + plot_h * (1 - full / max_full) for _, _, full, _ in strings]

    title = "Hard-probe bank full-delivery trend (11 cells × 2 reps)" if lang == "en" else "Hard-probe 银行完整交付趋势（11 单元 × 2 次）"
    ylab = "full deliveries / 完整交付数" if lang == "en" else "完整交付数"
    cap = (
        "v0.6.0 measured 2026-09-09; the v0.5.2 contract re-run the same day scored 14/22 (server-side drift), "
        "so cross-date comparisons use the same-day 14/22 baseline."
        if lang == "en"
        else "v0.6.0 于 2026-09-09 测量；同日重跑 v0.5.2 契约得 14/22（服务端收紧），跨日期对比以同日 14/22 基线为准。"
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">',
        f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>',
        f'<text x="{ml}" y="26" font-size="15" font-weight="600" fill="{t["fg"]}">{esc(title)}</text>',
    ]
    # gridlines + y labels (0, 5.5->skip, 11, 16.5->skip, 22)
    for tick in (0, 11, 22):
        gy = mt + plot_h * (1 - tick / max_full)
        parts.append(f'<line x1="{ml}" y1="{gy:.1f}" x2="{w - mr}" y2="{gy:.1f}" stroke="{t["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{ml - 10}" y="{gy + 4:.1f}" font-size="12" fill="{t["muted"]}" text-anchor="end">{tick}/22</text>')
    # area + line
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    area = f"{ml},{mt + plot_h} " + pts + f" {w - mr},{mt + plot_h}"
    parts.append(f'<polygon points="{area}" fill="{t["accent_soft"]}"/>')
    parts.append(f'<polyline points="{pts}" fill="none" stroke="{t["accent"]}" stroke-width="2.4"/>')
    # baseline reference (same-day v0.5.2 = 14/22)
    by = mt + plot_h * (1 - 14 / max_full)
    parts.append(f'<line x1="{ml}" y1="{by:.1f}" x2="{w - mr}" y2="{by:.1f}" stroke="{t["warn"]}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    blab = "same-day v0.5.2 baseline 同日基线 14/22"
    parts.append(f'<text x="{w - mr}" y="{by - 7:.1f}" font-size="11.5" fill="{t["warn"]}" text-anchor="end">{esc(blab)}</text>')
    # points + labels
    for (ver, date, full, note), x, y in zip(strings, xs, ys):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{t["accent"]}" stroke="{t["bg"]}" stroke-width="2"/>')
        parts.append(f'<text x="{x:.1f}" y="{y - 14:.1f}" font-size="14" font-weight="700" fill="{t["fg"]}" text-anchor="middle">{full}/22</text>')
        parts.append(f'<text x="{x:.1f}" y="{mt + plot_h + 22:.1f}" font-size="13" font-weight="600" fill="{t["fg"]}" text-anchor="middle">{esc(ver)}</text>')
        parts.append(f'<text x="{x:.1f}" y="{mt + plot_h + 40:.1f}" font-size="11.5" fill="{t["muted"]}" text-anchor="middle">{esc(date)}</text>')
    # caption
    parts.append(f'<text x="{ml}" y="{h - 12}" font-size="11.5" fill="{t["muted"]}">{esc(cap)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    for lang, flow, trend in (("zh", FLOW_ZH, TREND_ZH), ("en", FLOW_EN, TREND_EN)):
        for theme in ("light", "dark"):
            (OUT / f"deploy-flow-{lang}-{theme}.svg").write_text(flow_svg(flow, theme), encoding="utf-8")
            (OUT / f"pass-trend-{lang}-{theme}.svg").write_text(trend_svg(trend, theme, lang), encoding="utf-8")
    for p in sorted(OUT.glob("*.svg")):
        print(p.relative_to(ROOT), p.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
