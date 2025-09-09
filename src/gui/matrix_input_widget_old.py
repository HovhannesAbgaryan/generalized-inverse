from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSpinBox, QLineEdit, QLabel, QComboBox,
                             QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from .icons_rc import *  # Import the compiled resource file

class MatrixInputWidget(QWidget):
    entries_changed = pyqtSignal()

    # region Constructor

    def __init__(self, parent=None, *, show_hyperparameters: bool = False):
        super().__init__(parent)

        # CRITICAL: Set size policy to prevent unnecessary expansion
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # remember whether to display the 2nd control row
        self.show_hyperparameters = show_hyperparameters

        # STEP 1: Create the absolute minimal main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding around the whole widget
        self.main_layout.setSpacing(15)  # Increased spacing between sections

        # STEP 2: Remove widget-level margins and padding
        self.setContentsMargins(0, 0, 0, 0)

        # Initialize grid tracking variables
        self.prev_rows = 0
        self.prev_cols = 0

        # STEP 3: Create the parameters section with border
        self._create_parameters_section()

        # STEP 4: Create matrix grid with proper centering
        self._create_matrix_section()

        # STEP 5: Force the layout to stick to the top
        self.main_layout.addStretch(1)  # This pushes everything to the top

        # region Controls Container

        # 1) Container for all controls
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(5)

        # region 1st row

        # 2) First row: Rows, Columns, Variable
        top_row = QHBoxLayout()
        top_row.addStretch()

        # region Matrix sizes

        # region Rows

        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(1)
        self.rows_spin.setValue(2)

        top_row.addWidget(QLabel("Rows: m ="))
        top_row.addWidget(self.rows_spin)
        top_row.addSpacing(20)

        # endregion Rows

        # region Columns

        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(1)
        self.cols_spin.setValue(2)

        top_row.addWidget(QLabel("Columns: n ="))
        top_row.addWidget(self.cols_spin)
        top_row.addSpacing(20)

        # endregion Columns

        # endregion Matrix sizes

        # region Variable

        self.variable_combo = QComboBox()
        self.variable_combo.addItems(['t', 'x', 'y', 'z'])

        top_row.addWidget(QLabel("Variable:"))
        top_row.addWidget(self.variable_combo)
        top_row.addStretch()

        # endregion Variable

        controls_layout.addLayout(top_row)

        # endregion 1st row

        # region 2nd row

        if self.show_hyperparameters:
            # 3) Second row: K, tϑ, H
            bottom_row = QHBoxLayout()
            bottom_row.addStretch()

            # region Hyper-parameters

            # region Discretes count

            self.discretes_count_spin = QSpinBox()
            self.discretes_count_spin.setMinimum(1)
            self.discretes_count_spin.setValue(3)

            bottom_row.addWidget(QLabel("K ="))
            bottom_row.addWidget(self.discretes_count_spin)
            bottom_row.addSpacing(20)

            # endregion Discretes count

            # region Approximation center

            self.approximation_center_spin = QSpinBox()
            self.approximation_center_spin.setMinimum(0)
            self.approximation_center_spin.setValue(0)

            bottom_row.addWidget(QLabel("t\u03F8 ="))
            bottom_row.addWidget(self.approximation_center_spin)
            bottom_row.addSpacing(20)

            # endregion Approximation center

            # region Scaling coefficient

            self.scaling_coefficient_spin = QSpinBox()
            self.scaling_coefficient_spin.setMinimum(1)
            self.scaling_coefficient_spin.setValue(1)

            bottom_row.addWidget(QLabel("H ="))
            bottom_row.addWidget(self.scaling_coefficient_spin)
            bottom_row.addStretch()

            # endregion Scaling coefficient

            # endregion Hyper-parameters

            controls_layout.addLayout(bottom_row)

        # endregion 2nd row

        # 4) Add controls container to main layout
        self.main_layout.addWidget(controls_container)

        # endregion Controls Container

        # region Matrix Layout

        # 5) Create a dedicated grid for matrix entry widgets
        self.matrix_layout = QGridLayout()
        self.matrix_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.matrix_layout)

        # endregion Matrix Layout

        # Rebuild on spin change
        self.rows_spin.valueChanged.connect(self._build_grid)
        self.cols_spin.valueChanged.connect(self._build_grid)

        # STEP 6: Connect signals and initialize
        self._connect_signals()
        self.entry_widgets = []
        self._build_grid()

    # endregion Constructor

    # region Functions

    def _build_grid(self):
        # --- 1) Capture old entries if we have any ---
        old_entries = []
        if self.entry_widgets:
            for i in range(self.prev_rows):
                row = []
                for j in range(self.prev_cols):
                    idx = i * self.prev_cols + j
                    row.append(self.entry_widgets[idx].text())
                old_entries.append(row)

        # --- 2) Remove old widgets ---
        for w in self.entry_widgets:
            self.matrix_layout.removeWidget(w)
            w.deleteLater()
        self.entry_widgets.clear()

        # --- 3) Get new dimensions ---
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        # --- 4) Rebuild grid, copying back old entries where valid ---
        for i in range(rows):
            for j in range(cols):
                line = QLineEdit()
                line.setPlaceholderText("e.g. 1+I*t")
                if i < self.prev_rows and j < self.prev_cols:
                    line.setText(old_entries[i][j])
                self.matrix_layout.addWidget(line, i, j)
                line.textChanged.connect(self.entries_changed)
                self.entry_widgets.append(line)

        # --- 5) Update prev dimensions and emit ---
        self.prev_rows = rows
        self.prev_cols = cols
        self.entries_changed.emit()

    def get_matrix_entries(self):
        """
        Return a list of lists of the user-entered strings.
        Raises ValueError if any cell is empty.
        """
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        entries = []
        idx = 0
        for i in range(rows):
            row = []
            for j in range(cols):
                text = self.entry_widgets[idx].text().strip()
                if not text:
                    raise ValueError(f"Empty entry at ({i + 1}, {j + 1})")
                row.append(text)
                idx += 1
            entries.append(row)

        hyper_parameters = dict(variable=self.variable_combo.currentText())

        if self.show_hyperparameters:
            hyper_parameters["discretes_count"] = self.discretes_count_spin.value()
            hyper_parameters["approximation_center"] = self.approximation_center_spin.value()
            hyper_parameters["scaling_coefficient"] = self.scaling_coefficient_spin.value()


        return (rows, cols), hyper_parameters, entries

    def all_entries_filled(self):
        return all(w.text().strip() != "" for w in self.entry_widgets)

    def clear_entries(self):
        """Clear all matrix entries (reset to placeholder)."""
        for widget in self.entry_widgets:
            widget.clear()
        self.entries_changed.emit()

    # endregion Functions

