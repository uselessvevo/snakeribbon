import typing

from __feature__ import snake_case

from PySide6 import QtCore, QtGui, QtWidgets


class RibbonTabBar(QtWidgets.QTabBar):
    """The TabBar for the title widget."""
    _context_category_top_margin = 0
    _context_category_dark_color_height = 5
    _tab_colors: typing.Dict[str, typing.Union[QtCore.Qt.GlobalColor, QtGui.QColor]] = {}
    _associated_tabs = {}

    def __init__(self, parent=None):
        """Create a new tab bar.

        :param parent: The parent widget.
        """
        super().__init__(parent)

        self.currentChanged.connect(self.change_color)
        self.set_draw_base(False)

    def index_of(self, tabName: str) -> int:
        """Return the index of the tab with the given name.

        :param tabName: The name of the tab.
        :return: The index of the tab.
        """
        for i in range(self.count()):
            if self.tab_text(i) == tabName:
                return i
        return -1

    def tab_titles(self) -> typing.List[str]:
        """Return the titles of all tabs.

        :return: The titles of all tabs.
        """
        return [self.tab_text(i) for i in range(self.count())]

    def add_tab(self, text: str, color: QtGui.QColor = None, *args, **kwargs) -> int:
        """Add a new tab to the tab bar.

        :param text: The text of the tab.
        :param color: The color of the tab.
        :return: The index of the tab.
        """
        self._tab_colors[text] = color
        return super().add_tab(text)

    def add_associated_tabs(self, name: str, texts: typing.List[str], color: QtGui.QColor) -> typing.List[int]:
        """Add associated multiple tabs which have the same color to the tab bar.

        :param name: The name of the context category.
        :param texts: The texts of the tabs.
        :param color: The color of the tabs.
        :return: The indices of the tabs.
        """
        self._tab_colors[name] = color
        for text in texts:
            self._associated_tabs[text] = [t for t in texts if t != text]
        return [self.add_tab(text, color) for text in texts]

    def remove_associated_tabs(self, titles: typing.List[str]) -> None:
        """Remove tabs with the given titles.

        :param titles: The titles of the tabs to remove.
        """
        tabTitles = self.tab_titles()
        for title in titles:
            if title in tabTitles:
                self.remove_tab(self.index_of(title))
                del self._tab_colors[title]
                if title in self._associated_tabs:
                    del self._associated_tabs[title]

    def current_tab_color(self) -> QtGui.QColor:
        """Current tab color

        :return: Current tab color
        """
        return self._tab_colors[self.tab_text(self.current_index())]

    def change_color(self, inx: int) -> None:
        """Change tab's color."""

        if self.count() > 0:
            currentTabText = self.tab_text(inx)
            currentTabColor = self._tab_colors[currentTabText]
            if currentTabColor is not None:
                self.set_style_sheet("RibbonTabBar::tab:selected {color: %s;}" % QtGui.QColor(currentTabColor).name())
            else:
                self.set_style_sheet("RibbonTabBar::tab:selected {color: black;}")
