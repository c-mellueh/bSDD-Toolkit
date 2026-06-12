from bsdd_gui.tool.theme import rgba


def get_settings_style_sheet(tokens: dict[str, str]) -> str:
    return f"""
            QScrollArea {{ background: transparent; }}
            QWidget#qt_scrollarea_viewport {{ background: transparent; }}
            QWidget#scroll_content {{ background: transparent;}}
            QFrame#SettingsWidget {{
                background: {rgba(tokens["surface"], 215)};
                border: 1px solid {rgba(tokens["border_strong"], 160)};
                border-radius: 6px;
            }}
            QLabel#titleLabel {{
                font-weight: bold;
            }}
            QLabel {{
                color: {tokens["text"]};
            }}
            """
