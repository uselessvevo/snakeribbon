import typing

from __feature__ import snake_case
from PySide6 import QtCore, QtGui, QtWidgets

from snakeribbon.constants import RibbonIcon
from snakeribbon.menu import RibbonMenu
from snakeribbon.tabbar import RibbonTabBar
from snakeribbon.utils import DataFile


class RibbonApplicationButton(QtWidgets.QToolButton):
    """Application button in the ribbon bar."""

    def add_file_menu(self) -> RibbonMenu:
        """Add a new ribbon menu to the application button.

        :return: The new ribbon menu.
        """
        menu = RibbonMenu(self)
        self.set_popup_mode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.set_menu(menu)
        return menu


class RibbonTitleLabel(QtWidgets.QLabel):
    """Title label in the ribbon bar."""

    pass


class RibbonTitleWidget(QtWidgets.QFrame):
    """The title widget of the ribbon."""

    #: Signal, the help button was clicked.
    sig_help_button_clicked = QtCore.Signal(bool)

    #: Signal, the collapse button wa clicked.
    sig_collapse_ribbon_button_clicked = QtCore.Signal(bool)

    #: Buttons
    _quick_access_buttons = []
    _right_tool_buttons = []

    _quick_access_button_height = 20
    _right_button_height = 20

    # Mouse move events
    _start_point = None
    _window_point = None

    @typing.overload
    def __init__(self, title=None, parent=None):
        pass

    @typing.overload
    def __init__(self, parent=None):
        pass

    def __init__(self, *args, **kwargs):
        """Initialize the ribbon title widget.

        :param title: The title of the ribbon.
        :param parent: The parent widget.
        """
        if (args and not isinstance(args[0], QtWidgets.QWidget)) or ("title" in kwargs):
            title = args[0] if len(args) > 0 else kwargs.get("title", None)
            parent = args[1] if len(args) > 1 else kwargs.get("parent", None)
        else:
            title = "snakeribbon"
            parent = args[0] if len(args) > 0 else kwargs.get("parent", None)

        super().__init__(parent)
        # Tab bar layout
        self.set_size_policy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)  # type: ignore
        self._tab_bar_layout = QtWidgets.QHBoxLayout(self)
        self._tab_bar_layout.set_contents_margins(0, 0, 0, 0)
        self._tab_bar_layout.set_spacing(0)

        # Application
        self._application_button = RibbonApplicationButton()  # type: ignore
        self._application_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Application)))
        self._application_button.set_icon_size(QtCore.QSize(self._quick_access_button_height, self._quick_access_button_height))
        self._application_button.set_text("snakeribbon")
        self._application_button.set_tool_tip("snakeribbon")

        self._quick_access_tool_bar = QtWidgets.QToolBar()
        self._quick_access_tool_bar.set_icon_size(QtCore.QSize(self._quick_access_button_height, self._quick_access_button_height))
        self._quick_access_tool_bar.set_orientation(QtCore.Qt.Orientation.Horizontal)
        self._quick_access_tool_bar.set_movable(False)
        self._quick_access_tool_bar.add_widget(self._application_button)
        self._quick_access_tool_bar_widget = QtWidgets.QWidget()
        self._quick_access_tool_bar_layout = QtWidgets.QHBoxLayout(self._quick_access_tool_bar_widget)
        self._quick_access_tool_bar_layout.set_contents_margins(0, 0, 0, 0)
        self._quick_access_tool_bar_layout.set_spacing(0)
        self._quick_access_tool_bar_layout.add_widget(self._quick_access_tool_bar, 0, QtCore.Qt.AlignmentFlag.AlignBottom)

        # right toolbar
        self._right_tool_bar = QtWidgets.QToolBar()
        self._right_tool_bar.set_orientation(QtCore.Qt.Orientation.Horizontal)
        self._right_tool_bar.set_icon_size(QtCore.QSize(self._right_button_height, self._right_button_height))

        self._collapsable_ribbon_button = QtWidgets.QToolButton(self)
        self._collapsable_ribbon_button.set_icon_size(QtCore.QSize(self._right_button_height, self._right_button_height))
        self._collapsable_ribbon_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Up)))
        self._collapsable_ribbon_button.set_auto_raise(True)
        self._collapsable_ribbon_button.set_tool_tip("Collapse Ribbon")
        self._collapsable_ribbon_button.clicked.connect(self.sig_collapse_ribbon_button_clicked)  # type: ignore

        self._help_button = QtWidgets.QToolButton(self)
        self._help_button.set_icon_size(QtCore.QSize(self._right_button_height, self._right_button_height))
        self._help_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Help)))
        self._help_button.set_auto_raise(True)
        self._help_button.set_tool_tip("Help")
        self._help_button.clicked.connect(self.sig_help_button_clicked)  # type: ignore

        self.add_right_tool_button(self._collapsable_ribbon_button)
        self.add_right_tool_button(self._help_button)

        # category tab bar
        self._tab_bar = RibbonTabBar(self)
        self._tab_bar.set_expanding(False)
        self._tab_bar.set_size_policy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)  # type: ignore
        font = self._tab_bar.font()
        font.set_point_size(font.point_size() + 3)
        self._tab_bar.set_font(font)
        self._tab_bar.set_shape(QtWidgets.QTabBar.Shape.RoundedNorth)
        self._tab_bar.set_document_mode(True)

        # Title label
        self._title_label = RibbonTitleLabel(self)
        self._title_label.set_size_policy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)  # type: ignore
        self._title_label.set_alignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)  # type: ignore
        self._title_label.set_text(title)
        font = self._title_label.font()
        font.set_point_size(font.point_size() + 3)
        self._title_label.set_font(font)

        self._tab_bar_layout.add_widget(self._quick_access_tool_bar_widget, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        self._tab_bar_layout.add_widget(self._tab_bar, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        self._tab_bar_layout.add_widget(self._title_label, 1, QtCore.Qt.AlignmentFlag.AlignVCenter)
        self._tab_bar_layout.add_widget(self._right_tool_bar, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

    def application_button(self) -> RibbonApplicationButton:
        """Return the application button."""
        return self._application_button

    def set_application_icon(self, icon: QtGui.QIcon):
        """Set the application icon.

        :param icon: The icon to set.
        """
        self._application_button.set_icon(icon)

    def add_title_widget(self, widget: QtWidgets.QWidget):
        """Add a widget to the title layout.

        :param widget: The widget to add.
        """
        self._tab_bar_layout.add_widget(widget)

    def insert_title_widget(self, index: int, widget: QtWidgets.QWidget):
        """Insert a widget to the title layout.

        :param index: The index to insert the widget.
        :param widget: The widget to insert.
        """
        self._tab_bar_layout.insert_widget(index, widget)

    def remove_title_widget(self, widget: QtWidgets.QWidget):
        """Remove a widget from the title layout.

        :param widget: The widget to remove.
        """
        self._tab_bar_layout.remove_widget(widget)

    def tab_bar(self) -> RibbonTabBar:
        """Return the tab bar of the ribbon.

        :return: The tab bar of the ribbon.
        """
        return self._tab_bar

    def quick_access_tool_bar(self) -> QtWidgets.QToolBar:
        """Return the quick access toolbar of the ribbon.

        :return: The quick access toolbar of the ribbon.
        """
        return self._quick_access_tool_bar

    def quick_access_buttons(self) -> typing.List[QtWidgets.QToolButton]:
        """Return the quick access buttons of the ribbon.

        :return: The quick access buttons of the ribbon.
        """
        return self._quick_access_buttons

    def add_quick_access_button(self, button: QtWidgets.QToolButton):
        """Add a widget to the quick access bar.

        :param button: The button to add.
        """
        button.set_icon_size(QtCore.QSize(self._quick_access_button_height, self._quick_access_button_height))
        self._quick_access_buttons.append(button)
        self._quick_access_tool_bar.add_widget(button)

    def set_quick_access_button_height(self, height: int):
        """Set the height of the quick access buttons.

        :param height: The height to set.
        """
        self._quick_access_button_height = height
        self._application_button.set_icon(self._application_button.icon().pixmap(height, height))
        self._quick_access_tool_bar.set_icon_size(QtCore.QSize(height, height))

    def title(self) -> str:
        """Return the title of the ribbon.

        :return: The title of the ribbon.
        """
        return self._title_label.text()

    def set_title(self, title: str):
        """Set the title of the ribbon.

        :param title: The title to set.
        """
        self._title_label.set_text(title)

    def right_tool_bar(self) -> QtWidgets.QToolBar:
        """Return the right toolbar of the ribbon.

        :return: The right toolbar of the ribbon.
        """
        return self._right_tool_bar

    def add_right_tool_button(self, button: QtWidgets.QToolButton):
        """Add a widget to the right button bar.

        :param button: The button to add.
        """
        button.set_icon_size(QtCore.QSize(self._right_button_height, self._right_button_height))
        self._right_tool_buttons.append(button)
        self._right_tool_bar.add_widget(button)

    def set_right_tool_bar_height(self, height: int):
        """Set the height of the right buttons.

        :param height: The height to set.
        """
        self._right_button_height = height
        self._right_tool_bar.set_icon_size(QtCore.QSize(height, height))

    def help_ribbon_button(self) -> QtWidgets.QToolButton:
        """Return the help ribbon button.

        :return: The help ribbon button.
        """
        return self._help_button

    def set_help_button_icon(self, icon: QtGui.QIcon):
        """Set the icon of the help button.

        :param icon: The icon to set.
        """
        self._help_button.set_icon(icon)

    def remove_help_button(self):
        """Remove the help button from the ribbon."""
        self._help_button.set_visible(False)

    def set_collapse_button_icon(self, icon: QtGui.QIcon):
        """Set the icon of the min button.

        :param icon: The icon to set.
        """
        self._collapsable_ribbon_button.set_icon(icon)

    def remove_collapse_button(self):
        """Remove the min button from the ribbon."""
        self._collapsable_ribbon_button.set_visible(False)

    def collapse_ribbon_button(self) -> QtWidgets.QToolButton:
        """Return the collapse ribbon button.

        :return: The collapse ribbon button.
        """
        return self._collapsable_ribbon_button

    def set_title_widget_height(self, height: int):
        """Set the height of the title widget.

        :param height: The height to set.
        """
        self.set_quick_access_button_height(height)
        self.set_right_tool_bar_height(height)

    def top_level_widget(self) -> QtWidgets.QWidget:
        widget = self
        while widget.parentWidget():
            widget = widget.parentWidget()
        return widget

    def mouse_press_event(self, e: QtGui.QMouseEvent):
        self._start_point = e.pos()
        self._window_point = self.top_level_widget().frame_geometry().top_left()

    def mouse_move_event(self, e: QtGui.QMouseEvent):
        relpos = e.pos() - self._start_point if self._start_point else None
        self.top_level_widget().move(self._window_point + relpos) if self._window_point and relpos else None
        self.top_level_widget().window_handle().start_system_move()

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent):
        mainwindow = self.top_level_widget()
        mainwindow.show_normal() if mainwindow.is_maximized() else mainwindow.show_maximized()
