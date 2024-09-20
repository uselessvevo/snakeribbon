import sys
from pathlib import Path

from PySide6 import QtGui, QtWidgets
from PySide6.QtGui import QIcon

from __feature__ import snake_case

from snakeribbon.ribbonbar import RibbonBar
from snakeribbon.constants import Large, RibbonIcon
from snakeribbon.constants import RowWise
from snakeribbon.utils import DataFile, ThemeFile


if __name__ == "__main__":
    root = Path(__file__).resolve().parent

    app = QtWidgets.QApplication(sys.argv)
    app.set_font(QtGui.QFont("Times New Roman", 8))

    window = QtWidgets.QMainWindow()
    window.set_window_title("Pie-Ribbon Menu Bar")
    window.set_window_icon(QIcon(str(root / "icons/word.png")))
    centralWidget = QtWidgets.QWidget()
    window.set_central_widget(centralWidget)
    layout = QtWidgets.QVBoxLayout(centralWidget)

    # Define Ribbon instance without rendering it
    ribbon = RibbonBar()

    # Set-up internal icons and their path
    DataFile.update_registry_data({
        RibbonIcon.Application: root / "icons/app.png",
        RibbonIcon.Backward: root / "icons/backward.png",
        RibbonIcon.Forward: root / "icons/forward.png",
        RibbonIcon.Up: root / "icons/up.png",
        RibbonIcon.Down: root / "icons/down.png",
        RibbonIcon.More: root / "icons/more.png",
        RibbonIcon.Linking: root / "icons/linking.png",
        RibbonIcon.Help: root / "icons/help.png"
    })
    ThemeFile.update_registry_data(ribbon, "themes/base.qss")
    ThemeFile.update_registry_data(ribbon, "themes/default.qss")

    # Initialize Ribbon
    ribbon.init()
    window.set_menu_bar(ribbon)

    layout.add_widget(QtWidgets.QTextEdit(), 1)
    ribbon.set_application_text("App")
    ribbon.set_application_icon(QIcon(DataFile(RibbonIcon.Application)))

    undo_button = QtWidgets.QToolButton()
    undo_button.set_auto_raise(True)
    undo_button.set_text("Button")
    undo_button.set_icon(QIcon(DataFile(RibbonIcon.Undo)))
    undo_button.set_tool_tip("Undo")
    ribbon.add_quick_access_button(undo_button)

    redo_button = QtWidgets.QToolButton()
    redo_button.set_auto_raise(True)
    redo_button.set_text("Button")
    redo_button.set_icon(QIcon(DataFile(RibbonIcon.Redo)))
    redo_button.set_tool_tip("Redo")
    ribbon.add_quick_access_button(redo_button)

    # Home category
    home_category = ribbon.add_category("Home")
    options_category = ribbon.add_category("Options")

    clipboard_panel = home_category.add_panel("Clipboard")
    clipboard_panel.panel_option_clicked.connect(lambda: print("SEX?"))
    paste_button = clipboard_panel.add_large_button(
        "Paste",
        icon=QIcon(str(root / "icons/paste.png")),
        tooltip="Paste"
    )
    paste_button.add_action(QtGui.QAction(QIcon(str(root / "icons/paste-special.png")), "Paste Special"))
    paste_button.add_action(QtGui.QAction(QIcon(str(root / "icons/paste-as-text.png")), "Paste as Text"))
    clipboard_panel.add_small_button(
        "Cut",
        icon=QIcon(str(root / "icons/close.png")),
        show_text=False,
        tooltip="Cut"
    )
    clipboard_panel.add_small_button(
        "Copy",
        icon=QIcon(str(root / "icons/close.png")),
        show_text=False,
        tooltip="Copy"
    )
    clipboard_panel.add_small_button(
        "Painter",
        icon=QIcon(str(root / "icons/close.png")),
        show_text=False,
        tooltip="Format Painter"
    )

    font_panel = home_category.add_panel("Font")
    font_panel.add_small_toggle_button(
        "Bold",
        icon=QIcon(str(root / "icons/bold.png")),
        show_text=False,
        tooltip="Bold"
    )
    font_panel.add_small_toggle_button(
        "Italic",
        icon=QIcon(str(root / "icons/italic.png")),
        show_text=False,
        tooltip="Italic"
    )
    font_panel.add_small_toggle_button(
        "Underline",
        icon=QIcon(str(root / "icons/underline.png")),
        show_text=False,
        tooltip="Underline"
    )
    font_panel.add_small_toggle_button(
        "Toggle Button",
        icon=QIcon(str(root / "icons/strikethrough.png")),
        show_text=False,
        tooltip="Toggle me!"
    )
    font_panel.add_horizontal_separator()
    font_panel.add_date_time_edit(row_span=Large, col_span=Large)
    font_size_combo_box = font_panel.add_list_widget(["8", "9", "10"], fixed_height=True, mode=RowWise)
    spinBox = font_panel.add_double_spin_box(fixed_height=True, mode=RowWise)

    window.show_maximized()
    window.show()
    sys.exit(app.exec())
