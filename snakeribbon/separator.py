import typing

from __feature__ import snake_case

from PySide6 import QtCore, QtGui, QtWidgets


class RibbonSeparator(QtWidgets.QFrame):
    """The RibbonSeparator is a separator that can be used to separate widgets in a ribbon."""

    _top_margins: int = 4
    _bottom_margins: int = 4
    _left_margins: int = 4
    _right_margins: int = 4
    _orientation: QtCore.Qt.Orientation

    @typing.overload
    def __init__(self, orientation=QtCore.Qt.Orientation.Vertical, width=6, parent=None):
        pass

    @typing.overload
    def __init__(self, parent=None):
        pass

    def __init__(self, *args, **kwargs):
        """Create a new separator.

        :param orientation: The orientation of the separator.
        :param width: The width of the separator.
        :param parent: The parent widget.
        """
        if (args and not isinstance(args[0], QtWidgets.QWidget)) or ("orientation" in kwargs or "width" in kwargs):
            orientation = args[0] if len(args) > 0 else kwargs.get("orientation", QtCore.Qt.Orientation.Vertical)
            width = args[1] if len(args) > 1 else kwargs.get("width", 6)
            parent = args[2] if len(args) > 2 else kwargs.get("parent", None)
        else:
            orientation = QtCore.Qt.Orientation.Vertical
            width = 6
            parent = args[0] if len(args) > 0 else kwargs.get("parent", None)
        super().__init__(parent=parent)
        self._orientation = orientation
        if orientation == QtCore.Qt.Orientation.Horizontal:
            self.set_fixed_height(width)
            self.set_size_policy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)  # type: ignore
        else:
            self.set_fixed_width(width)
            self.set_size_policy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)  # type: ignore

    def size_hint(self) -> QtCore.QSize:
        """Return the size hint."""
        return self.size()

    def set_top_bottom_margins(self, top: int, bottom: int) -> None:
        """Set the top and bottom margins."""
        self._top_margins = top
        self._bottom_margins = bottom

    def paint_event(self, event: QtGui.QPaintEvent) -> None:
        """Paint the separator."""
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen()
        pen.set_color(QtGui.QColor(QtCore.Qt.GlobalColor.gray))
        painter.set_pen(pen)
        if self._orientation == QtCore.Qt.Orientation.Vertical:
            x1 = self.rect().center().x()
            painter.draw_line(
                QtCore.QPoint(x1, self.rect().top() + self._top_margins),
                QtCore.QPoint(x1, self.rect().bottom() - self._bottom_margins),
            )
        else:
            y1 = self.rect().center().y()
            painter.draw_line(
                QtCore.QPoint(self.rect().left() + self._left_margins, y1),
                QtCore.QPoint(self.rect().right() - self._right_margins, y1),
            )


class RibbonHorizontalSeparator(RibbonSeparator):
    """Horizontal separator."""

    def __init__(self, width: int = 6, parent=None) -> None:
        """Create a new horizontal separator.

        :param width: The width of the separator.
        :param parent: The parent widget.
        """
        super().__init__(QtCore.Qt.Orientation.Horizontal, width, parent)


class RibbonVerticalSeparator(RibbonSeparator):
    """Vertical separator."""

    def __init__(self, width: int = 6, parent=None) -> None:
        """Create a new vertical separator.

        :param width: The width of the separator.
        :param parent: The parent widget.
        """
        super().__init__(QtCore.Qt.Orientation.Vertical, width, parent)
