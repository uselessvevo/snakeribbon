from __feature__ import snake_case

import typing

from PySide6 import QtCore, QtGui, QtWidgets

from snakeribbon.constants import RibbonIcon
from snakeribbon.menu import RibbonPermanentMenu
from snakeribbon.separator import RibbonHorizontalSeparator
from snakeribbon.toolbutton import RibbonToolButton
from snakeribbon.utils import DataFile


class RibbonPopupWidget(QtWidgets.QFrame):
    """The popup widget for the gallery widget."""


class RibbonGalleryListWidget(QtWidgets.QListWidget):
    """Gallery list widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_view_mode(QtWidgets.QListWidget.ViewMode.IconMode)
        self.set_resize_mode(QtWidgets.QListWidget.ResizeMode.Adjust)
        self.set_vertical_scroll_mode(QtWidgets.QListWidget.ScrollMode.ScrollPerPixel)
        self.set_horizontal_scroll_bar_policy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.set_icon_size(QtCore.QSize(64, 64))

    def resize_event(self, e: QtGui.QResizeEvent) -> None:
        """Resize the list widget."""
        super().resize_event(e)

    def scroll_to_next_row(self) -> None:
        """Scroll to the next row."""
        self.vertical_scroll_bar().set_value(self.vertical_scroll_bar().value() + self.vertical_scroll_bar().single_step())

    def scroll_to_previous_row(self) -> None:
        """Scroll to the previous row."""
        self.vertical_scroll_bar().set_value(self.vertical_scroll_bar().value() - self.vertical_scroll_bar().single_step())


class RibbonGalleryButton(QtWidgets.QToolButton):
    """Gallery button."""


class RibbonGalleryPopupListWidget(RibbonGalleryListWidget):
    """Gallery popup list widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)


