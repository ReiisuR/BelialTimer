import re


BACKGROUND_COLOR_PATTERN = re.compile(
    r"(?P<prefix>\bbackground(?:-color)?\s*:\s*)"
    r"#(?P<color>[0-9a-fA-F]{6})"
)


def apply_background_opacity(widget, opacity):

    current_stylesheet = widget.styleSheet()
    applied_stylesheet = widget.property("opacity_applied_stylesheet")
    stylesheet = widget.property("opacity_base_stylesheet")
    if stylesheet is None or current_stylesheet != applied_stylesheet:
        stylesheet = current_stylesheet
        widget.setProperty("opacity_base_stylesheet", stylesheet)

    alpha = max(0, min(100, int(opacity))) / 100

    def replace_color(match):
        color = match.group("color")
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
        return "{}rgba({}, {}, {}, {:.2f})".format(
            match.group("prefix"),
            red,
            green,
            blue,
            alpha
        )

    adjusted_stylesheet = BACKGROUND_COLOR_PATTERN.sub(
        replace_color,
        stylesheet
    )
    widget.setStyleSheet(adjusted_stylesheet)
    widget.setProperty("opacity_applied_stylesheet", adjusted_stylesheet)
