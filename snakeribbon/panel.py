from __future__ import annotations
from __feature__ import snake_case

import re
import functools
from typing import Any, Callable, Dict, List, Union, overload

import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

from snakeribbon.constants import ColumnWise, RibbonIcon
from snakeribbon.constants import Large
from snakeribbon.constants import Medium
from snakeribbon.constants import RibbonButtonStyle
from snakeribbon.constants import RibbonSpaceFindMode
from snakeribbon.constants import Small
from snakeribbon.gallery import RibbonGallery
from snakeribbon.separator import RibbonSeparator
from snakeribbon.toolbutton import RibbonToolButton
from snakeribbon.utils import DataFile


class RibbonPanelTitle(QtWidgets.QLabel):
    """Widget to display the title of a panel."""


class RibbonGridLayoutManager(object):
    """Grid Layout Manager."""

    def __init__(self, rows: int):
        """Create a new grid layout manager.

        :param rows: The number of rows in the grid layout.
        """
        self.rows = rows
        self.cells = np.ones((rows, 1), dtype=bool)

    def request_cells(self, row_span: int = 1, col_span: int = 1, mode: RibbonSpaceFindMode = ColumnWise):
        """Request a number of available cells from the grid.

        :param row_span: The number of rows the cell should span.
        :param col_span: The number of columns the cell should span.
        :param mode: The mode of the grid.
        :return: row, col, the row and column of the requested cell.
        """
        if row_span > self.rows:
            raise ValueError("row_span is too large")
        if mode == ColumnWise:
            for row in range(self.cells.shape[0] - row_span + 1):
                for col in range(self.cells.shape[1] - col_span + 1):
                    if self.cells[row : row + row_span, col : col + col_span].all():
                        self.cells[row : row + row_span, col: col + col_span] = False
                        return row, col
        else:
            for col in range(self.cells.shape[1]):
                if self.cells[0, col:].all():
                    if self.cells.shape[1] - col < col_span:
                        self.cells = np.append(
                            self.cells, np.ones((self.rows, col_span - (self.cells.shape[1] - col)), dtype=bool), axis=1
                        )
                    self.cells[0, col:] = False
                    return 0, col
        cols = self.cells.shape[1]
        col_span1 = col_span
        if self.cells[:, -1].all():
            cols -= 1
            col_span1 -= 1
        self.cells = np.append(self.cells, np.ones((self.rows, col_span1), dtype=bool), axis=1)
        self.cells[:row_span, cols: cols + col_span] = False
        return 0, cols


