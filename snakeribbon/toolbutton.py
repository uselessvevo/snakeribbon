from __feature__ import snake_case

from PySide6 import QtCore
from PySide6 import QtWidgets

from snakeribbon.menu import RibbonMenu
from snakeribbon.constants import RibbonButtonStyle


class RibbonToolButton(QtWidgets.QToolButton):
    """Tool button that is showed in the ribbon."""

    _button_style: RibbonButtonStyle
    _large_button_icon_size = 64
    _medium_button_icon_size = 48
    _small_button_icon_size = 32
    _maximum_icon_size = 64

    def __init__(self, parent=None):
        """Create a new ribbon tool button.

        :param parent: The parent widget.
        """
        super().__init__(parent)

        # Styles
        self.set_button_style(RibbonButtonStyle.Large)
        self.set_auto_raise(True)
        self.set_focus_policy(QtCore.Qt.FocusPolicy.NoFocus)

    def set_maximum_icon_size(self, size: int):
        """Set the maximum icon size of the button.

        :param size: The maximum icon size of the button.
        """
        self._maximum_icon_size = size
        self.set_button_style(self._button_style)

    def maximum_icon_size(self) -> int:
        """Get the maximum icon size of the button.

        :return: The maximum icon size of the button.
        """
        return self._maximum_icon_size

    def set_button_style(self, style: RibbonButtonStyle):
        """Set the button style of the button.

        :param style: The button style of the button.
        """
        self._button_style = style
        if style == RibbonButtonStyle.Small:
            height = self._small_button_icon_size
            height = min(height, self._maximum_icon_size)
            self.set_icon_size(QtCore.QSize(height, height))
            self.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.set_style_sheet(
                """
                RibbonToolButton::menu-indicator {
                    subcontrol-origin: padding;
                    subcontrol-position: right;
                    right: -5px;
                }
                """
            )
        elif style == RibbonButtonStyle.Medium:
            height = self._medium_button_icon_size
            height = min(height, self._maximum_icon_size)
            self.set_icon_size(QtCore.QSize(height, height))
            self.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.set_style_sheet(
                """
                RibbonToolButton::menu-indicator {
                    subcontrol-origin: padding;
                    subcontrol-position: right;
                    right: -5px;
                }
                """
            )
        elif style == RibbonButtonStyle.Large:
            height = self._large_button_icon_size
            height = min(height, self._maximum_icon_size)
            self.set_icon_size(QtCore.QSize(height, height))
            self.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            self.set_style_sheet(
                """
                RibbonToolButton[popupMode="0"]::menu-indicator {
                    subcontrol-origin: padding;
                    subcontrol-position: bottom;
                    bottom: -5px;
                }
                RibbonToolButton[popupMode="2"]::menu-indicator {
                    subcontrol-origin: padding;
                    subcontrol-position: bottom;
                    bottom: -5px;
                }
                """
            )

    def button_style(self) -> RibbonButtonStyle:
        """Get the button style of the button.

        :return: The button style of the button.
        """
        return self._button_style

    def add_ribbon_menu(self) -> RibbonMenu:
        """Add a ribbon menu for the button.

        :return: The added ribbon menu.
        """
        menu = RibbonMenu()
        self.set_menu(menu)
        return menu
