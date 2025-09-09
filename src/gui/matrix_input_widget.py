from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSpinBox,
                             QLineEdit, QLabel, QComboBox, QSizePolicy, QFrame, QAbstractSpinBox, QPushButton)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from .icons_rc import *  # Import the compiled resource file


class MatrixInputWidget(QWidget):
    entries_changed = pyqtSignal()

    def __init__(self, parent=None, *, show_hyperparameters: bool = False):
        super().__init__(parent)

        # remember whether to display the 2nd control row
        self.show_hyperparameters = show_hyperparameters

        # CRITICAL: Set size policy to prevent unnecessary expansion
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

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

        # STEP 6: Connect signals and initialize
        self._connect_signals()
        self.entry_widgets = []
        self._build_grid()

        # STEP 7: Final styling
        self._apply_styling()

    def _create_parameters_section(self):
        """Create the parameters section with a bordered frame"""

        # Create a frame to contain all parameters with a border
        parameters_frame = QFrame()
        parameters_frame.setObjectName("parametersFrame")
        parameters_frame.setFrameStyle(QFrame.Box)  # Creates a box border
        parameters_frame.setContentsMargins(15, 10, 15, 10)  # Internal padding

        # Create layout for the parameters frame
        parameters_layout = QVBoxLayout(parameters_frame)
        parameters_layout.setContentsMargins(0, 5, 0, 5)
        parameters_layout.setSpacing(8)  # Spacing between parameter rows

        # Add title label for the parameters section
        self.title_label = QLabel("Parameters")
        self.title_label.setStyleSheet("""
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        parameters_layout.addWidget(self.title_label)

        # Create first row: Matrix dimensions and variable
        top_row = self._create_top_control_row()
        parameters_layout.addLayout(top_row)

        if self.show_hyperparameters:
            # Create second row: Hyperparameters
            bottom_row = self._create_bottom_control_row()
            parameters_layout.addLayout(bottom_row)

        # Add the parameters frame to main layout
        self.main_layout.addWidget(parameters_frame)

    def _create_spinbox_with_buttons(self, min_val=1, default_val=2, max_width=60):
        """Create a spinbox with custom up/down buttons positioned correctly"""
        # Create container for spinbox and buttons
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)

        # Create spinbox without default buttons
        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        spinbox.setMinimum(min_val)
        spinbox.setValue(default_val)
        spinbox.setMaximumWidth(max_width)
        spinbox.setMinimumHeight(28)

        # Create up/down buttons with custom icons
        up_btn = QPushButton()
        down_btn = QPushButton()

        # Set icons

        up_btn.setIcon(QIcon(":/icons/up.svg"))
        down_btn.setIcon(QIcon(":/icons/down.svg"))

        # Style the buttons
        button_style = """
            QPushButton {
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 2px;
                min-width: 18px;
                max-width: 18px;
                min-height: 12px;
                max-height: 12px;
            }
            QPushButton:hover {
                background-color: #E8E8E8;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """
        up_btn.setStyleSheet(button_style)
        down_btn.setStyleSheet(button_style)

        # Connect buttons to spinbox
        up_btn.clicked.connect(lambda: spinbox.stepUp())
        down_btn.clicked.connect(lambda: spinbox.stepDown())

        # Create vertical layout for buttons
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(1)
        buttons_layout.addWidget(up_btn)
        buttons_layout.addWidget(down_btn)

        # Add spinbox and buttons to container
        container_layout.addWidget(spinbox)
        container_layout.addWidget(buttons_widget)

        return container, spinbox

    def _create_top_control_row(self):
        """Create the top row with matrix dimensions and variable selection"""

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)  # Good spacing between elements

        # Center the controls
        row_layout.addStretch()

        # Rows control with custom buttons
        rows_container, self.rows_spin = self._create_spinbox_with_buttons(min_val=1, default_val=2)
        # row_layout.addWidget(QLabel("Rows: m ="))
        self.lbl_rows = QLabel("Rows: m =")
        row_layout.addWidget(self.lbl_rows)
        row_layout.addWidget(rows_container)
        row_layout.addSpacing(20)

        # Columns control with custom buttons
        cols_container, self.cols_spin = self._create_spinbox_with_buttons(min_val=1, default_val=2)
        # row_layout.addWidget(QLabel("Columns: n ="))
        self.lbl_cols = QLabel("Columns: n =")
        row_layout.addWidget(self.lbl_cols)
        row_layout.addWidget(cols_container)
        row_layout.addSpacing(20)

        # Variable selection
        self.variable_combo = QComboBox()
        self.variable_combo.setObjectName("variableCombo")
        self.variable_combo.addItems(['t', 'x', 'y', 'z'])
        self.variable_combo.setMaximumWidth(50)

        # row_layout.addWidget(QLabel("Variable:"))
        self.lbl_variable = QLabel("Variable:")
        row_layout.addWidget(self.lbl_variable)
        row_layout.addWidget(self.variable_combo)
        row_layout.addStretch()

        return row_layout

    def _create_bottom_control_row(self):
        """Create the bottom row with hyperparameters"""

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)  # Good spacing between elements

        # Center the controls
        row_layout.addStretch()

        # K parameter with custom buttons
        k_container, self.discretes_count_spin = self._create_spinbox_with_buttons(min_val=1, default_val=3)
        # row_layout.addWidget(QLabel("K ="))
        self.lbl_k = QLabel("K =")
        row_layout.addWidget(self.lbl_k)
        row_layout.addWidget(k_container)
        row_layout.addSpacing(20)

        # tθ parameter with custom buttons
        theta_container, self.approximation_center_spin = self._create_spinbox_with_buttons(min_val=0, default_val=0)
        # row_layout.addWidget(QLabel("tθ ="))
        self.lbl_theta = QLabel("tθ =")
        row_layout.addWidget(self.lbl_theta)
        row_layout.addWidget(theta_container)
        row_layout.addSpacing(20)

        # H parameter with custom buttons
        h_container, self.scaling_coefficient_spin = self._create_spinbox_with_buttons(min_val=1, default_val=1)
        # row_layout.addWidget(QLabel("H ="))
        self.lbl_h = QLabel("H =")
        row_layout.addWidget(self.lbl_h)
        row_layout.addWidget(h_container)
        row_layout.addStretch()

        return row_layout

    def _create_matrix_section(self):
        """Create the matrix input grid section with proper centering"""

        # Create a container for the matrix that will center it
        matrix_container = QWidget()
        matrix_container_layout = QHBoxLayout(matrix_container)
        matrix_container_layout.setContentsMargins(0, 0, 0, 0)

        # Add stretches to center the matrix horizontally
        matrix_container_layout.addStretch()

        # Create the actual matrix widget
        matrix_widget = QWidget()
        self.matrix_layout = QGridLayout(matrix_widget)
        self.matrix_layout.setContentsMargins(0, 0, 0, 0)
        self.matrix_layout.setSpacing(8)  # Increased spacing between matrix cells

        # Add the matrix widget to the container
        matrix_container_layout.addWidget(matrix_widget)
        matrix_container_layout.addStretch()

        # Add the centered matrix container to main layout
        self.main_layout.addWidget(matrix_container)

    def _connect_signals(self):
        """Connect all the control signals"""
        self.rows_spin.valueChanged.connect(self._build_grid)
        self.cols_spin.valueChanged.connect(self._build_grid)

    def _apply_styling(self):
        """Apply comprehensive styling to the widget"""

        # Set the dropdown arrow color based on tab
        dropdown_arrow_color = "black"

        self.setStyleSheet(f"""
            MatrixInputWidget {{
                background-color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                color: #2C3E50;
                font-size: 12px;
                font-weight: 500;
                margin: 2px;
            }}
            QSpinBox {{
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 3px;
                font-size: 12px;
                min-height: 24px;
            }}
            QSpinBox:focus {{
                border: 2px solid {dropdown_arrow_color};
            }}
            QComboBox {{
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 3px;
                font-size: 12px;
            }}
            QComboBox:focus {{
                border: 2px solid {dropdown_arrow_color};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #CCCCCC;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }}
            
            QComboBox#variableCombo::down-arrow {{
                image: url(:/icons/down.svg);
                width: 12px;   /* adjust to your SVG’s natural size */
                height: 12px;
            }}
            QComboBox#variableCombo::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }}
            QLineEdit {{
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
                font-family: 'Courier New', monospace;
                selection-background-color: {dropdown_arrow_color};
            }}
            QLineEdit:focus {{
                border: 2px solid {dropdown_arrow_color};
            }}
            QFrame#parametersFrame {{
                border: 2px solid teal;
                border-radius: 5px;
            }}
        """)

    def _build_grid(self):
        """Rebuild the matrix input grid when dimensions change"""

        # Step 1: Preserve existing entries
        old_entries = []
        if self.entry_widgets:
            for i in range(self.prev_rows):
                row = []
                for j in range(self.prev_cols):
                    idx = i * self.prev_cols + j
                    if idx < len(self.entry_widgets):
                        row.append(self.entry_widgets[idx].text())
                    else:
                        row.append("")
                old_entries.append(row)

        # Step 2: Clean up existing widgets
        for widget in self.entry_widgets:
            self.matrix_layout.removeWidget(widget)
            widget.deleteLater()
        self.entry_widgets.clear()

        # Step 3: Get new dimensions
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        # Step 4: Create new grid with better spacing
        for i in range(rows):
            for j in range(cols):
                line_edit = QLineEdit()
                # line_edit.setPlaceholderText("e.g., 1+I*t")
                line_edit.setPlaceholderText(self.placeholder_text if hasattr(self, 'placeholder_text') else "e.g., 1+I*t")

                # Set optimal size for line edit
                line_edit.setMinimumWidth(90)
                line_edit.setMaximumWidth(130)
                line_edit.setMinimumHeight(30)  # Increased height for better spacing
                line_edit.setMaximumHeight(35)

                # Restore old entry if it exists
                if i < len(old_entries) and j < len(old_entries[i]):
                    line_edit.setText(old_entries[i][j])

                # Add to grid with proper spacing
                self.matrix_layout.addWidget(line_edit, i, j)

                # Connect signal
                line_edit.textChanged.connect(self.entries_changed)

                # Track widget
                self.entry_widgets.append(line_edit)

        # Step 5: Add extra spacing between rows by setting row stretch
        for i in range(rows):
            self.matrix_layout.setRowMinimumHeight(i, 40)  # Minimum height for each row

        # Step 6: Update tracking
        self.prev_rows = rows
        self.prev_cols = cols

        # Step 7: Emit change signal
        self.entries_changed.emit()

        # Step 8: Force layout update
        self.updateGeometry()

        # NEW: shrink the window to fit its contents
        # top = self.window()  # for a QMainWindow use self.window(), for a QWidget-based window it's the same
        # top.adjustSize()

    # === PUBLIC INTERFACE METHODS ===

    def get_matrix_entries(self):
        """Extract all matrix entries and hyperparameters"""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        # Build entries matrix
        entries = []
        idx = 0
        for i in range(rows):
            row = []
            for j in range(cols):
                text = self.entry_widgets[idx].text().strip()
                if not text:
                    raise ValueError(f"Empty entry at position ({i + 1}, {j + 1})")
                row.append(text)
                idx += 1
            entries.append(row)

        # Collect hyperparameters
        hyper_parameters = dict(variable=self.variable_combo.currentText())

        if self.show_hyperparameters:
            hyper_parameters["discretes_count"] = self.discretes_count_spin.value()
            hyper_parameters["approximation_center"] = self.approximation_center_spin.value()
            hyper_parameters["scaling_coefficient"] = self.scaling_coefficient_spin.value()

        return (rows, cols), hyper_parameters, entries

    def all_entries_filled(self):
        """Check if all matrix entries contain non-empty text"""
        return all(widget.text().strip() != "" for widget in self.entry_widgets)

    def clear_entries(self):
        """Clear all matrix entries and emit change signal"""
        for widget in self.entry_widgets:
            widget.clear()
        self.entries_changed.emit()

    def set_language(self, translations: dict):
        """
        translations: a dict containing keys:
            'rows_label','cols_label','variable_label',
            'k_label','theta_label','h_label','placeholder',
            optionally 'parameters_title'
        """
        # store placeholder for new entries
        self.placeholder_text = translations.get('placeholder', "e.g., 1+I*t")

        # Title
        title = translations.get('parameters_title', translations.get('parameters', 'Parameters'))
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)

        # top row labels
        if hasattr(self, 'lbl_rows'):
            self.lbl_rows.setText(translations.get('rows_label', self.lbl_rows.text()))
        if hasattr(self, 'lbl_cols'):
            self.lbl_cols.setText(translations.get('cols_label', self.lbl_cols.text()))
        if hasattr(self, 'lbl_variable'):
            self.lbl_variable.setText(translations.get('variable_label', self.lbl_variable.text()))

        # bottom row labels
        if hasattr(self, 'lbl_k'):
            self.lbl_k.setText(translations.get('k_label', self.lbl_k.text()))
        if hasattr(self, 'lbl_theta'):
            self.lbl_theta.setText(translations.get('theta_label', self.lbl_theta.text()))
        if hasattr(self, 'lbl_h'):
            self.lbl_h.setText(translations.get('h_label', self.lbl_h.text()))

        # Update placeholders of existing entry widgets
        if hasattr(self, 'entry_widgets') and self.entry_widgets:
            for w in self.entry_widgets:
                w.setPlaceholderText(self.placeholder_text)

