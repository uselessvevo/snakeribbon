from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

import typing

from snakeribbon.category import (
    RibbonCategory,
    RibbonContextCategories,
    RibbonContextCategory,
    RibbonNormalCategory,
)
from snakeribbon.utils import DataFile
from snakeribbon.menu import RibbonMenu
from snakeribbon.tabbar import RibbonTabBar
from snakeribbon.constants import RibbonCategoryStyle, context_colors, RibbonIcon
from snakeribbon.titlewidget import RibbonApplicationButton, RibbonTitleWidget


class RibbonStackedWidget(QtWidgets.QStackedWidget):
    """Stacked widget that is used to display the ribbon."""

    def __init__(self, parent=None):
        """Create a new ribbon stacked widget.

        :param parent: The parent widget.
        """
        super().__init__(parent)
        effect = QtWidgets.QGraphicsDropShadowEffect()
        effect.set_offset(2, 2)
        self.set_graphics_effect(effect)


class RibbonBar(QtWidgets.QMenuBar):
    """The RibbonBar class is the top level widget that contains the ribbon."""

    #: Signal, the help button was clicked.
    sig_help_button_clicked = QtCore.Signal(bool)

    #: hide the ribbon bar automatically when the mouse press outside the ribbon bar
    _auto_hide_ribbon = False

    #: The categories of the ribbon.
    _categories: typing.Dict[str, RibbonCategory] = {}
    _context_category_count = 0

    #: Maximum rows
    _max_rows = 6

    #: Whether the ribbon is visible.
    _ribbon_visible = True

    #: heights of the ribbon elements
    _ribbon_height = 150

    #: current tab index
    _current_tab_index = 0

    def __init__(self, title: str = "Ribbon Bar Title", max_rows=6, parent=None):
        """Create a new ribbon.

        :param title: The title of the ribbon.
        :param max_rows: The maximum number of rows.
        :param parent: The parent widget of the ribbon.
        """
        super().__init__(parent)
        self._categories = {}
        self._max_rows = max_rows
        self._ribbon_title = title

    def init(self):
        self.set_fixed_height(self._ribbon_height)

        self._title_widget = RibbonTitleWidget(self._ribbon_title, self)
        self._stacked_widget = RibbonStackedWidget(self)

        # Main layout
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._main_layout.set_contents_margins(0, 0, 0, 0)
        self._main_layout.set_spacing(0)
        self._main_layout.add_widget(self._title_widget, 0)
        self._main_layout.add_widget(self._stacked_widget, 1)
        self._main_layout.set_size_constraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)

        # Connect signals
        self._title_widget.sig_help_button_clicked.connect(self.sig_help_button_clicked)
        self._title_widget.sig_collapse_ribbon_button_clicked.connect(self._collapse_button_clicked)
        self._title_widget.tab_bar().currentChanged.connect(self.show_category_by_index)  # type: ignore

    def auto_hide_ribbon(self) -> bool:
        """Return whether the ribbon bar is automatically hidden when the mouse is pressed outside the ribbon bar.

        :return: Whether the ribbon bar is automatically hidden.
        """
        return self._auto_hide_ribbon

    def set_auto_hide_ribbon(self, autoHide: bool):
        """Set whether the ribbon bar is automatically hidden when the mouse is pressed outside the ribbon bar.

        :param autoHide: Whether the ribbon bar is automatically hidden.
        """
        self._auto_hide_ribbon = autoHide

    def event_filter(self, a0: QtCore.QObject, a1: QtCore.QEvent) -> bool:
        if self._auto_hide_ribbon and a1.type() == QtCore.QEvent.Type.HoverMove:
            self.set_ribbon_visible(self.under_mouse())
        return super().event_filter(a0, a1)

    def action_at(self, QPoint):
        raise NotImplementedError("RibbonBar.action_at() is not implemented in the ribbon bar.")

    def action_geometry(self, QAction):
        raise NotImplementedError("RibbonBar.action_geometry() is not implemented in the ribbon bar.")

    def active_action(self):
        raise NotImplementedError("RibbonBar.active_action() is not implemented in the ribbon bar.")

    def add_menu(self, *__args):
        raise NotImplementedError("RibbonBar.add_menu() is not implemented in the ribbon bar.")

    def add_action(self, *__args):
        raise NotImplementedError("RibbonBar.add_action() is not implemented in the ribbon bar.")

    def add_separator(self):
        raise NotImplementedError("RibbonBar.add_separator() is not implemented in the ribbon bar.")

    def clear(self):
        raise NotImplementedError("RibbonBar.clear() is not implemented in the ribbon bar.")

    def corner_widget(self, corner=None, *args, **kwargs):
        raise NotImplementedError("RibbonBar.corner_widget() is not implemented in the ribbon bar.")

    def insert_menu(self, QAction, QMenu):
        raise NotImplementedError("RibbonBar.insert_menu() is not implemented in the ribbon bar.")

    def insert_separator(self, QAction):
        raise NotImplementedError("RibbonBar.insert_separator() is not implemented in the ribbon bar.")

    def is_default_up(self):
        raise NotImplementedError("RibbonBar.is_default_up() is not implemented in the ribbon bar.")

    def is_native_menu_bar(self):
        raise NotImplementedError("RibbonBar.is_native_menu_bar() is not implemented in the ribbon bar.")

    def set_active_action(self, QAction):
        raise NotImplementedError("RibbonBar.set_active_action() is not implemented in the ribbon bar.")

    def set_corner_widget(self, QWidget, corner=None, *args, **kwargs):
        raise NotImplementedError("RibbonBar.set_corner_widget() is not implemented in the ribbon bar.")

    def set_default_up(self, up):
        raise NotImplementedError("RibbonBar.set_default_up() is not implemented in the ribbon bar.")

    def set_native_menu_bar(self, bar):
        raise NotImplementedError("RibbonBar.set_native_menu_bar() is not implemented in the ribbon bar.")

    def application_option_button(self) -> RibbonApplicationButton:
        """Return the application button."""
        return self._title_widget.application_button()

    def set_application_text(self, text: str):
        return self._title_widget.application_button().set_text(text)

    def set_application_icon(self, icon: QtGui.QIcon):
        """Set the application icon.

        :param icon: The icon to set.
        """
        self._title_widget.application_button().set_icon(icon)

    def add_title_widget(self, widget: QtWidgets.QWidget):
        """Add a widget to the title widget.

        :param widget: The widget to add.
        """
        self._title_widget.add_title_widget(widget)

    def remove_title_widget(self, widget: QtWidgets.QWidget):
        """Remove a widget from the title widget.

        :param widget: The widget to remove.
        """
        self._title_widget.remove_title_widget(widget)

    def insert_title_widget(self, index: int, widget: QtWidgets.QWidget):
        """Insert a widget to the title widget.

        :param index: The index to insert the widget.
        :param widget: The widget to insert.
        """
        self._title_widget.insert_title_widget(index, widget)

    def add_file_menu(self) -> RibbonMenu:
        """Add a file menu to the ribbon."""
        return self.application_option_button().add_file_menu()

    def ribbon_height(self) -> int:
        """Get the total height of the ribbon.

        :return: The height of the ribbon.
        """
        return self._ribbon_height

    def set_ribbon_height(self, height: int):
        """Set the total height of the ribbon.

        :param height: The height to set.
        """
        self._ribbon_height = height
        self.set_fixed_height(height)

    def tab_bar(self) -> RibbonTabBar:
        """Return the tab bar of the ribbon.

        :return: The tab bar of the ribbon.
        """
        return self._title_widget.tab_bar()

    def quick_access_tool_bar(self) -> QtWidgets.QToolBar:
        """Return the quick access toolbar of the ribbon.

        :return: The quick access toolbar of the ribbon.
        """
        return self._title_widget.quick_access_tool_bar()

    def add_quick_access_button(self, button: QtWidgets.QToolButton):
        """Add a button to the quick access bar.

        :param button: The button to add.
        """
        button.set_auto_raise(True)
        self._title_widget.quick_access_tool_bar().add_widget(button)

    def set_quick_access_button_height(self, height: int):
        """Set the height of the quick access buttons.

        :param height: The height to set.
        """
        self._title_widget.set_quick_access_button_height(height)

    def title(self) -> str:
        """Return the title of the ribbon.

        :return: The title of the ribbon.
        """
        return self._title_widget.title()

    def set_title(self, title: str):
        """Set the title of the ribbon.

        :param title: The title to set.
        """
        self._title_widget.set_title(title)

    def set_title_widget_height(self, height: int):
        """Set the height of the title widget.

        :param height: The height to set.
        """
        self._title_widget.set_title_widget_height(height)

    def right_tool_bar(self) -> QtWidgets.QToolBar:
        """Return the right toolbar of the ribbon.

        :return: The right toolbar of the ribbon.
        """
        return self._title_widget.right_tool_bar()

    def add_right_tool_button(self, button: QtWidgets.QToolButton):
        """Add a widget to the right button bar.

        :param button: The button to add.
        """
        button.set_auto_raise(True)
        self._title_widget.add_right_tool_button(button)

    def set_right_tool_bar_height(self, height: int):
        """Set the height of the right buttons.

        :param height: The height to set.
        """
        self._title_widget.set_right_tool_bar_height(height)

    def help_ribbon_button(self) -> QtWidgets.QToolButton:
        """Return the help button of the ribbon.

        :return: The help button of the ribbon.
        """
        return self._title_widget.help_ribbon_button()

    def set_help_button_icon(self, icon: QtGui.QIcon):
        """Set the icon of the help button.

        :param icon: The icon to set.
        """
        self._title_widget.set_help_button_icon(icon)

    def remove_help_button(self):
        """Remove the help button from the ribbon."""
        self._title_widget.remove_help_button()

    def collapse_ribbon_button(self) -> QtWidgets.QToolButton:
        """Return the collapse ribbon button.

        :return: The collapse ribbon button.
        """
        return self._title_widget.collapse_ribbon_button()

    def set_collapse_button_icon(self, icon: QtGui.QIcon):
        """Set the icon of the min button.

        :param icon: The icon to set.
        """
        self._title_widget.set_collapse_button_icon(icon)

    def remove_collapse_button(self):
        """Remove the min button from the ribbon."""
        self._title_widget.remove_collapse_button()

    def category(self, name: str) -> RibbonCategory:
        """Return the category with the given name.

        :param name: The name of the category.
        :return: The category with the given name.
        """
        return self._categories[name]

    def categories(self) -> typing.Dict[str, RibbonCategory]:
        """Return a list of categories of the ribbon.

        :return: A dict of categories of the ribbon.
        """
        return self._categories

    def add_categories_by(
        self,
        data: typing.Dict[
            str,  # title of the category
            typing.Dict,  # data of the category
        ],
    ) -> typing.Dict[str, RibbonCategory]:
        """Add categories from a dict.

        :param data: The dict of categories. The dict is of the form:

            .. code-block:: python

                {
                    "category-title": {
                        "style": RibbonCategoryStyle.Normal,
                        "color": QtCore.Qt.red,
                        "panels": {
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
                        },
                    }
                }
        :return: A dict of categories of the ribbon.
        """
        categories = {}
        for title, category_data in data.items():
            style = category_data.get("style", RibbonCategoryStyle.Normal)
            color = category_data.get("color", None)
            categories[title] = self.add_category(title, style, color)
            categories[title].add_panels_by(category_data.get("panels", {}))
        return categories

    def add_category(
        self,
        title: str,
        style=RibbonCategoryStyle.Normal,
        color: QtGui.QColor = None,
    ) -> typing.Union[RibbonNormalCategory, RibbonContextCategory]:
        """Add a new category to the ribbon.

        :param title: The title of the category.
        :param style: The button style of the category.
        :param color: The color of the context category, only used if style is Context, if None, the default color
                      will be used.
        :return: The newly created category.
        """
        if title in self._categories:
            raise ValueError(f"Category with title {title} already exists.")
        if style == RibbonCategoryStyle.Context:
            if color is None:
                color = context_colors[self._context_category_count % len(context_colors)]
                self._context_category_count += 1
        category = (
            RibbonContextCategory(title, color, self)  # noqa
            if style == RibbonCategoryStyle.Context
            else RibbonNormalCategory(title, self)  # noqa
        )
        category.set_maximum_rows(self._max_rows)
        category.set_fixed_height(
            self._ribbon_height
            - self._main_layout.spacing() * 2
            - self._main_layout.contents_margins().top()
            - self._main_layout.contents_margins().bottom()
            - self._title_widget.height()
        )  # 4: extra space for drawing lines when debugging

        self._categories[title] = category
        self._stacked_widget.add_widget(category)

        if style == RibbonCategoryStyle.Normal:
            self._title_widget.tab_bar().add_tab(title, color)

        elif style == RibbonCategoryStyle.Context:
            category.hide()

        if len(self._categories) == 1:
            self._title_widget.tab_bar().set_current_index(1)
            self.show_category_by_index(1)

        return category

    def add_normal_category(self, title: str) -> RibbonNormalCategory:
        """Add a new category to the ribbon.

        :param title: The title of the category.
        :return: The newly created category.
        """
        return self.add_category(title, RibbonCategoryStyle.Normal)

    def add_context_category(
        self,
        title: str,
        color: typing.Union[QtGui.QColor, QtCore.Qt.GlobalColor] = QtCore.Qt.GlobalColor.blue,
    ) -> RibbonContextCategory:
        """Add a new context category to the ribbon.

        :param title: The title of the category.
        :param color: The color of the context category, if None, the default color will be used.
        :return: The newly created category.
        """
        return self.add_category(title, RibbonCategoryStyle.Context, color)

    def add_context_categories(
        self,
        name: str,
        titles: typing.List[str],
        color: typing.Union[QtGui.QColor, QtCore.Qt.GlobalColor] = QtCore.Qt.GlobalColor.blue,
    ) -> RibbonContextCategories:
        """Add a group of context categories with the same tab color to the ribbon.

        :param name: The name of the context categories.
        :param titles: The title of the category.
        :param color: The color of the context category, if None, the default color will be used.
        :return: The newly created category.
        """
        if color is None:
            color = context_colors[self._context_category_count % len(context_colors)]
            self._context_category_count += 1
        categories = RibbonContextCategories(
            name,
            color,
            {title: self.add_context_category(title, color) for title in titles},
            self,
        )
        return categories

    def show_category_by_index(self, index: int):
        """Show category by tab index

        :param index: tab index
        """
        self._current_tab_index = index
        title = self._title_widget.tab_bar().tab_text(index)  # 0 is the file tab
        if title in self._categories:
            self._stacked_widget.set_current_widget(self._categories[title])

    def show_context_category(self, category: typing.Union[RibbonContextCategory, RibbonContextCategories]):
        """Show the given category or categories, if it is not a context category, nothing happens.

        :param category: The category to show.
        """
        if isinstance(category, RibbonContextCategory):
            self._title_widget.tab_bar().add_tab(category.title(), category.color())
            self._title_widget.tab_bar().set_current_index(self._title_widget.tab_bar().count() - 1)
            self._stacked_widget.set_current_widget(category)
        elif isinstance(category, RibbonContextCategories):
            categories = category
            titles = list(categories.keys())
            self._title_widget.tab_bar().add_associated_tabs(categories.name(), titles, categories.color())
            self._title_widget.tab_bar().set_current_index(self._title_widget.tab_bar().count() - len(titles))
            self._stacked_widget.set_current_widget(categories[titles[0]])

    def hide_context_category(self, category: typing.Union[RibbonContextCategory, RibbonContextCategories]):
        """Hide the given category or categories, if it is not a context category, nothing happens.

        :param category: The category to hide.
        """
        if isinstance(category, RibbonContextCategory):
            self.tab_bar().remove_tab(self.tab_bar().index_of(category.title()))
        elif isinstance(category, RibbonContextCategories):
            categories = category
            for c in categories:
                self.tab_bar().remove_tab(self.tab_bar().index_of(c.title()))

    def category_visible(self, category: RibbonCategory) -> bool:
        """Return whether the category is shown.

        :param category: The category to check.

        :return: Whether the category is shown.
        """
        return category.title() in self._title_widget.tab_bar().tab_titles()

    def remove_category(self, category: RibbonCategory):
        """Remove a category from the ribbon.

        :param category: The category to remove.
        """
        self.tab_bar().remove_tab(self._title_widget.tab_bar().index_of(category.title()))
        self._stacked_widget.remove_widget(category)

    def remove_categories(self, categories: RibbonContextCategories):
        """Remove a list of categories from the ribbon.

        :param categories: The categories to remove.
        """
        for category in categories.values():
            self.remove_category(category)

    def set_current_category(self, category: RibbonCategory):
        """Set the current category.

        :param category: The category to set.
        """
        self._stacked_widget.set_current_widget(category)
        if category.title() in self._title_widget.tab_bar().tab_titles():
            self._title_widget.tab_bar().set_current_index(self._title_widget.tab_bar().index_of(category.title()))
        else:
            raise ValueError(
                f"Category {category.title()} is not in the ribbon, "
                f"please show the context category/categories first."
            )

    def current_category(self) -> RibbonCategory:
        """Return the current category.

        :return: The current category.
        """
        return self._categories[self._title_widget.tab_bar().tab_text(self._title_widget.tab_bar().current_index())]

    def minimum_size_hint(self) -> QtCore.QSize:
        """Return the minimum size hint of the widget.

        :return: The minimum size hint.
        """
        return QtCore.QSize(super().minimum_size_hint().width(), self._ribbon_height)

    def _collapse_button_clicked(self):
        self.tab_bar().currentChanged.connect(self.show_ribbon)  # type: ignore
        self.hide_ribbon() if self._stacked_widget.is_visible() else self.show_ribbon()

    def show_ribbon(self):
        """Show the ribbon."""
        if not self._ribbon_visible:
            self._ribbon_visible = True
            self.collapse_ribbon_button().set_tool_tip("Collapse Ribbon")
            self.collapse_ribbon_button().set_icon(QtGui.QIcon(DataFile(RibbonIcon.Up)))
            self._stacked_widget.set_visible(True)
            self.set_fixed_size(self.size_hint())

    def hide_ribbon(self):
        """Hide the ribbon."""
        if self._ribbon_visible:
            self._ribbon_visible = False
            self.collapse_ribbon_button().set_tool_tip("Expand Ribbon")
            self.collapse_ribbon_button().set_icon(QtGui.QIcon(DataFile(RibbonIcon.Down)))
            self._stacked_widget.set_visible(False)
            self.set_fixed_size(self.size_hint().width(), self._title_widget.size().height() + 5)  # type: ignore

    def ribbon_visible(self) -> bool:
        """Get the visibility of the ribbon.

        :return: True if the ribbon is visible, False otherwise.
        """
        return self._ribbon_visible

    def set_ribbon_visible(self, visible: bool):
        """Set the visibility of the ribbon.

        :param visible: True to show the ribbon, False to hide it.
        """
        self.show_ribbon() if visible else self.hide_ribbon()