class RibbonPanelItemWidget(QtWidgets.QFrame):
    """Widget to display a panel item."""

    def __init__(self, parent=None):
        """Create a new panel item.

        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.set_layout(QtWidgets.QVBoxLayout())
        self.layout().set_contents_margins(0, 0, 0, 0)
        self.layout().set_spacing(0)
        self.layout().set_alignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout().set_size_constraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.set_size_policy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)  # type: ignore

    def add_widget(self, widget):
        """Add a widget to the panel item.

        :param widget: The widget to add.
        """
        self.layout().add_widget(widget)


class RibbonPanelOptionButton(QtWidgets.QToolButton):
    """Button to display the options of a panel."""


class RibbonPanel(QtWidgets.QFrame):
    """Panel in the ribbon category."""

    #: maximal number of rows
    _max_rows: int = 6
    #: rows for large widgets
    _large_rows: int = 6
    #: rows for medium widgets
    _medium_rows: int = 3
    #: rows for small widgets
    _small_rows: int = 2
    #: GridLayout manager to request available cells.
    _grid_layout_manager: RibbonGridLayoutManager
    #: whether to show the panel option button
    _show_panel_option_button: bool

    #: widgets that are added to the panel
    _widgets: List[QtWidgets.QWidget] = []

    # height of the title widget
    _title_height: int = 15

    # Panel options signal
    panel_option_clicked = QtCore.Signal(bool)

    @overload
    def __init__(self, title: str = "", max_rows: int = 6, show_panel_option_button=True, parent=None):
        pass

    @overload
    def __init__(self, parent=None):
        pass

    def __init__(self, *args, **kwargs):
        """Create a new panel.

        :param title: The title of the panel.
        :param max_rows: The maximal number of rows in the panel.
        :param show_panel_option_button: Whether to show the panel option button.
        :param parent: The parent widget.
        """
        if (args and not isinstance(args[0], QtWidgets.QWidget)) or ("title" in kwargs or "max_rows" in kwargs):
            title = args[0] if len(args) > 0 else kwargs.get("title", "")
            max_rows = args[1] if len(args) > 1 else kwargs.get("max_rows", 6)
            show_panel_option_button = args[2] if len(args) > 2 else kwargs.get("show_panel_option_button", True)
            parent = args[3] if len(args) > 3 else kwargs.get("parent", None)
        else:
            title = ""
            max_rows = 6
            show_panel_option_button = True
            parent = args[0] if len(args) > 0 else kwargs.get("parent", None)
        super().__init__(parent)
        self._max_rows = max_rows
        self._large_rows = max_rows
        self._medium_rows = max(round(max_rows / 2), 1)
        self._small_rows = max(round(max_rows / 3), 1)
        self._grid_layout_manager = RibbonGridLayoutManager(self._max_rows)
        self._widgets = []
        self._show_panel_option_button = show_panel_option_button

        # Main layout
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._main_layout.set_contents_margins(0, 0, 0, 0)
        self._main_layout.set_spacing(0)

        # Actions layout
        self._actions_layout = QtWidgets.QGridLayout()
        self._actions_layout.set_contents_margins(5, 5, 5, 5)
        self._actions_layout.set_spacing(0)
        self._main_layout.add_layout(self._actions_layout, 1)

        # Title layout
        self._title_widget = QtWidgets.QWidget()
        self._title_widget.set_fixed_height(self._title_height)
        self._title_layout = QtWidgets.QHBoxLayout(self._title_widget)
        self._title_layout.set_contents_margins(0, 0, 0, 0)
        self._title_layout.set_spacing(0)
        self._title_label = RibbonPanelTitle()  # type: ignore
        self._title_label.set_text(title)
        self._title_label.set_alignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._title_layout.add_widget(self._title_label, 1)

        # Panel option button
        if show_panel_option_button:
            self._panel_option = RibbonPanelOptionButton()  # type: ignore
            self._panel_option.set_auto_raise(True)
            self._panel_option.set_icon(QtGui.QIcon(DataFile(RibbonIcon.Linking)))
            self._panel_option.set_icon_size(QtCore.QSize(self._title_height, self._title_height))
            self._panel_option.set_tool_tip("Panel options")
            self._panel_option.clicked.connect(self.panel_option_clicked)  # type: ignore
            self._title_layout.add_widget(self._panel_option, 0)

        self._main_layout.add_widget(self._title_widget, 0)

    def maximum_rows(self) -> int:
        """Return the maximal number of rows in the panel.

        :return: The maximal number of rows in the panel.
        """
        return self._max_rows

    def large_rows(self) -> int:
        """Return the number of span rows for large widgets.

        :return: The number of span rows for large widgets.
        """
        return self._large_rows

    def medium_rows(self) -> int:
        """Return the number of span rows for medium widgets.

        :return: The number of span rows for medium widgets.
        """
        return self._medium_rows

    def small_rows(self) -> int:
        """Return the number of span rows for small widgets.

        :return: The number of span rows for small widgets.
        """
        return self._small_rows

    def set_maximum_rows(self, max_rows: int):
        """Set the maximal number of rows in the panel.

        :param max_rows: The maximal number of rows in the panel.
        """
        self._max_rows = max_rows
        self._large_rows = max_rows
        self._medium_rows = max(round(max_rows / 2), 1)
        self._small_rows = max(round(max_rows / 3), 1)

    def set_large_rows(self, rows: int):
        """Set the number of span rows for large widgets.

        :param rows: The number of span rows for large widgets.
        """
        assert rows <= self._max_rows, "Invalid number of rows"
        self._large_rows = rows

    def set_medium_rows(self, rows: int):
        """Set the number of span rows for medium widgets.

        :param rows: The number of span rows for medium widgets.
        """
        assert 0 < rows <= self._max_rows, "Invalid number of rows"
        self._medium_rows = rows

    def set_small_rows(self, rows: int):
        """Set the number of span rows for small widgets.

        :param rows: The number of span rows for small widgets.
        """
        assert 0 < rows <= self._max_rows, "Invalid number of rows"
        self._small_rows = rows

    def default_row_span(self, row_span: Union[int, RibbonButtonStyle]) -> int:
        """Return the number of span rows for the given widget type.

        :param row_span: row span or type.
        :return: The number of span rows for the given widget type.
        """
        if not isinstance(row_span, RibbonButtonStyle):
            return row_span
        if row_span == Large:
            return self._large_rows
        elif row_span == Medium:
            return self._medium_rows
        elif row_span == Small:
            return self._small_rows
        else:
            raise ValueError("Invalid row span")

    def panel_option_button(self) -> RibbonPanelOptionButton:
        """Return the panel option button.

        :return: The panel option button.
        """
        return self._panel_option

    def set_panel_option_tool_tip(self, text: str):
        """Set the tooltip of the panel option button.

        :param text: The tooltip text.
        """
        self._panel_option.set_tool_tip(text)

    def row_height(self) -> int:
        """Return the height of a row."""
        return int(
            (
                    self.size().height()
                    - self._main_layout.contents_margins().top()
                    - self._main_layout.contents_margins().bottom()
                    - self._main_layout.spacing()
                    - self._title_widget.height()
                    - self._actions_layout.contents_margins().top()
                    - self._actions_layout.contents_margins().bottom()
                    - self._actions_layout.vertical_spacing() * (self._grid_layout_manager.rows - 1)
            )
            / self._grid_layout_manager.rows
        )

    def set_title(self, title: str):
        """Set the title of the panel.

        :param title: The title to set.
        """
        self._title_label.set_text(title)

    def title(self):
        """Get the title of the panel.

        :return: The title.
        """
        return self._title_label.text()

    def set_title_height(self, height: int):
        """Set the height of the title widget.

        :param height: The height to set.
        """
        self._title_height = height
        self._title_widget.set_fixed_height(height)
        self._panel_option.set_icon_size(QtCore.QSize(height, height))

    def title_height(self) -> int:
        """Get the height of the title widget.

        :return: The height of the title widget.
        """
        return self._title_height

    def add_widgets_by(self, data: Dict[str, Dict]) -> Dict[str, QtWidgets.QWidget]:
        """Add widgets to the panel.

        :param data: The data to add. The dict is of the form:

            .. code-block:: python

                {
                    "widget-name": {
                        "type": "Button",
                        "args": (),
                        "kwargs": {  # or "arguments" for backward compatibility
                            "key1": "value1",
                            "key2": "value2"
                        }
                    },
                }

            Possible types are: Button, SmallButton, MediumButton, LargeButton,
            ToggleButton, SmallToggleButton, MediumToggleButton, LargeToggleButton, ComboBox, FontComboBox,
            LineEdit, TextEdit, PlainTextEdit, Label, ProgressBar, SpinBox, DoubleSpinBox, DataEdit, TimeEdit,
            DateTimeEdit, TableWidget, TreeWidget, ListWidget, CalendarWidget, Separator, HorizontalSeparator,
            VerticalSeparator, Gallery.
        :return: A dictionary of the added widgets.
        """
        widgets = {}  # type: Dict[str, QtWidgets.QWidget]
        for key, widget_data in data.items():
            type = widget_data.pop("type", "").capitalize()
            method = getattr(self, f"add{type}", None)  # type: Callable
            assert callable(method), f"Method add{type} is not callable or does not exist"
            args = widget_data.get("args", ())
            kwargs = widget_data.get("kwargs", widget_data.get("arguments", {}))
            widgets[key] = method(*args, **kwargs)
        return widgets

    def add_widget(
        self,
        widget: QtWidgets.QWidget,
        *,
        row_span: Union[int, RibbonButtonStyle] = Small,
        col_span: int = 1,
        mode: RibbonSpaceFindMode = ColumnWise,
        alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter,
        fixed_height: Union[bool, float] = False,
    ) -> QtWidgets.QWidget | Any:
        """Add a widget to the panel.

        :param widget: The widget to add.
        :param row_span: The number of rows the widget should span, 2: small, 3: medium, 6: large.
        :param col_span: The number of columns the widget should span.
        :param mode: The mode to find spaces.
        :param alignment: The alignment of the widget.
        :param fixed_height: Whether to fix the height of the widget, it can be a boolean, a percentage or a fixed
                            height, when a boolean is given, the height is fixed to the maximum height allowed if the
                            value is True, when a percentage is given (0 < percentage < 1) the height is calculated
                            from the height of the maximum height allowed, depends on the number of rows to span. The
                            minimum height is 40% of the maximum height allowed.
        :return: The added widget.
        """
        row_span = self.default_row_span(row_span)
        self._widgets.append(widget)
        row, col = self._grid_layout_manager.request_cells(row_span, col_span, mode)
        maximumHeight = self.row_height() * row_span + self._actions_layout.vertical_spacing() * (row_span - 2)
        widget.set_maximum_height(maximumHeight)
        if fixed_height is True or fixed_height > 0:
            fixed_height = (
                int(fixed_height * maximumHeight)
                if 0 < fixed_height <= 1
                else fixed_height if 1 < fixed_height < maximumHeight else maximumHeight
            )
            fixed_height = max(fixed_height, 0.4 * maximumHeight)  # minimum height is 40% of the maximum height
            widget.set_fixed_height(fixed_height)
        item = RibbonPanelItemWidget(self)
        item.add_widget(widget)
        self._actions_layout.add_widget(item, row, col, row_span, col_span, alignment)  # type: ignore
        return widget

    add_small_widget = functools.partialmethod(add_widget, row_span=Small)
    add_medium_widget = functools.partialmethod(add_widget, row_span=Medium)
    add_large_widget = functools.partialmethod(add_widget, row_span=Large)

    def remove_widget(self, widget: QtWidgets.QWidget):
        """Remove a widget from the panel."""
        self._actions_layout.remove_widget(widget)

    def widget(self, index: int) -> QtWidgets.QWidget:
        """Get the widget at the given index.

        :param index: The index of the widget, starting from 0.
        :return: The widget at the given index.
        """
        return self._widgets[index]

    def widgets(self) -> List[QtWidgets.QWidget]:
        """Get all the widgets in the panel.

        :return: A list of all the widgets in the panel.
        """
        return self._widgets

    def add_button(
        self,
        text: str = None,
        icon: QtGui.QIcon = None,
        show_text: bool = True,
        slot: Callable = None,
        shortcut: (
            QtCore.Qt.Key | QtGui.QKeySequence | QtCore.QKeyCombination | QtGui.QKeySequence.StandardKey | str | int
        ) = None,
        tooltip: str = None,
        statusTip: str = None,
        checkable: bool = False,
        *,
        row_span: RibbonButtonStyle = Large,
        **kwargs,
    ) -> RibbonToolButton:
        """Add a button to the panel.

        :param text: The text of the button.
        :param icon: The icon of the button.
        :param show_text: Whether to show the text of the button.
        :param slot: The slot to call when the button is clicked.
        :param shortcut: The shortcut of the button.
        :param tooltip: The tooltip of the button.
        :param statusTip: The status tip of the button.
        :param checkable: Whether the button is checkable.
        :param row_span: The type of the button corresponding to the number of rows it should span.
        :param kwargs: keyword arguments to control the properties of the widget on the ribbon bar.

        :return: The button that was added.
        """
        assert isinstance(row_span, RibbonButtonStyle), "row_span must be an instance of RibbonButtonStyle"
        style = row_span
        button = RibbonToolButton(self)
        button.set_button_style(style)
        button.set_text(text) if text else None
        button.set_icon(icon) if icon else None
        button.clicked.connect(slot) if slot else None  # type: ignore
        button.set_shortcut(shortcut) if shortcut else None
        button.set_tool_tip(tooltip) if tooltip else None
        button.set_status_tip(statusTip) if statusTip else None
        maximumHeight = (
            self.height()
            - self._title_label.size_hint().height()
            - self._main_layout.spacing()
            - self._main_layout.contents_margins().top()
            - self._main_layout.contents_margins().bottom()
        )
        button.set_maximum_height(maximumHeight)
        if style == Large:
            font_size = max(button.font().point_size() * 4 / 3, button.font().pixel_size())
            arrow_size = font_size
            maximum_icon_size = max(maximumHeight - font_size * 2 - arrow_size, 48)
            button.set_maximum_icon_size(int(maximum_icon_size))
        if not show_text:
            button.set_tool_button_style(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        button.set_checkable(checkable)
        kwargs["row_span"] = (
            self.default_row_span(Small)
            if style == Small
            else self.default_row_span(Medium) if style == Medium else self.default_row_span(Large)
        )
        self.add_widget(button, **kwargs)  # noqa
        return button

    add_small_button = functools.partialmethod(add_button, row_span=Small)
    add_medium_button = functools.partialmethod(add_button, row_span=Medium)
    add_large_button = functools.partialmethod(add_button, row_span=Large)
    add_toggle_button = functools.partialmethod(add_button, checkable=True)
    add_small_toggle_button = functools.partialmethod(add_toggle_button, row_span=Small)
    add_medium_toggle_button = functools.partialmethod(add_toggle_button, row_span=Medium)
    add_large_toggle_button = functools.partialmethod(add_toggle_button, row_span=Large)

    def add_ribbon_widget(
        self,
        *args,
        cls,
        initializer: Callable = None,
        row_span: Union[int, RibbonButtonStyle] = Small,
        col_span: int = 1,
        mode: RibbonSpaceFindMode = ColumnWise,
        alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter,
        fixed_height: Union[bool, float] = False,
        **kwargs,
    ) -> QtWidgets.QWidget:
        """Add any widget to the panel.

        :param cls: The class of the widget to add.
        :param initializer: The initializer function of the widget to add.
        :param args: The arguments passed to the initializer.
        :param row_span: The number of rows the widget should span, 2: small, 3: medium, 6: large.
        :param col_span: The number of columns the widget should span.
        :param mode: The mode to find spaces.
        :param alignment: The alignment of the widget.
        :param fixed_height: Whether to fix the height of the widget, it can be a boolean, a percentage or a fixed
                            height, when a boolean is given, the height is fixed to the maximum height allowed if the
                            value is True, when a percentage is given (0 < percentage < 1) the height is calculated
                            from the height of the maximum height allowed, depends on the number of rows to span. The
                            minimum height is 40% of the maximum height allowed.
        :param kwargs: The keyword arguments are passed to the initializer
        """
        widget = cls(self)
        if callable(initializer):
            initializer(widget, *args, **kwargs)
        elif args or kwargs:
            raise ValueError("Arguments are provided but the initializer is not set")
        return self.add_widget(
            widget=widget,
            row_span=row_span,
            col_span=col_span,
            mode=mode,
            alignment=alignment,
            fixed_height=fixed_height
        )

    def __getattr__(self, method: str) -> Callable:
        """Get the dynamic method `add[Small|Medium|Large][Widget]`.

        :param method: The name of the method to get.
        :return: The method of the widget to add.
        """
        # Match the method name
        match = re.match(r"add(Small|Medium|Large)(\w+)", method)
        assert match, f"Invalid method name: {method!s}"

        # Get the widget class and the size
        size = match.group(1)
        base_method_name = f"add{match.group(2)}"
        assert hasattr(self, base_method_name), f"Invalid method name {base_method_name}"

        # Get the base method
        base_method = getattr(self, base_method_name)
        row_span = Small if size == "Small" else Medium if size == "Medium" else Large

        # Create the new method
        return functools.partial(base_method, row_span=row_span)

    add_check_box = functools.partialmethod(
        add_ribbon_widget, cls=QtWidgets.QCheckBox, initializer=QtWidgets.QCheckBox.set_text
    )
    add_combo_box = functools.partialmethod(
        add_ribbon_widget, cls=QtWidgets.QComboBox, initializer=QtWidgets.QComboBox.add_items
    )
    add_line_edit = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QLineEdit)
    add_text_edit = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QTextEdit)
    add_plain_text_edit = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QPlainTextEdit)
    add_label = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QLabel, initializer=QtWidgets.QLabel.set_text)
    add_progress_bar = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QProgressBar)
    add_slider = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QSlider)
    add_spin_box = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QSpinBox)
    add_double_spin_box = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QDoubleSpinBox)
    add_date_edit = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QDateEdit)
    add_time_edit = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QTimeEdit)
    add_date_time_edit = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QDateTimeEdit)
    add_table_widget = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QTableWidget, row_span=Large)
    add_tree_widget = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QTreeWidget, row_span=Large)
    add_list_widget = functools.partialmethod(
        add_ribbon_widget, cls=QtWidgets.QListWidget, initializer=QtWidgets.QListWidget.add_items, row_span=Large
    )
    add_calendar_widget = functools.partialmethod(add_ribbon_widget, cls=QtWidgets.QCalendarWidget, row_span=Large)
    add_font_combo_box = functools.partialmethod(
        add_ribbon_widget,
        cls=QtWidgets.QFontComboBox,
        initializer=QtWidgets.QFontComboBox.add_items,
        row_span=Large
    )
    add_small_font_combo_box = functools.partialmethod(add_font_combo_box, row_span=Small)
    add_medium_font_combo_box = functools.partialmethod(add_font_combo_box, row_span=Medium)
    add_large_font_combo_box = functools.partialmethod(add_font_combo_box, row_span=Large)

    def add_separator(self, orientation=QtCore.Qt.Orientation.Vertical, width=6, **kwargs) -> RibbonSeparator:
        """Add a separator to the panel.

        :param orientation: The orientation of the separator.
        :param width: The width of the separator.
        :param kwargs: keyword arguments to control the properties of the widget on the ribbon bar.

        :return: The separator.
        """
        kwargs["row_span"] = Large if "row_span" not in kwargs else kwargs["row_span"]
        return self.add_widget(RibbonSeparator(orientation, width), **kwargs)

    add_horizontal_separator = functools.partialmethod(add_separator, orientation=QtCore.Qt.Orientation.Horizontal)
    add_vertical_separator = functools.partialmethod(add_separator, orientation=QtCore.Qt.Orientation.Vertical)

    def add_gallery(self, minimum_width: int = 800, popup_hide_on_click: bool = False, **kwargs) -> RibbonGallery:
        """Add a gallery to the panel.

        :param minimum_width: The minimum width of the gallery.
        :param popup_hide_on_click: Whether the gallery popup should be hidden when a user clicks on it.
        :param kwargs: keyword arguments to control the properties of the widget on the ribbon bar.

        :return: The gallery.
        """
        kwargs["row_span"] = Large if "row_span" not in kwargs else kwargs["row_span"]
        row_span = self.default_row_span(kwargs["row_span"])
        gallery = RibbonGallery(minimum_width, popup_hide_on_click, self)
        maximum_height = self.row_height() * row_span + self._actions_layout.vertical_spacing() * (row_span - 2)
        gallery.set_fixed_height(maximum_height)
        return self.add_widget(gallery, **kwargs)
