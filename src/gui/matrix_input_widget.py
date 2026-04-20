import sympy as sp
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSpinBox, QLineEdit,
                             QLabel, QComboBox, QSizePolicy, QFrame, QAbstractSpinBox, QPushButton)

from src.utils.rounding import round_matrix, round_floats_in_expr


class MatrixInputWidget(QWidget):
    entries_changed = pyqtSignal()

    # region Constructor

    def __init__(self, parent=None, *, show_hyperparameters: bool = False):
        super().__init__(parent)

        # Remember whether to display the 2nd control row (hyperparameters of numerical-analytical methods)
        self.show_hyperparameters = show_hyperparameters

        # Set size policy to prevent unnecessary expansion
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

        # file-backed entries storage (None or a list of rows)
        self._file_entries = None

        # optional: store loaded filename for UX if you want later
        self._loaded_filename = None

        self._build_grid()

        # STEP 7: Final styling
        self._apply_styling()

    # endregion Constructor

    # region Functions

    # region Private

    def _create_parameters_section(self):
        # region Summary
        """
        Create the parameters section with a bordered frame
        """
        # endregion Summary

        # region Body

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

        # Create 1st row: Matrix dimensions and variable
        top_row = self._create_top_control_row()
        parameters_layout.addLayout(top_row)

        if self.show_hyperparameters:
            # Create 2nd row: Hyperparameters
            bottom_row = self._create_bottom_control_row()
            parameters_layout.addLayout(bottom_row)

        # Add the parameters frame to main layout
        self.main_layout.addWidget(parameters_frame)

        # endregion Body

    def _create_spinbox_with_buttons(self, min_val=None, default_val=2, max_width=60):
        # region Summary
        """
        Create a spinbox with custom up/down buttons positioned correctly
        """
        # endregion Summary

        # region Body

        # Create container for spinbox and buttons
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)

        # Create spinbox without default buttons
        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)

        if min_val is not None:
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

        # endregion Body

    def _create_top_control_row(self):
        # region Summary
        """
        Create the top row with matrix dimensions and variable selection
        """
        # endregion Summary

        # region Body

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)  # Good spacing between elements

        # Center the controls
        row_layout.addStretch()

        # Rows control with custom buttons
        rows_container, self.rows_spin = self._create_spinbox_with_buttons(min_val=1, default_val=2)
        self.lbl_rows = QLabel("Rows: m =")
        row_layout.addWidget(self.lbl_rows)
        row_layout.addWidget(rows_container)
        row_layout.addSpacing(20)

        # Columns control with custom buttons
        cols_container, self.cols_spin = self._create_spinbox_with_buttons(min_val=1, default_val=2)
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

        # endregion Body

    def _create_bottom_control_row(self):
        # region Summary
        """
        Create the bottom row with hyperparameters
        """
        # endregion Summary

        # region Body

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)  # Good spacing between elements

        # Center the controls
        row_layout.addStretch()

        # K parameter with custom buttons
        k_container, self.discretes_count_spin = self._create_spinbox_with_buttons(min_val=1, default_val=3)
        self.lbl_k = QLabel("K =")
        row_layout.addWidget(self.lbl_k)
        row_layout.addWidget(k_container)
        row_layout.addSpacing(20)

        # tθ parameter with custom buttons
        theta_container, self.approximation_center_spin = self._create_spinbox_with_buttons(default_val=0)
        self.lbl_theta = QLabel("tθ =")
        row_layout.addWidget(self.lbl_theta)
        row_layout.addWidget(theta_container)
        row_layout.addSpacing(20)

        # H parameter with custom buttons
        h_container, self.scaling_coefficient_spin = self._create_spinbox_with_buttons(min_val=1, default_val=1)
        self.lbl_h = QLabel("H =")
        row_layout.addWidget(self.lbl_h)
        row_layout.addWidget(h_container)
        row_layout.addStretch()

        return row_layout

        # endregion Body

    def _create_matrix_section(self):
        # region Summary
        """
        Create the matrix input grid section with left (input) and right (output) panels and a vertical separator.
        """
        # endregion Summary

        # region Body

        # Create a container for the whole matrix area
        matrix_container = QWidget()
        matrix_container_layout = QHBoxLayout(matrix_container)
        matrix_container_layout.setContentsMargins(0, 0, 0, 0)
        matrix_container_layout.setSpacing(12)

        # Add left stretch to center horizontally
        matrix_container_layout.addStretch()

        # --- Left: input matrix widget ---
        input_widget = QWidget()
        self.matrix_layout = QGridLayout(input_widget)
        self.matrix_layout.setContentsMargins(0, 0, 0, 0)
        self.matrix_layout.setSpacing(8)  # Increased spacing between matrix cells
        matrix_container_layout.addWidget(input_widget)

        # --- Middle: vertical separator line ---
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(2)
        separator.setFixedWidth(12)
        matrix_container_layout.addWidget(separator)

        # --- Right: output matrix widget ---
        output_widget = QWidget()
        self.output_layout = QGridLayout(output_widget)
        self.output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_layout.setSpacing(8)
        matrix_container_layout.addWidget(output_widget)

        # Add right stretch
        matrix_container_layout.addStretch()

        # Add the whole container to main layout
        self.main_layout.addWidget(matrix_container)

        # Initialize storage for output widgets
        self.output_entry_widgets = []

        # endregion Body

    def _connect_signals(self):
        # region Summary
        """
        Connect all the control signals
        """
        # endregion Summary

        # region Body

        self.rows_spin.valueChanged.connect(self._build_grid)
        self.cols_spin.valueChanged.connect(self._build_grid)

        # When any input entry changes, we should clear previous outputs (so the user doesn't get stale results)
        self.entries_changed.connect(self._clear_outputs_on_input_change)

        # endregion Body

    def _apply_styling(self):
        # region Summary
        """
        Apply comprehensive styling to the widget
        """
        # endregion Summary

        # region Body

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
                width: 12px;   /* adjust to your SVG's natural size */
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

        # endregion Body

    def _build_grid(self):
        # region Summary
        """
        Rebuild the matrix input grid when dimensions change and create matching output grid (n x m).
        """
        # endregion Summary

        # region Body

        # ------- preserve old input entries -------
        old_entries = []
        if hasattr(self, 'entry_widgets') and self.entry_widgets:
            for i in range(self.prev_rows):
                row = []
                for j in range(self.prev_cols):
                    idx = i * self.prev_cols + j
                    if idx < len(self.entry_widgets):
                        row.append(self.entry_widgets[idx].text())
                    else:
                        row.append("")
                old_entries.append(row)

        # ------- clear existing input widgets -------
        if hasattr(self, 'entry_widgets'):
            for widget in self.entry_widgets:
                self.matrix_layout.removeWidget(widget)
                widget.deleteLater()
        self.entry_widgets = []

        # ------- clear existing output widgets -------
        if hasattr(self, 'output_entry_widgets'):
            for widget in self.output_entry_widgets:
                self.output_layout.removeWidget(widget)
                widget.deleteLater()
        self.output_entry_widgets = []

        # ------- get new dimensions -------
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        # ------- create new input grid -------
        for i in range(rows):
            for j in range(cols):
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(
                    self.placeholder_text if hasattr(self, 'placeholder_text') else "e.g., 1+I*t")
                line_edit.setMinimumWidth(90)
                line_edit.setMaximumWidth(130)
                line_edit.setMinimumHeight(30)
                line_edit.setMaximumHeight(35)

                # restore old entry if present
                if i < len(old_entries) and j < len(old_entries[i]):
                    line_edit.setText(old_entries[i][j])

                self.matrix_layout.addWidget(line_edit, i, j)
                line_edit.textChanged.connect(self.entries_changed)
                self.entry_widgets.append(line_edit)

        # spacing for input rows
        for i in range(rows):
            self.matrix_layout.setRowMinimumHeight(i, 40)

        # ------- create default output grid sized (cols x rows) i.e. n x m -------
        out_rows = cols
        out_cols = rows

        for i in range(out_rows):
            for j in range(out_cols):
                out_edit = QLineEdit()
                out_edit.setReadOnly(True)
                out_edit.setPlaceholderText("")  # starts empty
                out_edit.setMinimumWidth(90)
                out_edit.setMaximumWidth(130)
                out_edit.setMinimumHeight(30)
                out_edit.setMaximumHeight(35)
                out_edit.setFrame(True)
                # style slightly different so visually distinct (optional)
                out_edit.setStyleSheet("QLineEdit { background-color: #FBFBFB; }")

                self.output_layout.addWidget(out_edit, i, j)
                self.output_entry_widgets.append(out_edit)

        for i in range(out_rows):
            self.output_layout.setRowMinimumHeight(i, 40)

        # Update tracking
        self.prev_rows = rows
        self.prev_cols = cols

        # Emit change signal
        self.entries_changed.emit()
        self.updateGeometry()

        # endregion Body

    def _clear_outputs_on_input_change(self):
        # region Summary
        """
        Clears output fields when input changes to avoid stale displayed results.
        """
        # endregion Summary

        # region Body

        if hasattr(self, 'output_entry_widgets'):
            for w in self.output_entry_widgets:
                w.clear()

        # endregion Body

    def _format_value_for_display(self, val, ndigits=4):
        # region Summary
        """
        Format a value for display using the rounding utilities.
        Returns a clean string representation suitable for UI display.
        """
        # endregion Summary

        # region Body

        try:
            # If it's a SymPy expression or number, try to round floating point parts
            if isinstance(val, (sp.Expr, sp.Number)):
                # First, round any floating point components within the expression
                rounded_val = round_floats_in_expr(val, ndigits)

                # Convert to string using SymPy's string representation
                result = str(rounded_val)

                # Clean up the representation
                result = self._clean_number_string(result)
                result = self._simplify_coefficients(result)
                return result  if result not in ["0.0"] else "" # "0",

            # For Python numeric types
            elif isinstance(val, complex):
                real_part = self._clean_float_string(val.real, ndigits)
                imag_part = self._clean_float_string(val.imag, ndigits)

                if imag_part == "0":
                    return real_part
                elif real_part == "0":
                    return f"{imag_part}*I" if imag_part != "1" else "I"
                else:
                    sign = "+" if val.imag >= 0 else "-"
                    imag_display = abs(val.imag)
                    imag_str = self._clean_float_string(imag_display, ndigits)
                    if imag_str == "1":
                        return f"{real_part}{sign}I"
                    else:
                        return f"{real_part}{sign}{imag_str}*I"

            elif isinstance(val, float):
                return self._clean_float_string(val, ndigits)

            else:
                # For other types, convert to string and clean
                result = str(val)
                result = self._clean_number_string(result)
                result = self._simplify_coefficients(result)
                return result if result not in ["0", "0.0"] else ""

        except Exception:
            # Fallback to basic string conversion
            try:
                result = str(val) if val is not None else ""
                result = self._simplify_coefficients(result)
                return result if result not in ["0", "0.0"] else ""
            except:
                return ""

        # endregion Body

    def _simplify_coefficients(self, expression_str):
        # region Summary
        """
        Remove coefficient 1 from expressions like 1*I -> I, 1*t -> t
        Also handles more complex cases like 1*I*t -> I*t
        """
        # endregion Summary

        # region Body

        import re

        if not expression_str or expression_str.strip() == "":
            return expression_str

        result = expression_str

        # Handle coefficient 1 at the beginning: 1*variable -> variable
        result = re.sub(r'^1\*([a-zA-Z])', r'\1', result)

        # Handle coefficient 1 after operators: +1*variable -> +variable, -1*variable -> -variable
        result = re.sub(r'([+\-\s])1\*([a-zA-Z])', r'\1\2', result)

        # Handle spaces around 1*: " 1*I" -> " I"
        result = re.sub(r'\s1\*([a-zA-Z])', r' \1', result)

        # Handle coefficient 1 in parentheses: (1*I) -> (I)
        result = re.sub(r'\(1\*([a-zA-Z])', r'(\1', result)

        # Handle more complex cases like 1*I*t -> I*t
        result = re.sub(r'^1\*([a-zA-Z]\*[a-zA-Z])', r'\1', result)
        result = re.sub(r'([+\-\s])1\*([a-zA-Z]\*[a-zA-Z])', r'\1\2', result)

        # Clean up any double spaces that might result
        result = re.sub(r'\s+', ' ', result)

        return result.strip()

        # endregion Body

    def _clean_float_string(self, val, ndigits=4):
        # region Summary
        """
        Clean up float string representation.
        """
        # endregion Summary

        # region Body

        if abs(val) < 10 ** (-ndigits):
            return ""  # Return empty string instead of "0"

        rounded = round(val, ndigits)
        if rounded == int(rounded):
            int_val = int(rounded)
            return str(int_val) if int_val != 0 else ""
        else:
            # Remove trailing zeros
            result = f"{rounded:.{ndigits}f}".rstrip('0').rstrip('.')
            return result if result != "0" else ""

        # endregion Body

    def _clean_number_string(self, s):
        # region Summary
        """
        Clean up number string by removing trailing zeros and unnecessary decimals.
        """
        # endregion Summary

        # region Body

        import re

        # Pattern to match decimal numbers
        def clean_decimal(match):
            num_str = match.group(0)
            try:
                # Convert to float and back to remove trailing zeros
                num = float(num_str)
                if num == int(num):
                    return str(int(num))
                else:
                    return str(num).rstrip('0').rstrip('.')
            except:
                return num_str

        # Replace decimal numbers in the string
        result = re.sub(r'\d+\.\d+', clean_decimal, s)
        return result

        # endregion Body

    # endregion Private

    # region Public

    def get_matrix_entries(self):
        # region Summary
        """
        Extract all matrix entries and hyperparameters
        """
        # endregion Summary

        # region Body

        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        # at top of get_matrix_entries, after rows/cols are known
        if self._file_entries is not None:
            # Validate shape
            if len(self._file_entries) != rows or any(len(r) != cols for r in self._file_entries):
                raise ValueError("Loaded file entries do not match selected dimensions.")

            # Build hyperparameters as before
            hyper_parameters = dict(variable=self.variable_combo.currentText())
            if self.show_hyperparameters:
                hyper_parameters["discretes_count"] = self.discretes_count_spin.value()
                hyper_parameters["approximation_center"] = self.approximation_center_spin.value()
                hyper_parameters["scaling_coefficient"] = self.scaling_coefficient_spin.value()

            return (rows, cols), hyper_parameters, self._file_entries

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

        # endregion Body

    def all_entries_filled(self):
        # region Summary
        """
        Check if all matrix entries contain non-empty text OR a valid file has been loaded.
        """
        # endregion Summary

        # region Body

        # If file entries exist and match shape, treat as filled
        if self._file_entries is not None:
            rows = self.rows_spin.value()
            cols = self.cols_spin.value()
            if len(self._file_entries) == rows and all(len(r) == cols for r in self._file_entries):
                # ensure no empty strings inside
                return all(cell.strip() != "" for row in self._file_entries for cell in row)
            else:
                return False

        # Fall back to text widgets behavior
        return all(widget.text().strip() != "" for widget in self.entry_widgets)

        # endregion Body

    def clear_entries(self):
        # region Summary
        """
        Clear all matrix entries and also clear outputs.
        """
        # endregion Summary

        # region Body

        # Clear typed entries
        for widget in self.entry_widgets:
            widget.clear()

        # Clear outputs too
        if hasattr(self, "output_entry_widgets"):
            for w in self.output_entry_widgets:
                w.clear()

        # Clear any file-backed entries and filename
        self._file_entries = None
        self._loaded_filename = None

        # If dims are large (>10), keep inputs read-only; otherwise allow editing
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        if rows > 10 or cols > 10:
            self.set_input_fields_read_only(True)
        else:
            self.set_input_fields_read_only(False)

        # Signal change
        self.entries_changed.emit()

        # endregion Body

    def set_language(self, translations: dict):
        # region Summary
        """
        translations: a dict containing keys:
            'rows_label','cols_label','variable_label',
            'k_label','theta_label','h_label','placeholder',
            optionally 'parameters_title'
        """
        # endregion Summary

        # region Body

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

        # endregion Body

    def set_output_matrix(self, matrix, ndigits=4):
        # region Summary
        """
        Set the right-hand output grid to show `matrix`.
        `matrix` may be:
          - a sympy.Matrix
          - a nested list of numbers/expressions
          - a scalar (will be shown in a 1x1 output)
        `ndigits` controls numeric precision when possible.
        """
        # endregion Summary

        # region Body

        try:
            # First, try to apply rounding using the round_matrix function
            if hasattr(matrix, 'is_Matrix') and matrix.is_Matrix:
                # It's a SymPy Matrix - use round_matrix
                try:
                    rounded_matrix = round_matrix(matrix, ndigits=ndigits)
                except Exception:
                    # If rounding fails, use original matrix
                    rounded_matrix = matrix

                rows_out, cols_out = rounded_matrix.rows, rounded_matrix.cols
                data = [[rounded_matrix[i, j] for j in range(cols_out)] for i in range(rows_out)]

            elif hasattr(matrix, '__len__') and len(matrix) > 0 and hasattr(matrix[0], '__len__'):
                # It's a nested list - convert to SymPy Matrix, round, then convert back
                try:
                    temp_matrix = sp.Matrix(matrix)
                    rounded_matrix = round_matrix(temp_matrix, ndigits=ndigits)
                    rows_out, cols_out = rounded_matrix.rows, rounded_matrix.cols
                    data = [[rounded_matrix[i, j] for j in range(cols_out)] for i in range(rows_out)]
                except Exception:
                    # If conversion fails, use original data
                    rows_out = len(matrix)
                    cols_out = len(matrix[0]) if rows_out else 0
                    data = matrix

            else:
                # It's a scalar - wrap in 1x1 matrix and round
                try:
                    temp_matrix = sp.Matrix([[matrix]])
                    rounded_matrix = round_matrix(temp_matrix, ndigits=ndigits)
                    rows_out, cols_out = 1, 1
                    data = [[rounded_matrix[0, 0]]]
                except Exception:
                    # If rounding fails, use original scalar
                    rows_out, cols_out = 1, 1
                    data = [[matrix]]

        except Exception:
            # Fallback: handle without rounding
            if hasattr(matrix, 'is_Matrix') and matrix.is_Matrix:
                rows_out, cols_out = matrix.rows, matrix.cols
                data = [[matrix[i, j] for j in range(cols_out)] for i in range(rows_out)]
            elif hasattr(matrix, '__len__') and len(matrix) > 0 and hasattr(matrix[0], '__len__'):
                rows_out = len(matrix)
                cols_out = len(matrix[0]) if rows_out else 0
                data = matrix
            else:
                rows_out, cols_out = 1, 1
                data = [[matrix]]

        # Rebuild output grid if dimensions don't match
        if len(self.output_entry_widgets) != rows_out * cols_out:
            # Clear existing output widgets
            if hasattr(self, 'output_entry_widgets'):
                for widget in self.output_entry_widgets:
                    self.output_layout.removeWidget(widget)
                    widget.deleteLater()
            self.output_entry_widgets = []

            # Build new output grid
            for i in range(rows_out):
                for j in range(cols_out):
                    out_edit = QLineEdit()
                    out_edit.setReadOnly(True)
                    out_edit.setPlaceholderText("")
                    out_edit.setMinimumWidth(90)
                    out_edit.setMaximumWidth(130)
                    out_edit.setMinimumHeight(30)
                    out_edit.setMaximumHeight(35)
                    out_edit.setFrame(True)
                    out_edit.setStyleSheet("QLineEdit { background-color: #FBFBFB; }")
                    self.output_layout.addWidget(out_edit, i, j)
                    self.output_entry_widgets.append(out_edit)

        # Fill output fields with formatted values
        for i in range(rows_out):
            for j in range(cols_out):
                val = data[i][j]
                formatted_val = self._format_value_for_display(val, ndigits)
                idx = i * cols_out + j
                if idx < len(self.output_entry_widgets):
                    self.output_entry_widgets[idx].setText(formatted_val)

        # endregion Body

    def set_input_fields_read_only(self, readonly: bool):
        # region Summary
        """
        Set input widgets readOnly property (if they exist). Does not affect output widgets.
        """
        # endregion Summary

        # region Body

        # If we haven't built the grid yet, just store mode
        if not hasattr(self, "entry_widgets") or not self.entry_widgets:
            return
        for w in self.entry_widgets:
            w.setReadOnly(readonly)
            # optionally change style so read-only is visually distinct
            if readonly:
                w.setStyleSheet("QLineEdit { background-color: #EEEEEE; }")
            else:
                w.setStyleSheet("")  # revert to style by parent stylesheet

        # endregion Body

    def load_entries_from_txt(self, filepath: str):
        # region Summary
        """
        Load matrix entries from a text file and store them in self._file_entries.
        Current simple parser: lines -> split by whitespace or commas.
        The loaded entries must match the current rows x cols or raise ValueError.
        """
        # endregion Summary

        # region Body

        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
    
        # read file
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip() != ""]
    
        parsed = []
        for ln in lines:
            # split by whitespace or commas; remove empty tokens
            tokens = [
                tok.strip() for tok in ln.replace(",", " ").split() if tok.strip() != ""
            ]
            if tokens:
                parsed.append(tokens)
    
        # Flatten vs line-per-row: if file is provided as single-line or as matrix
        # If parsed is single row of many tokens, flatten and reshape row-major:
        flat = []
        if len(parsed) == 1 and len(parsed[0]) == rows * cols:
            flat = parsed[0]
        else:
            # if parsed has >= rows lines and each line has >= cols tokens, use first rows x cols
            for r in parsed:
                flat.extend(r)
    
        if len(flat) != rows * cols:
            raise ValueError(f"File contains {len(flat)} tokens but expected {rows*cols} entries (m={rows}, n={cols}).")
    
        # Arrange into list of lists (rows)
        entries = []
        idx = 0
        for i in range(rows):
            row = []
            for j in range(cols):
                row.append(flat[idx])
                idx += 1
            entries.append(row)
    
        # Store file-backed entries and set inputs to read-only (visual will be handled by MainWindow too)
        self._file_entries = entries

        self._loaded_filename = filepath

        # Populate the visible input QLineEdits so user gets visual confirmation, and make them editable:
        # If grid was previously built, fill the QLineEdit widgets (they exist in row-major order)
        if hasattr(self, 'entry_widgets') and len(self.entry_widgets) == rows * cols:
            for i in range(rows):
                for j in range(cols):
                    widget_idx = i * cols + j
                    self.entry_widgets[widget_idx].setText(entries[i][j])
            # Make inputs editable so user can tweak values after loading
            self.set_input_fields_read_only(False)
        else:
            # If for some reason widgets don't match shape, still keep entries stored; caller will trigger rebuild
            pass

        # Notify listeners (MainWindow) so they can enable Moore-Penrose buttons etc.
        self.entries_changed.emit()

        # endregion Body

    def has_loaded_file(self) -> bool:
        # region Summary
        """
        Return True if a file has been loaded and stored in the widget.
        """
        # endregion Summary

        # region Body

        return self._file_entries is not None

        # endregion Body

    # endregion Public

    # endregion Functions
