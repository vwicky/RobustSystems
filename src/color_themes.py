from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    app_bg: str
    text: str
    card_bg: str
    border: str
    accent: str
    button_hover: str
    button_disabled_bg: str
    button_disabled_text: str
    danger: str
    danger_hover: str
    danger_pressed: str
    danger_disabled_bg: str
    danger_disabled_text: str
    tab_bg: str
    tab_selected_bg: str
    progress_chunk: str
    log_bg: str
    log_text: str
    table_grid: str
    header_bg: str
    header_border: str


THEMES: dict[str, ThemePalette] = {
    "light": ThemePalette(
        app_bg="#F8F9FA",
        text="#2D3436",
        card_bg="#FFFFFF",
        border="#DDE3EA",
        accent="#0B6BC7",
        button_hover="#3A8DDE",
        button_disabled_bg="#A8B3BF",
        button_disabled_text="#EAF0F6",
        danger="#D92D20",
        danger_hover="#B42318",
        danger_pressed="#912018",
        danger_disabled_bg="#E4B8B4",
        danger_disabled_text="#FAFAFA",
        tab_bg="#EEF2F7",
        tab_selected_bg="#FFFFFF",
        progress_chunk="#00A884",
        log_bg="#111827",
        log_text="#E5E7EB",
        table_grid="#EEF2F7",
        header_bg="#F3F7FC",
        header_border="#E5ECF4",
    ),
    "dark": ThemePalette(
        app_bg="#111827",
        text="#E5E7EB",
        card_bg="#1F2937",
        border="#374151",
        accent="#60A5FA",
        button_hover="#3B82F6",
        button_disabled_bg="#4B5563",
        button_disabled_text="#9CA3AF",
        danger="#EF4444",
        danger_hover="#DC2626",
        danger_pressed="#B91C1C",
        danger_disabled_bg="#7F1D1D",
        danger_disabled_text="#FCA5A5",
        tab_bg="#0F172A",
        tab_selected_bg="#1F2937",
        progress_chunk="#10B981",
        log_bg="#030712",
        log_text="#E5E7EB",
        table_grid="#374151",
        header_bg="#111827",
        header_border="#374151",
    ),
    "ocean": ThemePalette(
        app_bg="#ECF7FF",
        text="#14324A",
        card_bg="#FFFFFF",
        border="#C5DEED",
        accent="#0D82B8",
        button_hover="#2A9ECF",
        button_disabled_bg="#9FBCCB",
        button_disabled_text="#E9F2F7",
        danger="#CF3F2E",
        danger_hover="#B93524",
        danger_pressed="#972E20",
        danger_disabled_bg="#E2B8B2",
        danger_disabled_text="#FAFAFA",
        tab_bg="#E2F0F8",
        tab_selected_bg="#FFFFFF",
        progress_chunk="#1AA782",
        log_bg="#102231",
        log_text="#E6F1F7",
        table_grid="#DDEBF3",
        header_bg="#EAF4FB",
        header_border="#D2E3EE",
    ),
    "forest": ThemePalette(
        app_bg="#DAD7CD",  # Dust Grey
        text="#344E41",  # Pine Teal
        card_bg="#A3B18A",  # Dry Sage
        border="#588157",  # Fern
        accent="#3A5A40",  # Hunter Green
        button_hover="#344E41",  # Pine Teal
        button_disabled_bg="#588157",  # Fern
        button_disabled_text="#DAD7CD",  # Dust Grey
        danger="#588157",  # Fern
        danger_hover="#3A5A40",  # Hunter Green
        danger_pressed="#344E41",  # Pine Teal
        danger_disabled_bg="#A3B18A",  # Dry Sage
        danger_disabled_text="#DAD7CD",  # Dust Grey
        tab_bg="#A3B18A",  # Dry Sage
        tab_selected_bg="#DAD7CD",  # Dust Grey
        progress_chunk="#588157",  # Fern
        log_bg="#344E41",  # Pine Teal
        log_text="#DAD7CD",  # Dust Grey
        table_grid="#A3B18A",  # Dry Sage
        header_bg="#DAD7CD",  # Dust Grey
        header_border="#588157",  # Fern
    ),
    "onyx": ThemePalette(
        app_bg="#171614",  # Onyx
        text="#9A8873",  # Dusty Taupe
        card_bg="#3A2618",  # Dark Coffee
        border="#37423D",  # Iron Grey
        accent="#754043",  # Bitter Chocolate
        button_hover="#9A8873",  # Dusty Taupe
        button_disabled_bg="#37423D",  # Iron Grey
        button_disabled_text="#9A8873",  # Dusty Taupe
        danger="#754043",  # Bitter Chocolate
        danger_hover="#3A2618",  # Dark Coffee
        danger_pressed="#171614",  # Onyx
        danger_disabled_bg="#37423D",  # Iron Grey
        danger_disabled_text="#9A8873",  # Dusty Taupe
        tab_bg="#3A2618",  # Dark Coffee
        tab_selected_bg="#171614",  # Onyx
        progress_chunk="#754043",  # Bitter Chocolate
        log_bg="#171614",  # Onyx
        log_text="#9A8873",  # Dusty Taupe
        table_grid="#37423D",  # Iron Grey
        header_bg="#3A2618",  # Dark Coffee
        header_border="#37423D",  # Iron Grey
    ),
    "tomato": ThemePalette(
        app_bg="#E8E9EB",  # Platinum
        text="#313638",  # Gunmetal
        card_bg="#E0DFD5",  # Soft Linen
        border="#F09D51",  # Sandy Brown
        accent="#F06543",  # Tomato
        button_hover="#F09D51",  # Sandy Brown
        button_disabled_bg="#E0DFD5",  # Soft Linen
        button_disabled_text="#313638",  # Gunmetal
        danger="#F06543",  # Tomato
        danger_hover="#313638",  # Gunmetal
        danger_pressed="#313638",  # Gunmetal
        danger_disabled_bg="#E0DFD5",  # Soft Linen
        danger_disabled_text="#313638",  # Gunmetal
        tab_bg="#E0DFD5",  # Soft Linen
        tab_selected_bg="#E8E9EB",  # Platinum
        progress_chunk="#F06543",  # Tomato
        log_bg="#313638",  # Gunmetal
        log_text="#E8E9EB",  # Platinum
        table_grid="#F09D51",  # Sandy Brown
        header_bg="#E8E9EB",  # Platinum
        header_border="#F09D51",  # Sandy Brown
    ),
}


