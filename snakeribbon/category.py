from __feature__ import snake_case

import typing

from PySide6 import QtCore, QtGui, QtWidgets

from snakeribbon.constants import RibbonCategoryStyle, RibbonIcon
from snakeribbon.panel import RibbonPanel
from snakeribbon.separator import RibbonSeparator
from snakeribbon.utils import DataFile

if typing.TYPE_CHECKING:
    from .ribbonbar import RibbonBar  # noqa: F401


class RibbonCategoryLayoutButton(QtWidgets.QToolButton):
    """Previous/Next buttons in the category when the
    size is not enough for the widgets.
    """


class RibbonCategoryScrollArea(QtWidgets.QScrollArea):
    """Scroll area for the gallery"""


class RibbonCategoryScrollAreaContents(QtWidgets.QFrame):
    """Scroll area contents for the gallery"""


class RibbonCategoryLayoutWidget(QtWidgets.QFrame):
    """The category layout widget's category scroll area to arrange the widgets in the category."""

    display_options_button_clicked = QtCore.Signal()

    def __init__(self, parent=None):
        """Create a new category layout widget.

        :param parent: The parent widget.
        """
        super().__init__(parent)

        # Contents of the category scroll area
        self._category_scroll_area_contents = RibbonCategoryScrollAreaContents()  # type: ignore
        self._category_scroll_area_contents.set_size_policy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self._category_layout = QtWidgets.QHBoxLayout(self._category_scroll_area_contents)
        self._category_layout.set_contents_margins(0, 0, 0, 0)
        self._category_layout.set_spacing(0)
        self._category_layout.set_size_constraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)

        # Category scroll area
        self._category_scroll_area = RibbonCategoryScrollArea()  # type: ignore
        self._category_scroll_area.set_horizontal_scroll_bar_policy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._category_scroll_area.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._category_scroll_area.set_widget(self._category_scroll_area_contents)

        # Previous/Next buttons
        self._previous_button = RibbonCategoryLayoutButton(self)
        self._previous_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Backward)))
        self._previous_button.set_icon_size(QtCore.QSize(12, 12))
        self._previous_button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._previous_button.set_auto_raise(True)
        self._previous_button.clicked.connect(self.scroll_previous)  # type: ignore
        self._next_button = RibbonCategoryLayoutButton(self)
        self._next_button.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Forward)))
        self._next_button.set_icon_size(QtCore.QSize(12, 12))
        self._next_button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._next_button.set_auto_raise(True)
        self._next_button.clicked.connect(self.scroll_next)  # type: ignore

        # Add the widgets to the main layout
        self._main_layout = QtWidgets.QHBoxLayout(self)
        self._main_layout.set_contents_margins(0, 0, 0, 0)
        self._main_layout.set_spacing(0)
        self._main_layout.add_widget(self._previous_button, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        self._main_layout.add_widget(self._category_scroll_area, 1)
        self._main_layout.add_spacer_item(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding,
                                                               QtWidgets.QSizePolicy.Policy.Minimum))  # fmt: skip
        self._main_layout.add_widget(self._next_button, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        # Auto set the visibility of the scroll buttons
        self.auto_set_scroll_buttons_visible()

    def paint_event(self, a0: QtGui.QPaintEvent) -> None:
        """Override the paint event to draw the background."""
        super().paint_event(a0)
        self.auto_set_scroll_buttons_visible()

    def resize_event(self, a0: QtGui.QResizeEvent) -> None:
        """Override the resize event to resize the scroll area."""
        super().resize_event(a0)
        self.auto_set_scroll_buttons_visible()

    def auto_set_scroll_buttons_visible(self):
        """Set the visibility of the scroll buttons."""
        horizontal_scroll_bar = self._category_scroll_area.horizontal_scroll_bar()
        self._previous_button.set_visible(horizontal_scroll_bar.value() > horizontal_scroll_bar.minimum())
        self._next_button.set_visible(horizontal_scroll_bar.value() < horizontal_scroll_bar.maximum())
        self._previous_button.set_icon_size(QtCore.QSize(12, self.size().height() - 15))
        self._next_button.set_icon_size(QtCore.QSize(12, self.size().height() - 15))

    def scroll_previous(self):
        """Scroll the category to the previous widget."""
        horizontal_scroll_bar = self._category_scroll_area.horizontal_scroll_bar()
        horizontal_scroll_bar.set_value(horizontal_scroll_bar.value() - 50)
        self.auto_set_scroll_buttons_visible()

    def scroll_next(self):
        """Scroll the category to the next widget."""
        self._category_scroll_area.horizontal_scroll_bar().set_value(
            self._category_scroll_area.horizontal_scroll_bar().value() + 50
        )
        self.auto_set_scroll_buttons_visible()

    def add_widget(self, widget: QtWidgets.QWidget):
        """Add a widget to the category layout.

        :param widget: The widget to add.
        """
        self._category_layout.add_widget(widget)

    def remove_widget(self, widget: QtWidgets.QWidget):
        """Remove a widget from the category layout.

        :param widget: The widget to remove.
        """
        self._category_layout.remove_widget(widget)

    def take_widget(self, widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """Remove and return a widget from the category layout.

        :param widget: The widget to remove.
        :return: The widget that was removed.
        """
        self._category_layout.remove_widget(widget)
        return widget


class RibbonCategory(RibbonCategoryLayoutWidget):
    """The RibbonCategory is the logical grouping that represents the contents of a ribbon tab."""

    #: Title of the category
    _title: str
    #: The button style of the category.
    _style: RibbonCategoryStyle
    #: Panels
    _panels: typing.Dict[str, RibbonPanel]
    #: color of the context category
    _color: typing.Optional[QtGui.QColor]
    #: Maximum rows
    _max_rows: int = 6

    @typing.overload
    def __init__(
        self,
        title: str = "",
        style: RibbonCategoryStyle = RibbonCategoryStyle.Normal,
        color: QtGui.QColor = None,
        parent=None,
    ):
        pass

    @typing.overload
    def __init__(self, parent=None):
        pass

    def __init__(self, *args, **kwargs):
        """Create a new category.

        :param title: The title of the category.
        :param style: The button style of the category.
        :param color: The color of the context category.
        :param parent: The parent widget.
        """
        if (args and not isinstance(args[0], QtWidgets.QWidget)) or (
                "title" in kwargs or "style" in kwargs or "color" in kwargs
        ):
            title = args[0] if len(args) > 0 else kwargs.get("title", "")
            style = args[1] if len(args) > 1 else kwargs.get("style", RibbonCategoryStyle.Normal)
            color = args[2] if len(args) > 2 else kwargs.get("color", None)
            parent = args[3] if len(args) > 3 else kwargs.get("parent", None)
        else:
            title = ""
            style = RibbonCategoryStyle.Normal
            color = None
            parent = args[0] if len(args) > 0 else kwargs.get("parent", None)
        super().__init__(parent)
        self._title = title
        self._style = style
        self._panels = {}
        self._ribbon = parent  # type: RibbonBar
        self._color = color

    def set_maximum_rows(self, rows: int):
        """Set the maximum number of rows.

        :param rows: The maximum number of rows.
        """
        self._max_rows = rows

    def title(self) -> str:
        """Return the title of the category."""
        return self._title

    def set_category_style(self, style: RibbonCategoryStyle):
        """Set the button style of the category.

        :param style: The button style.
        """
        self._style = style
        self.repaint()

    def category_style(self) -> RibbonCategoryStyle:
        """Return the button style of the category.

        :return: The button style.
        """
        return self._style

    def add_panels_by(
        self,
        data: typing.Dict[
            str,  # title of the panel
            typing.Dict,  # data of the panel
        ],
    ) -> typing.Dict[str, RibbonPanel]:
        """Add panels from a dictionary.

        :param data: The dictionary. The keys are the titles of the panels. The value is a dictionary of
                     arguments. the argument showPanelOptionButton is a boolean to decide whether to show
                     the panel option button, the rest arguments are passed to the RibbonPanel.add_widgetsBy() method.
                     The dict is of the form:

                     .. code-block:: python

                        {
                            "panel-title": {
                                "showPanelOptionButton": True,
                                "widgets": {
                                    "widget-name": {
                                        "type": "Button",
                                        "args": (),
                                        "kwargs": {  # or "arguments" for backward compatibility
                                            "key1": "value1",
                                            "key2": "value2"
                                        }
                                    },
                                }
                            },
                        }
        :return: A dictionary of the newly created panels.
        """
        panels = {}
        for title, panel_data in data.items():
            show_panel_option_button = panel_data.get("show_panel_option_button", True)
            panels[title] = self.add_panel(title, show_panel_option_button)
            panels[title].add_widgets_by(panel_data.get("widgets", {}))
        return panels

    def add_panel(self, title: str, show_panel_option_button=True) -> RibbonPanel:
        """Add a new panel to the category.

        :param title: The title of the panel.
        :param show_panel_option_button: Whether to show the panel option button.
        :return: The newly created panel.
        """
        panel = RibbonPanel(title, max_rows=self._max_rows, show_panel_option_button=show_panel_option_button, parent=self)
        panel.set_fixed_height(
            self.height()
            - self._main_layout.spacing()
            - self._main_layout.contents_margins().top()
            - self._main_layout.contents_margins().bottom()
        )
        self._panels[title] = panel
        self.add_widget(panel)  # type: ignore
        self.add_widget(RibbonSeparator(width=10))  # type: ignore
        return panel

    def remove_panel(self, title: str):
        """Remove a panel from the category.

        :param title: The title of the panel.
        """
        # self._panelLayout.removeWidget(self._panels[title])
        self.remove_widget(self._panels[title])
        self._panels.pop(title)

    def take_panel(self, title: str) -> RibbonPanel:
        """Remove and return a panel from the category.

        :param title: The title of the panel.
        :return: The removed panel.
        """
        panel = self._panels[title]
        self.remove_panel(title)
        return panel

    def panel(self, title: str) -> RibbonPanel:
        """Return a panel from the category.

        :param title: The title of the panel.
        :return: The panel.
        """
        return self._panels[title]

    def panels(self) -> typing.Dict[str, RibbonPanel]:
        """Return all panels in the category.

        :return: The panels.
        """
        return self._panels


class RibbonNormalCategory(RibbonCategory):
    """A normal category."""

    def __init__(self, title: str, parent: QtWidgets.QWidget):
        """Create a new normal category.

        :param title: The title of the category.
        :param parent: The parent widget.
        """
        super().__init__(title, RibbonCategoryStyle.Normal, parent=parent)

    def set_category_style(self, style: RibbonCategoryStyle):
        """Set the button style of the category.

        :param style: The button style.
        """
        raise ValueError("You can not set the category style of a normal category.")


class RibbonContextCategory(RibbonCategory):
    """A context category."""

    def __init__(self, title: str, color: QtGui.QColor, parent: QtWidgets.QWidget):
        """Create a new context category.

        :param title: The title of the category.
        :param color: The color of the context category.
        :param parent: The parent widget.
        """
        super().__init__(title, RibbonCategoryStyle.Context, color=color, parent=parent)

    def set_category_style(self, style: RibbonCategoryStyle):
        """Set the button style of the category.

        :param style: The button style.
        """
        raise ValueError("You can not set the category style of a context category.")

    def color(self) -> QtGui.QColor:
        """Return the color of the context category.

        :return: The color of the context category.
        """
        return self._color

    def set_color(self, color: QtGui.QColor):
        """Set the color of the context category.

        :param color: The color of the context category.
        """
        self._color = color
        self._ribbon.repaint()

    def show_context_category(self):
        """Show the given category, if it is not a context category, nothing happens."""
        self._ribbon.show_context_category(self)

    def hide_context_category(self):
        """Hide the given category, if it is not a context category, nothing happens."""
        self._ribbon.hide_context_category(self)

    def category_visible(self) -> bool:
        """Return whether the category is shown.

        :return: Whether the category is shown.
        """
        return self._ribbon.category_visible(self)

    def set_category_visible(self, visible: bool):
        """Set the state of the category.

        :param visible: The state.
        """
        if visible:
            self.show_context_category()
        else:
            self.hide_context_category()


class RibbonContextCategories(typing.Dict[str, RibbonContextCategory]):
    """A list of context categories."""

    def __init__(
        self,
        name: str,
        color: QtGui.QColor,
        categories: typing.Dict[str, RibbonContextCategory],
        ribbon,
    ):
        self._name = name
        self._color = color
        self._ribbon = ribbon
        super().__init__(categories)

    def name(self) -> str:
        """Return the name of the context categories."""
        return self._name

    def set_name(self, name: str):
        """Set the name of the context categories."""
        self._name = name

    def color(self) -> QtGui.QColor:
        """Return the color of the context categories."""
        return self._color

    def set_color(self, color: QtGui.QColor):
        """Set the color of the context categories."""
        self._color = color

    def show_context_categories(self):
        """Show the categories"""
        self._ribbon.show_context_category(self)

    def hide_context_categories(self):
        """Hide the categories"""
        self._ribbon.hide_context_category(self)

    def categories_visible(self) -> bool:
        """Return whether the categories are shown."""
        for category in self.values():
            if category.category_visible():
                return True
        return False

    def set_categories_visible(self, visible: bool):
        """Set the state of the categories."""
        self.show_context_categories() if visible else self.hide_context_categories()
