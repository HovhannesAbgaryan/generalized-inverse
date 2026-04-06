from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import math

class ErrorsWindow(QWidget):
    # region Summary
    """
    Display Moore-Penrose errors supplied as a dict-of-dicts:
        errors_dict = {
            t1: {'c1': <float>, 'c2': <float>, 'c3': <float>, 'c4': <float>},
            t2: {...},
            ...
        }

    This window is a top-level window (has its own decorations) and deletes itself on close.
    It accepts an optional `translator` callable (e.g. MainWindow.tr) for localization.
    """
    # endregion Summary

    # region Constructor

    def __init__(self, errors_dict: dict, parent=None, translator=None, all_translations=None):
        # Make this widget a true top-level window by not passing `parent` to QWidget ctor.
        # Passing parent=None avoids reparenting issues across platforms.
        super().__init__(None)

        self.setWindowIcon(QIcon(":/icons/app_icon.png"))

        # Translator priority:
        # 1) explicit translator argument (callable)
        # 2) parent's tr attribute if available
        # 3) fallback identity lambda
        if callable(translator):
            self._tr = translator
        elif parent is not None and hasattr(parent, "tr") and callable(parent.tr):
            self._tr = parent.tr
        else:
            self._tr = lambda k: k

        # All language translations dict (used to stabilise column widths across languages)
        self._all_translations = all_translations or {}

        # Force top-level window flags to ensure proper window decorations and behavior.
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        # Delete the widget on close to release resources
        self.setAttribute(Qt.WA_DeleteOnClose)

        # use localized strings from MainWindow.translations via translator callable
        self.setWindowTitle(self._tr("errors_window_title"))

        # start with a reasonable size; we'll adjust after populating
        self.resize(640, 320)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        # hide the left-side row numbers (vertical header)
        self.table.verticalHeader().setVisible(False)

        # Populate the table
        self.populate_table(errors_dict)

        # Resize to fit table content and screen
        self._resize_to_fit()

    # endregion Constructor

    # region Functions

    # region Formatting

    @staticmethod
    def _format_error_value(v):
        """Format a numeric error to scientific notation or 'inf'."""
        try:
            if v is None:
                return ""
            # handle NaN / inf
            if isinstance(v, float) and (math.isinf(v) or math.isnan(v)):
                return "inf" if math.isinf(v) else "nan"
            # cast to float then format
            fv = float(v)
            return f"{fv:.2e}"
        except Exception:
            return str(v)

    @staticmethod
    def _format_t_value(t_val):
        """Nicely format t value for display (prefer short float or integer representation)."""
        try:
            fv = float(t_val)
            if abs(fv - round(fv)) < 1e-12:
                return str(int(round(fv)))
            return f"{fv:.6g}"
        except Exception:
            return str(t_val)

    # endregion Formatting

    # ---------- Table population ----------
    def populate_table(self, errors_dict: dict):
        """Fill the QTableWidget from errors_dict (dict-of-dicts)."""
        if not errors_dict:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # Determine sorted order of t-values (try numeric sort, fallback to string)
        try:
            t_keys = sorted(errors_dict.keys(), key=lambda k: float(k))
        except Exception:
            t_keys = sorted(errors_dict.keys(), key=lambda k: str(k))

        rows = len(t_keys)
        cols = 5  # t + C1..C4

        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        # Header labels (use translator if available)
        headers = [
            self._tr("errors_col_t"),
            self._tr("errors_col_condition1"),
            self._tr("errors_col_condition2"),
            self._tr("errors_col_condition3"),
            self._tr("errors_col_condition4"),
        ]
        self.table.setHorizontalHeaderLabels(headers)

        for i, t_key in enumerate(t_keys):
            row_dict = errors_dict.get(t_key, {})
            c1 = row_dict.get("c1")
            c2 = row_dict.get("c2")
            c3 = row_dict.get("c3")
            c4 = row_dict.get("c4")

            t_item = QTableWidgetItem(self._format_t_value(t_key))
            t_item.setFlags(t_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, t_item)

            for j, val in enumerate((c1, c2, c3, c4), start=1):
                cell = QTableWidgetItem(self._format_error_value(val))
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, j, cell)

        self.table.setAlternatingRowColors(True)

    # region Size

    def _finalize_size(self):
        """After show, nudge window size to account for OS window-decoration insets."""
        try:
            self.show()
            extra_w = self.frameGeometry().width() - self.geometry().width()
            extra_h = self.frameGeometry().height() - self.geometry().height()
            self.resize(self.width() + extra_w + 4, self.height() + extra_h + 4)
            self.setMinimumSize(200, 150)
        except Exception:
            pass

    def _resize_to_fit(self):
        """Size columns/rows to content and set the ideal initial window size.
        The window remains freely resizable by the user after this call."""
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(
                i, max(self.table.sizeHintForColumn(i), header.sectionSizeHint(i))
            )

        # Ensure column widths are stable across all languages.
        if self._all_translations:
            fm = header.fontMetrics()
            col_keys = [
                'errors_col_t', 'errors_col_condition1', 'errors_col_condition2',
                'errors_col_condition3', 'errors_col_condition4',
            ]
            ref_text_w = fm.boundingRect(self._tr('errors_col_condition1')).width()
            col_padding = max(header.sectionSizeHint(1) - ref_text_w, 8)
            for i, key in enumerate(col_keys):
                max_w = self.table.columnWidth(i)
                for lang_dict in self._all_translations.values():
                    text = lang_dict.get(key, '')
                    if text:
                        max_w = max(max_w, fm.boundingRect(text).width() + col_padding)
                self.table.setColumnWidth(i, max_w)

        preferred_table_w = sum(self.table.columnWidth(i) for i in range(self.table.columnCount()))
        preferred_table_h = (sum(self.table.rowHeight(i) for i in range(self.table.rowCount())) + header.height())
        frame_w = 2 * self.table.frameWidth()
        margins = self.layout().contentsMargins()

        ideal_w = preferred_table_w + frame_w + margins.left() + margins.right()
        ideal_h = preferred_table_h + frame_w + margins.top() + margins.bottom()

        # Scrollbars appear only when the user shrinks the window below content size.
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Remove any previous fixed constraints so the table expands with the window.
        self.table.setMinimumSize(0, 0)
        self.table.setMaximumSize(16777215, 16777215)

        self.resize(ideal_w, ideal_h)
        QTimer.singleShot(0, self._finalize_size)

    # endregion Size

    def refresh_translations(self):
        self.setWindowTitle(self._tr("errors_window_title"))

        # update column headers
        headers = [
            self._tr("errors_col_t"),
            self._tr("errors_col_condition1"),
            self._tr("errors_col_condition2"),
            self._tr("errors_col_condition3"),
            self._tr("errors_col_condition4"),
        ]
        self.table.setHorizontalHeaderLabels(headers)

        # repopulate sizes (we don't need to repopulate data)
        self._resize_to_fit()

    # endregion Functions
