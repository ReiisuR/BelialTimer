"""Identidade visual global da Central de DGs."""

COLORS = {
    "background": "#17151C",
    "sidebar": "#1D1922",
    "surface": "#27202B",
    "surface_hover": "#342938",
    "border": "#574251",
    "primary": "#93485D",
    "primary_hover": "#AD5A71",
    "gold": "#C6A16B",
    "text": "#F4EDF1",
    "muted": "#B9A7B3",
}

BASE_QSS = """
QWidget#dashboard {
    background: #17151C;
    color: #F4EDF1;
    font-family: 'Segoe UI';
}
QFrame#sidebar { background: #1D1922; border-right: 1px solid #574251; }
QLabel#heading { color: #F4EDF1; font-size: 24px; font-weight: 700; }
QLabel#subheading { color: #B9A7B3; font-size: 12px; }
QLabel#cardTitle { color: #F4EDF1; font-size: 15px; font-weight: 700; }
QLabel#cardDetail { color: #B9A7B3; font-size: 11px; }
QFrame#dungeonCard {
    background: #27202B;
    border: 1px solid #574251;
    border-radius: 10px;
}
QLineEdit#search {
    background: #27202B;
    border: 1px solid #574251;
    border-radius: 7px;
    padding: 10px 12px;
    color: #F4EDF1;
}
QLineEdit#search:focus { border-color: #C6A16B; }
QPushButton {
    background: #93485D;
    border: 1px solid #AD5A71;
    border-radius: 6px;
    padding: 8px 12px;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton:hover { background: #AD5A71; }
QPushButton:disabled { background: #39313E; color: #A99AA4; border-color: #574251; }
QPushButton#filter { background: #27202B; border-color: #574251; }
QPushButton#filter:checked { background: #93485D; border-color: #C6A16B; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
"""
