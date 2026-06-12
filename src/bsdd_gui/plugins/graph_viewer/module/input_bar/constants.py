from bsdd_gui.tool.theme import rgba


def get_style_sheet(tokens: dict[str, str]) -> str:
    return f"""
            QLineEdit {{
                color: {tokens["text"]};
                background: {rgba(tokens["surface"], 235)};
                border: 1px solid {tokens["border_strong"]};
                border-radius: 10px;
                padding: 10px 14px;
                selection-background-color: {tokens["accent"]};
                selection-color: {tokens["on_accent"]};
                font-weight: 600;
                letter-spacing: 0.2px;
            }}
            QLineEdit:focus {{
                border-color: {tokens["accent"]};
            }}
            """