class RibbonGallery(QtWidgets.QFrame):
    """A widget that displays a gallery of buttons."""

    _popup_window_size = QtCore.QSize(500, 500)
    _buttons: typing.List[RibbonToolButton] = []
    _popup_buttons: typing.List[RibbonToolButton] = []
    _popup_hide_on_click = False

    @typing.overload
    def __init__(self, minimum_width=800, popup_hide_on_click=False, parent=None):
        pass

    @typing.overload
    def __init__(self, parent=None):
        pass

    def __init__(self, *args, **kwargs):
        """Create a gallery.

        :param minimum_width: minimum width of the gallery
        :param popup_hide_on_click: hide on click flag
        :param parent: parent widget
        """
        if (args and not isinstance(args[0], QtWidgets.QWidget)) or (
            "minimum_width" in kwargs or "popup_hide_on_click" in kwargs
        ):
            minimum_width = args[0] if len(args) > 0 else kwargs.get("minimum_width", 800)
            popup_hide_on_click = args[1] if len(args) > 1 else kwargs.get("popup_hide_on_click", False)
            parent = args[2] if len(args) > 2 else kwargs.get("parent", None)
        else:
            minimum_width = 800
            popup_hide_on_click = False
            parent = args[0] if len(args) > 0 else kwargs.get("parent", None)
        super().__init__(parent)
        self.set_minimum_width(minimum_width)
        self._popup_hide_on_click = popup_hide_on_click

        self._main_layout = QtWidgets.QHBoxLayout(self)
        self._main_layout.set_contents_margins(5, 5, 5, 5)
        self._main_layout.set_spacing(5)

        self._up_button = RibbonGalleryButton(self)
        self._up_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Up)))
        self._up_button.set_icon_size(QtCore.QSize(24, 24))
        self._up_button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._up_button.set_auto_raise(True)
        self._down_button = RibbonGalleryButton(self)
        self._down_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Down)))
        self._down_button.set_icon_size(QtCore.QSize(24, 24))
        self._down_button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._down_button.set_auto_raise(True)
        self._more_button = RibbonGalleryButton(self)
        self._more_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.More)))
        self._more_button.set_icon_size(QtCore.QSize(24, 24))
        self._more_button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._more_button.set_auto_raise(True)
        self._scroll_button_layout = QtWidgets.QVBoxLayout()
        self._scroll_button_layout.set_contents_margins(0, 0, 0, 0)
        self._scroll_button_layout.set_spacing(2)
        self._scroll_button_layout.add_widget(self._up_button)
        self._scroll_button_layout.add_widget(self._down_button)
        self._scroll_button_layout.add_widget(self._more_button)

        self._list_widget = RibbonGalleryListWidget()
        self._main_layout.add_widget(self._list_widget)
        self._main_layout.add_layout(self._scroll_button_layout)

        self._up_button.clicked.connect(self._list_widget.scroll_to_previous_row)  # type: ignore
        self._down_button.clicked.connect(self._list_widget.scroll_to_next_row)  # type: ignore

        self._popup_widget = RibbonPopupWidget()  # type: ignore
        self._popup_widget.set_font(QtWidgets.QApplication.instance().font())  # type: ignore
        self._popup_widget.set_window_flag(QtCore.Qt.WindowType.Popup)
        self._popup_layout = QtWidgets.QVBoxLayout(self._popup_widget)
        self._popup_layout.set_contents_margins(5, 5, 5, 5)
        self._popup_layout.set_spacing(2)

        self._popup_list_widget = RibbonGalleryPopupListWidget()
        self._popup_layout.add_widget(self._popup_list_widget)
        self._popup_layout.add_widget(RibbonHorizontalSeparator())

        self._popup_menu = RibbonPermanentMenu()
        self._popup_menu.set_size_policy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)  # type: ignore
        self._popup_menu.action_added.connect(self._handle_popup_action)
        self._popup_layout.add_widget(self._popup_menu)

        self._more_button.clicked.connect(self.show_popup)  # type: ignore

    def _handle_popup_action(self, action: QtGui.QAction) -> None:
        """Handle a popup action."""
        if isinstance(action, QtGui.QAction):
            action.triggered.connect(self.hide_popup_widget)  # type: ignore

    def resize_event(self, a0: QtGui.QResizeEvent) -> None:
        """Resize the gallery."""
        height = self.height() - self._main_layout.contents_margins().top() - self._main_layout.contents_margins().bottom()
        self._up_button.set_fixed_size(height // 4, height // 3)  # type: ignore
        self._down_button.set_fixed_size(height // 4, height // 3)  # type: ignore
        self._more_button.set_fixed_size(height // 4, height // 3)  # type: ignore
        super().resize_event(a0)

    def popup_menu(self) -> RibbonPermanentMenu:
        """Return the popup menu."""
        return self._popup_menu

    def show_popup(self):
        """Show the popup window"""
        self._popup_widget.move(self.map_to_global(self.geometry().top_left()))
        self._popup_widget.resize(
            QtCore.QSize(
                max(self.popup_window_size().width(), self.width()), max(self.popup_window_size().height(), self.height())
            )
        )
        self._popup_menu.set_fixed_height(
            self._popup_widget.width()
            - self._popup_layout.contents_margins().left()
            - self._popup_layout.contents_margins().right()
        )
        self._popup_widget.show()

    def hide_popup_widget(self):
        """Hide the popup window"""
        self._popup_widget.hide()

    def popup_window_size(self):
        """Return the size of the popup window

        :return: size of the popup window
        """
        return self._popup_window_size

    def set_popup_window_size(self, size: QtCore.QSize):
        """Set the size of the popup window

        :param size: size of the popup window
        """
        self._popup_window_size = size

    def set_selected_button(self):
        """Set the selected button"""
        button = self.sender()
        if isinstance(button, RibbonToolButton):
            row = self._popup_buttons.index(button)
            self._list_widget.scroll_to(
                self._list_widget.model().index(row, 0), QtWidgets.QAbstractItemView.ScrollHint.EnsureVisible
            )
            if self._buttons[row].is_checkable():
                self._buttons[row].set_checked(not self._buttons[row].is_checked())

    def _add_widget(self, widget: QtWidgets.QWidget):
        """Add a widget to the gallery

        :param widget: widget to add
        """
        item = QtWidgets.QListWidgetItem()
        item.set_size_hint(widget.size_hint())
        self._list_widget.set_spacing((self.height() - item.size_hint().height()) // 2)
        self._list_widget.add_item(item)
        self._list_widget.set_item_widget(item, widget)

    def _add_popup_widget(self, widget: QtWidgets.QWidget):
        """Add a widget to the popup gallery

        :param widget: widget to add
        """
        item = QtWidgets.QListWidgetItem()
        item.set_size_hint(widget.size_hint())
        self._popup_list_widget.set_spacing((self.height() - item.size_hint().height()) // 2)
        self._popup_list_widget.add_item(item)
        self._popup_list_widget.set_item_widget(item, widget)

    def set_popup_hide_on_click(self, popup_hide_on_click: bool):
        """Set the hide on click flag

        :param popup_hide_on_click: hide on click flag
        """
        self._popup_hide_on_click = popup_hide_on_click

    def add_button(
        self,
        text: str = None,
        icon: QtGui.QIcon = None,
        slot=None,
        shortcut=None,
        tooltip=None,
        statusTip=None,
        checkable=False,
    ) -> typing.Tuple[RibbonToolButton, RibbonToolButton]:
        """Add a button to the gallery

        :param text: text of the button
        :param icon: icon of the button
        :param slot: slot to call when the button is clicked
        :param shortcut: shortcut of the button
        :param tooltip: tooltip of the button
        :param statusTip: status tip of the button
        :param checkable: checkable flag of the button.
        :return: the button and the popup button added
        """
        button = RibbonToolButton(self)
        popup_button = RibbonToolButton(self._popup_widget)
        if text is not None:
            button.set_text(text)
            popup_button.set_text(text)
        if icon is not None:
            button.set_icon(icon)
            popup_button.set_icon(icon)
        if slot is not None:
            button.clicked.connect(slot)  # type: ignore
            popup_button.clicked.connect(slot)  # type: ignore
        if shortcut is not None:
            button.set_shortcut(shortcut)
            popup_button.set_shortcut(shortcut)
        if tooltip is not None:
            button.set_tool_tip(tooltip)
            popup_button.set_tool_tip(tooltip)
        if statusTip is not None:
            button.set_status_tip(statusTip)
            popup_button.set_status_tip(statusTip)
        if checkable:
            button.set_checkable(True)
            popup_button.set_checkable(True)
        self._buttons.append(button)
        self._popup_buttons.append(popup_button)
        button.clicked.connect(lambda checked: popup_button.set_checked(checked))  # type: ignore
        if self._popup_hide_on_click:
            popup_button.clicked.connect(self.hide_popup_widget)  # type: ignore
        popup_button.clicked.connect(self.set_selected_button)  # type: ignore

        if text is None:
            button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
            popup_button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        else:
            button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            popup_button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self._add_widget(button)  # noqa
        self._add_popup_widget(popup_button)  # noqa
        return button, popup_button

    def addToggleButton(
        self,
        text: str = None,
        icon: QtGui.QIcon = None,
        slot=None,
        shortcut=None,
        tooltip=None,
        statusTip=None,
    ) -> typing.Tuple[RibbonToolButton, RibbonToolButton]:
        """Add a toggle button to the gallery

        :param text: text of the button
        :param icon: icon of the button
        :param slot: slot to call when the button is clicked
        :param shortcut: shortcut of the button
        :param tooltip: tooltip of the button
        :param statusTip: status tip of the button.
        :return: the button and the popup button added
        """
        return self.add_button(text, icon, slot, shortcut, tooltip, statusTip, True)
