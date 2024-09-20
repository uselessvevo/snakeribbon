import typing

from __feature__ import snake_case

from PySide6 import QtCore, QtGui, QtWidgets


class RibbonMenu(QtWidgets.QMenu):
    @typing.overload
    def __init__(self, title: str = "", parent=None):
        pass

    @typing.overload
    def __init__(self, parent=None):
        pass

    def __init__(self, *args, **kwargs):
        """Create a new panel.

        :param title: The title of the menu.
        :param parent: The parent widget.
        """
        if (args and not isinstance(args[0], QtWidgets.QWidget)) or ("title" in kwargs):
            title = args[0] if len(args) > 0 else kwargs.get("title", "")
            parent = args[1] if len(args) > 1 else kwargs.get("parent", None)
        else:
            title = ""
            parent = args[0] if len(args) > 0 else kwargs.get("parent", None)
        super().__init__(title, parent)
        self.set_font(QtWidgets.QApplication.instance().font())  # type: ignore

    def add_widget(self, widget: QtWidgets.QWidget):
        """Add a widget to the menu.

        :param widget: The widget to add.
        """
        widgetAction = QtWidgets.QWidgetAction(self)
        widgetAction.set_default_widget(widget)
        self.add_action(widgetAction)

    def add_horizontal_layout_widget(self) -> QtWidgets.QHBoxLayout:
        """Add a horizontal layout widget to the menu.

        :return: The horizontal layout.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.set_contents_margins(0, 0, 0, 0)
        self.add_widget(widget)
        return layout

    def add_vertical_layout_widget(self) -> QtWidgets.QVBoxLayout:
        """Add a vertical layout widget to the menu.

        :return: The vertical layout.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.set_contents_margins(0, 0, 0, 0)
        self.add_widget(widget)
        return layout

    def add_grid_layout_widget(self) -> QtWidgets.QGridLayout:
        """Add a grid layout widget to the menu.

        :return: The grid layout.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(widget)
        layout.set_contents_margins(0, 0, 0, 0)
        self.add_widget(widget)
        return layout

    def add_form_layout_widget(self) -> QtWidgets.QFormLayout:
        """Add a form layout widget to the menu.

        :return: The form layout.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        layout.set_contents_margins(0, 0, 0, 0)
        self.add_widget(widget)
        return layout

    def add_spacing(self, spacing: int = 5):
        """Add spacing to the menu.

        :param spacing: The spacing.
        """
        spacer = QtWidgets.QLabel()
        spacer.set_size_policy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        spacer.set_fixed_height(spacing)
        self.add_widget(spacer)  # noqa

    def add_label(self, text: str = "", alignment=QtCore.Qt.AlignmentFlag.AlignLeft):
        """Add a label to the menu.

        :param text: The text of the label.
        :param alignment: The alignment of the label.
        """
        label = QtWidgets.QLabel(text)
        label.set_alignment(alignment)
        self.add_widget(label)  # noqa


class RibbonPermanentMenu(RibbonMenu):
    """
    A permanent menu.
    """

    action_added = QtCore.Signal(QtGui.QAction)

    def hide_event(self, a0: QtGui.QHideEvent) -> None:
        self.show()

    def add_action(self, *args, **kwargs) -> QtGui.QAction:
        action = super().add_action(*args, **kwargs)
        self.action_added.emit(action)
        return action