def get_available_themes() -> tuple[str, ...]:
    return tuple(THEMES.keys())


def get_theme_palette(theme_name: str) -> ThemePalette:
    return THEMES.get(theme_name, THEMES["light"])


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB color, got: {hex_color}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgba(hex_color: str, alpha: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    clamped_alpha = max(0.0, min(1.0, alpha))
    return f"rgba({r}, {g}, {b}, {clamped_alpha:.2f})"


def build_stylesheet(theme_name: str) -> str:
    palette = get_theme_palette(theme_name)
    return f"""
QWidget {{ background: {palette.app_bg}; font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; font-size: 14px; color: {palette.text}; }}
QGroupBox {{ border: 1px solid {rgba(palette.border, 0.80)}; border-radius: 10px; margin-top: 14px; padding: 14px; background: {rgba(palette.card_bg, 0.72)}; font-weight: 600; }}
QGroupBox::title {{ left: 8px; color: {palette.accent}; }}
QPushButton {{ background: {palette.accent}; color: #FFFFFF; border: none; border-radius: 7px; padding: 9px 16px; font-weight: 600; }}
QPushButton:hover {{ background: {palette.button_hover}; }}
QPushButton:disabled {{ background: {palette.button_disabled_bg}; color: {palette.button_disabled_text}; }}
QPushButton#dangerButton {{ background: {palette.danger}; }}
QPushButton#dangerButton:hover {{ background: {palette.danger_hover}; }}
QPushButton#dangerButton:pressed {{ background: {palette.danger_pressed}; }}
QPushButton#dangerButton:disabled {{ background: {palette.danger_disabled_bg}; color: {palette.danger_disabled_text}; }}
QTabWidget::pane {{ border: 1px solid {rgba(palette.border, 0.9)}; border-radius: 4px; background: {rgba(palette.card_bg, 0.88)}; }}
QTabBar::tab {{ padding: 10px 18px; background: {rgba(palette.tab_bg, 0.78)}; border: 1px solid {rgba(palette.border, 0.85)}; border-bottom: none; margin-right: 4px; border-top-left-radius: 7px; border-top-right-radius: 7px; }}
QTabBar::tab:selected {{ background: {rgba(palette.tab_selected_bg, 0.92)}; color: {palette.accent}; font-weight: 700; }}
QProgressBar {{ border: 1px solid {rgba(palette.border, 0.85)}; border-radius: 7px; text-align: center; height: 20px; background: {rgba(palette.card_bg, 0.75)}; }}
QProgressBar::chunk {{ background: {palette.progress_chunk}; border-radius: 5px; }}
QPlainTextEdit {{ background: {palette.log_bg}; color: {palette.log_text}; border-radius: 8px; padding: 10px; font-family: "Cascadia Mono", "JetBrains Mono", Menlo, Consolas, monospace; font-size: 13px; }}
QTableWidget {{ border: 1px solid {rgba(palette.border, 0.85)}; border-radius: 10px; padding: 8px; margin: 3px; gridline-color: {palette.table_grid}; background: {rgba(palette.card_bg, 0.86)}; }}
QHeaderView::section {{ background: {rgba(palette.header_bg, 0.85)}; border: 1px solid {rgba(palette.header_border, 0.85)}; padding: 8px 10px; }}
QLabel {{ margin: 2px 1px; padding: 1px 0; }}
QWidget#paramRow {{ background: {rgba(palette.card_bg, 0.38)}; border: 1px solid {rgba(palette.border, 0.50)}; border-radius: 8px; }}
QLabel#paramIcon {{ background: {rgba(palette.accent, 0.18)}; border: 1px solid {rgba(palette.accent, 0.42)}; border-radius: 15px; color: {palette.accent}; font-size: 12px; font-weight: 700; }}
QLabel#paramKey {{ font-size: 13px; font-weight: 600; color: {rgba(palette.text, 0.78)}; letter-spacing: 0.2px; }}
QLabel#paramValue {{ font-size: 16px; font-weight: 700; color: {palette.text}; padding-left: 6px; }}
QLabel#paramKey, QLabel#paramValue {{ background: transparent; }}
""".strip()
