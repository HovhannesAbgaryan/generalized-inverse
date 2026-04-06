import sympy as sp
import json
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QPushButton, QMessageBox, QScrollArea, QCheckBox, QDialog,
                             QTextEdit, QFileDialog, QComboBox)
from PyQt5.QtPrintSupport import QPrinter

from .matrix_input_widget import MatrixInputWidget
from src.core.generalized_inverse import (ginv_type_I_II, ginv_type_III, ginv_type_IV)
from src.utils.rounding import round_matrix
from src.gui.errors_window import ErrorsWindow
from src.utils.calculation_steps import get_analytical_steps, get_numerical_analytical_steps
from src.utils.errors_calculation import calculate_errors

class MainWindow(QMainWindow):
    # region Constructor

    def __init__(self):
        super().__init__()

        # region Window

        self.setWindowIcon(QIcon(":/icons/app_icon.png"))
        self.setWindowTitle("Generalized Inverse Calculator")
        self.resize(1100, 500)

        # endregion Window

        # region Tabs

        self.tabs = QTabWidget()

        # region Language

        # Language selector in top-right corner of tab widget
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Հայերեն", "Русский"])
        self.tabs.setCornerWidget(self.lang_combo, Qt.TopRightCorner)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)

        # endregion Language

        # Basic operations tab
        self.tabs.addTab(self._create_basic_tab(), "Basic Operations")

        # Generalized inverse tab
        self.tabs.addTab(self._create_pinv_tab(), "Generalized Inverse")

        self.setCentralWidget(self.tabs)

        # endregion Tabs

        # region Calculation steps and errors

        self._last_errors = None
        self._errors_window = None

        # Generalized inverse matrix
        self._current_ginv_result = None

        # Intermediate results
        self._intermediate_results = None

        # Input matrix A(t)
        self._current_matrix = None

        # Hyperparameters used for the run
        self._current_hyper = None

        # endregion Calculation steps and errors

        self._update_button_states()

        self.analytical_checkbox.stateChanged.connect(self._update_button_states)

        # region Translator

        # Load translations from src/locales/<lang>.json files.
        # Each JSON file is named by its language code (e.g. en.json, hy.json, ru.json).
        _locales_dir = Path(__file__).resolve().parent.parent / 'locales'
        self.translations = {}
        if _locales_dir.is_dir():
            for _p in sorted(_locales_dir.glob('*.json')):
                try:
                    with open(_p, 'r', encoding='utf-8') as _f:
                        self.translations[_p.stem] = json.load(_f)
                except Exception as _e:
                    print(f"Warning: could not load locale {_p.name}: {_e}")

        # current language code:
        self.lang = 'en'

        # helper to fetch translations
        def tr(key):
            return self.translations.get(self.lang, {}).get(key, key)

        self.tr = tr  # attach to instance for easy use

        # endregion Translator

        self.apply_language()

    # endregion Constructor

    # region Functions

    # region Helpers

    def _get_matrix(self, use_ginv=False):
        # region Summary
        """
        Read entries from the appropriate MatrixInputWidget and build a Sympy Matrix.
        """
        # endregion Summary

        # region Body

        widget = self.pinv_input if use_ginv else self.basic_input

        try:
            sizes, hyper_parameters, entries = widget.get_matrix_entries()

            print(f"Sizes = {sizes}")
            print(f"Hyper-parameters = {hyper_parameters}")
            print(f"Entries = {entries}")

            t = sp.symbols(hyper_parameters["variable"], real=True)
            hyper_parameters["variable"] = t
            mat = sp.Matrix()
            for i in range(sizes[0]):
                row = [sp.parse_expr(element, local_dict=dict(t=t)) for element in entries[i]]
                mat = mat.row_insert(i, sp.Matrix([row]))

            return sizes, hyper_parameters, mat

        except Exception as e:
            QMessageBox.critical(self, self.tr('input_error'), str(e))
            return None

        # endregion Body

    def _update_button_states(self):
        # region Body

        # region Basic tab

        filled_basic = self.basic_input.all_entries_filled()
        self.btn_determinant.setEnabled(filled_basic)
        self.btn_transpose.setEnabled(filled_basic)
        self.btn_inverse.setEnabled(filled_basic)

        # endregion Basic tab

        # region Pseudo-inverse tab

        filled_pinv = self.pinv_input.all_entries_filled()
        for btn in self.pinv_buttons:
            btn.setEnabled(filled_pinv)

        # If “use analytical” is checked, disable III & IV
        if hasattr(self, 'analytical_checkbox') and self.analytical_checkbox.isChecked():
            # buttons 2 and 3 correspond to III and IV
            self.pinv_buttons[2].setEnabled(False)
            self.pinv_buttons[3].setEnabled(False)

        # --- Enable file load and set read-only when dims > 10 ---
        if hasattr(self, 'btn_load_file') and hasattr(self, 'pinv_input'):
            try:
                r = self.pinv_input.rows_spin.value()
                c = self.pinv_input.cols_spin.value()
                too_large = (r > 10) or (c > 10)

                # if a file is loaded, we want inputs editable so user can confirm/edit values;
                # if no file loaded and dims too large, make inputs readonly.
                has_file = self.pinv_input.has_loaded_file() if hasattr(self.pinv_input, 'has_loaded_file') else False

                want_readonly = too_large and (not has_file)
                self.pinv_input.set_input_fields_read_only(want_readonly)

                # Activate the button only when dims are too large (so user can load file)
                self.btn_load_file.setEnabled(too_large)
            except Exception:
                pass


        # Enable Clear button if at least one matrix cell has text
        if hasattr(self, 'btn_clear'):
            has_any_entry = any(w.text().strip() != "" for w in self.pinv_input.entry_widgets)
            self.btn_clear.setEnabled(has_any_entry)

        # Enable Export-PDF if Calculation Steps is enabled
        if hasattr(self, 'btn_export_pdf'):
            self.btn_export_pdf.setEnabled(self.btn_calc_steps.isEnabled())

        # endregion Pseudo-inverse tab

        # endregion Body

    def load_matrix_from_file(self):
        """Open a dialog to choose a .txt file and pass it to MatrixInputWidget for parsing."""
        fn, _ = QFileDialog.getOpenFileName(self, self.tr("dialog_open_file"), "", "Text Files (*.txt)")
        if not fn:
            return
    
        try:
            # this method will be implemented in MatrixInputWidget (see next section)
            self.pinv_input.load_entries_from_txt(fn)
            # After loading from file, update buttons / states
            self._update_button_states()
            # Optionally notify user that loading succeeded (you can remove if you prefer silent)
            QMessageBox.information(
                self,
                self.tr("dialog_export_complete"),
                f"{self.tr('dialog_steps_saved_to')}\n{fn}",
            )  # small re-use of existing message
        except Exception as e:
            QMessageBox.warning(
                self,
                self.tr("file_load_error").format(error=str(e)),
                self.tr("file_load_error").format(error=str(e)),
            )

    def clear_ginv_entries(self):
        """Clear all pseudo-inverse matrix entries."""
        self.pinv_input.clear_entries()
        self._reset_errors()

    # region Calculation Steps

    def show_steps(self):
        # region Summary
        """Display the stored step-by-step derivation in its own scrollable dialog."""
        # endregion Summary

        # region Body

        # Create a modal dialog
        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr('btn_calc_steps'))
        dlg.resize(600, 400)

        # Layout
        layout = QVBoxLayout(dlg)

        # Read-only text area for the steps
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setPlainText("\n".join(self._last_steps))
        layout.addWidget(text_area)

        # Close button at the bottom
        btn_close = QPushButton(self.tr('close'))
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)

        dlg.exec_()

        # endregion Body

    def _on_calc_steps_clicked(self):
        """Compute (if needed) calculation steps on demand and show them."""
        # If we already have the steps cached, just show them
        if getattr(self, "_last_steps", None):
            self.show_steps()
            return
    
        # Ensure we have what we need
        if self._intermediate_results is None or self._current_matrix is None:
            QMessageBox.warning(
                self,
                self.tr("input_error"),
                self.tr("failed_compute").format(
                    title=self.tr("btn_calc_steps"), error="Missing intermediate data"
                ),
            )
            return
    
        # Provide immediate UI feedback
        from PyQt5.QtWidgets import QApplication
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.btn_calc_steps.setEnabled(False)
        self.errors_button.setEnabled(False)
        try:
            real_matrix, imaginary_matrix = self._current_matrix.as_real_imag()
            if self._current_hyper["use_analytical_method"]:
                steps = get_analytical_steps(self._current_matrix, real_matrix, imaginary_matrix,
                                             self._current_hyper['method'], self._intermediate_results, self._current_ginv_result)
            else:
                steps = get_numerical_analytical_steps(self._current_matrix, real_matrix, imaginary_matrix,
                                                       self._current_hyper, self._intermediate_results, self._current_ginv_result)

            # cache and show
            self._last_steps = steps

            # enable export PDF now that we have steps
            if hasattr(self, "btn_export_pdf"):
                self.btn_export_pdf.setEnabled(True)

            # show them using your existing display method
            self.show_steps()

        except Exception as e:
            QMessageBox.warning(self, self.tr("failed_compute").format(title=self.tr("btn_calc_steps"), error=str(e)), self.tr("failed_compute").format(title=self.tr("btn_calc_steps"), error=str(e)))
        finally:
            QApplication.restoreOverrideCursor()
            # restore button states (errors_button should be enabled if we have intermediate results)
            if hasattr(self, "btn_calc_steps"):
                self.btn_calc_steps.setEnabled(True)
            if hasattr(self, "errors_button"):
                self.errors_button.setEnabled(self._intermediate_results is not None)

    def export_steps_pdf(self):
        """Ask where to save, then write self._last_steps into a PDF with proper formatting."""
        fn, _ = QFileDialog.getSaveFileName(self, self.tr('dialog_save_pdf'), "", "PDF Files (*.pdf)")
        if not fn:
            return

        def tidy_numbers(s: str) -> str:
            """Remove trailing zeros from decimal numbers in a string."""
            import re
            def repl(m):
                num = m.group(0)
                if '.' in num:
                    num2 = num.rstrip('0').rstrip('.')
                    if num2 == '' or num2 == '-':
                        return num
                    return num2
                return num

            return re.sub(r'(?<![\w.])(-?\d+\.\d+)(?![\w.])', repl, s)

        def simplify_coefficients_for_pdf(expression_str):
            """Apply the same coefficient simplification as the UI for PDF export."""
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

        def format_step_for_pdf(step):
            """Apply both number tidying and coefficient simplification."""
            # First tidy numbers
            tidied = tidy_numbers(step)
            # Then simplify coefficients
            simplified = simplify_coefficients_for_pdf(tidied)
            return simplified

        doc = QTextDocument()
        h_title = self.tr('pdf_title')
        html_content = f"""
        <html>
          <head>
            <style>
              body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12pt; }}
              h1 {{ text-align: center; font-size: 16pt; }}
              pre {{
                font-family: Courier, monospace;
                background-color: #f7f7f7;
                padding: 8px;
                border: 1px solid #ccc;
                white-space: pre-wrap;
                word-wrap: break-word;
              }}
              p {{ margin: 8px 0; }}
            </style>
          </head>
          <body>
            <h1>{h_title}</h1>
        """

        total = len(self._last_steps)
        body_steps = self._last_steps[:total - 3] if total > 3 else self._last_steps
        tail_steps = self._last_steps[total - 3:] if total > 3 else []

        html_content += "<ul>\n"
        in_li = False

        for step in body_steps:
            # Apply enhanced formatting
            formatted_step = format_step_for_pdf(step)

            text = formatted_step.strip()
            escaped = (formatted_step.replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;'))

            if text.startswith("K ="):
                if in_li:
                    html_content += "</li>\n"
                html_content += f"  <li><strong>{escaped}</strong><br/>\n"
                in_li = True
            else:
                if text.startswith('[') and '\n' in formatted_step:
                    html_content += f"<pre>{escaped}</pre>\n"
                else:
                    html_content += f"{escaped}<br/>\n"

        if in_li:
            html_content += "</li>\n"
        html_content += "</ul>\n"

        for step in tail_steps:
            formatted_step = format_step_for_pdf(step)

            if formatted_step.strip().startswith('[') and '\n' in formatted_step:
                escaped = formatted_step.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_content += f"<pre>{escaped}</pre>\n"
            else:
                escaped = formatted_step.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_content += f"<p>{escaped}</p>\n"

        html_content += """
          </body>
        </html>
        """

        doc.setHtml(html_content)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(fn)
        doc.print_(printer)

        QMessageBox.information(self, self.tr('dialog_export_complete'), f"{self.tr('dialog_steps_saved_to')}\n{fn}")

    # endregion Calculation Steps

    # region Calculation Errors

    def _show_errors_window(self):
        """Open the errors window as an independent top-level window."""
        if not self._last_errors:
            return

        # Close any existing errors window first (if present)
        try:
            if getattr(self, "_errors_window", None) is not None:
                try:
                    # close existing; it is top-level so this won't affect main window
                    self._errors_window.close()
                except Exception:
                    # ignore errors during close
                    pass
                # remove reference so a new instance is created
                self._errors_window = None
        except Exception:
            # defensive: ensure we don't crash here
            self._errors_window = None

        # Create a new ErrorsWindow WITHOUT parenting it to the main window.
        # Pass MainWindow.tr as translator so ErrorsWindow can localize strings.
        try:
            self._errors_window = ErrorsWindow(
                self._last_errors,
                translator=self.tr,
                all_translations=self.translations,
            )
            # Show non-modally (user can still interact with main window)
            self._errors_window.show()
        except Exception as e:
            # If anything goes wrong, show a friendly message instead of crashing
            import traceback

            traceback.print_exc()
            QMessageBox.warning(
                self,
                self.tr("input_error"),
                f"{self.tr('file_load_error').format(error=str(e))}\n\n(See console for traceback)",
            )
            self._errors_window = None

    def _on_errors_clicked(self):
        """Compute (if needed) errors on demand and open the errors window."""
        # If cached, show immediately
        if getattr(self, "_last_errors", None):
            self._show_errors_window()
            return
    
        # Check prereqs
        if self._intermediate_results is None or self._current_matrix is None:
            QMessageBox.warning(
                self,
                self.tr("input_error"),
                self.tr("failed_compute").format(
                    title=self.tr("btn_show_errors"), error="Missing intermediate data"
                ),
            )
            return
    
        # Provide UI feedback
        from PyQt5.QtWidgets import QApplication
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.errors_button.setEnabled(False)
        self.btn_calc_steps.setEnabled(False)
        try:
            errors = calculate_errors(self._current_matrix, self._current_ginv_result, self._current_hyper)

            self._last_errors = errors
            # open the errors window (your existing method expects _last_errors)
            self._show_errors_window()
        except Exception as e:
            QMessageBox.warning(self, self.tr("failed_compute").format(title=self.tr("btn_show_errors"), error=str(e)), self.tr("failed_compute").format(title=self.tr("btn_show_errors"), error=str(e)))
            self._last_errors = None
        finally:
            QApplication.restoreOverrideCursor()
            # restore states
            if hasattr(self, "errors_button"):
                self.errors_button.setEnabled(self._intermediate_results is not None and self._last_errors is not None)
            if hasattr(self, "btn_calc_steps"):
                self.btn_calc_steps.setEnabled(True)

    def _reset_errors(self):
        """Clear stored errors and cached intermediates and disable the errors button."""
        self._last_errors = None
        self._last_steps = None
        self._intermediate_results = None
        self._current_ginv_result = None
        self._current_matrix = None
        self._current_hyper = None
        if hasattr(self, "errors_button"):
            self.errors_button.setEnabled(False)
        if hasattr(self, "btn_calc_steps"):
            self.btn_calc_steps.setEnabled(False)
        if hasattr(self, "btn_export_pdf"):
            self.btn_export_pdf.setEnabled(False)

    # endregion Calculation Errors

    # endregion Helpers

    # region Translator

    def on_language_changed(self, index):
        # Map combo index -> language code
        codes = ["en", "hy", "ru"]

        # default to 'en' if index is out of range
        self.lang = codes[index] if 0 <= index < len(codes) else "en"
        self.apply_language()

    def apply_language(self):
        """Apply translations to all UI elements (called whenever language changes)."""
        # Window / tabs
        self.setWindowTitle(self.tr('app_title'))
        # set tab texts (tab 0 = basic, tab 1 = pinv)
        self.tabs.setTabText(0, self.tr('tab_basic'))
        self.tabs.setTabText(1, self.tr('tab_pinv'))

        # Basic tab buttons
        self.btn_determinant.setText(self.tr('btn_determinant'))
        self.btn_transpose.setText(self.tr('btn_transpose'))
        self.btn_inverse.setText(self.tr('btn_inverse'))

        # Pseudo-inverse tab UI
        self.analytical_checkbox.setText(self.tr('analytical_checkbox'))
        self.btn_calc_steps.setText(self.tr('btn_calc_steps'))
        self.btn_clear.setText(self.tr('btn_clear'))
        self.btn_export_pdf.setText(self.tr('btn_export_pdf'))

        # Moore-Penrose buttons: use translations if present
        # We created them in original order: 0..3 = I...IV
        self.pinv_buttons[0].setText(self.tr('moore_i'))
        self.pinv_buttons[1].setText(self.tr('moore_ii'))
        self.pinv_buttons[2].setText(self.tr('moore_iii'))
        self.pinv_buttons[3].setText(self.tr('moore_iv'))

        # Tell both matrix widgets to update their labels/placeholders
        # (they now implement set_language — see matrix_input_widget changes below)
        if hasattr(self, 'basic_input'):
            self.basic_input.set_language(self.translations[self.lang])
        if hasattr(self, 'pinv_input'):
            self.pinv_input.set_language(self.translations[self.lang])

        if hasattr(self, "btn_load_file"):
            self.btn_load_file.setText(self.tr("btn_load_file"))

        if hasattr(self, "errors_button"):
            self.errors_button.setText(self.tr("btn_show_errors"))

        if getattr(self, "_errors_window", None) is not None:
            try:
                self._errors_window.refresh_translations()
            except Exception:
                pass


    # endregion Translator

    # region Basic Tab

    # region Tab

    def _create_basic_tab(self):
        basic_tab = QWidget()

        # Make the first tab’s background mintcream
        basic_tab.setStyleSheet("background-color: mintcream;")

        layout = QVBoxLayout(basic_tab)
        self.basic_input = MatrixInputWidget(show_hyperparameters=False)
        layout.addWidget(self.basic_input)

        # Horizontal layout for the buttons
        button_layout = QHBoxLayout()

        self.btn_determinant = QPushButton("Determinant")
        self.btn_transpose = QPushButton("Transpose")
        self.btn_inverse = QPushButton("Inverse")

        for btn in (self.btn_determinant, self.btn_transpose, self.btn_inverse):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: mediumseagreen;
                    border: 2px solid darkgreen;
                    color: #0a450a;
                }
                QPushButton:disabled {
                    background-color: #7faf94;
                    border: 2px solid #477447;
                    color: #345434;
                }
            """)

        for btn, handler in [(self.btn_determinant, self.calculate_determinant),
                             (self.btn_transpose, self.calculate_transpose),
                             (self.btn_inverse, self.calculate_inverse)]:
            btn.clicked.connect(handler)
            button_layout.addWidget(btn)

        self.basic_input.entries_changed.connect(self._update_button_states)
        layout.addLayout(button_layout)

        return basic_tab

    # endregion Tab

    # region Operations

    def calculate_determinant(self):
        _, _, M = self._get_matrix()
        if M is not None:
            try:
                det = M.det()
                # wrap 1x1 Matrix so we can use round_matrix
                det_mat = sp.Matrix([[det]])
                rounded = round_matrix(det_mat, ndigits=4)
                try:
                    self.basic_input.set_output_matrix(rounded)
                except Exception:
                    QMessageBox.information(self, self.tr('determinant_title'), f"{det}")
            except Exception as e:
                QMessageBox.warning(self,
                                    self.tr('failed_compute').format(title=self.tr('determinant_title'), error=str(e)),
                                    self.tr('failed_compute').format(title=self.tr('determinant_title'), error=str(e)))

    def calculate_transpose(self):
        _, _, M = self._get_matrix()
        if M is not None:
            try:
                trans = M.T
                rounded = round_matrix(trans, ndigits=4) if isinstance(trans, sp.Matrix) else trans
                try:
                    self.basic_input.set_output_matrix(rounded)
                except Exception:
                    QMessageBox.information(self, self.tr('transpose_title'), f"{trans}")
            except Exception as e:
                QMessageBox.warning(self,
                                    self.tr('failed_compute').format(title=self.tr('transpose_title'), error=str(e)),
                                    self.tr('failed_compute').format(title=self.tr('transpose_title'), error=str(e)))

    def calculate_inverse(self):
        _, _, M = self._get_matrix()
        if M is not None:
            try:
                inv = M.inv()
                try:
                    rounded = round_matrix(inv, ndigits=4) if isinstance(inv, sp.Matrix) else inv
                    self.basic_input.set_output_matrix(rounded)
                except Exception:
                    QMessageBox.information(self, self.tr('inverse_title'), f"{inv}")
            except Exception as e:
                QMessageBox.warning(self, self.tr('inverse_error'), self.tr('cannot_invert').format(error=str(e)))

    # endregion Operations

    # endregion Basic Tab

    # region Generalized Inverse Tab

    # region Tab

    def _create_pinv_tab(self):
        pin_tab = QWidget()

        # Make the second tab’s background azure
        pin_tab.setStyleSheet("background-color: azure;")

        layout  = QVBoxLayout(pin_tab)

        # Scroll area for large matrices
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.pinv_input = MatrixInputWidget(show_hyperparameters=True)

        # ensure MainWindow reacts to dimension changes
        self.pinv_input.rows_spin.valueChanged.connect(self._update_button_states)
        self.pinv_input.cols_spin.valueChanged.connect(self._update_button_states)

        content_layout.addWidget(self.pinv_input)

        self.analytical_checkbox = QCheckBox("Use analytical method?")
        content_layout.addWidget(self.analytical_checkbox)

        # Horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Buttons for each pseudo-inverse type
        self.pinv_buttons = []
        for label, handler in [
            ("Moore-Penrose I",   self.calculate_pinv_I),
            ("Moore-Penrose II",  self.calculate_pinv_II),
            ("Moore-Penrose III", self.calculate_pinv_III),
            ("Moore-Penrose IV",  self.calculate_pinv_IV),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #40e0d0;
                    border: 2px solid #00a89a;
                    color: #154a4a;
                }
                QPushButton:disabled {
                    background-color: #c2fcf3;
                    border: 2px solid #8bc3bb;
                    color: #487474;
                }
            """)

            btn.clicked.connect(handler)
            btn.setEnabled(False)  # Start disabled
            self.pinv_buttons.append(btn)
            button_layout.addWidget(btn)

        self.pinv_input.entries_changed.connect(self._update_button_states)
        self.pinv_input.entries_changed.connect(self._reset_errors)
        content_layout.addLayout(button_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Create a horizontal layout for both buttons
        button_row = QHBoxLayout()

        # region Load Matrix from File

        # Button
        self.btn_load_file = QPushButton(self.tr('btn_load_file'))  # text will be localized in apply_language
        self.btn_load_file.setEnabled(False)  # disabled by default
        self.btn_load_file.clicked.connect(self.load_matrix_from_file)
        button_row.addWidget(self.btn_load_file)

        # Style
        self.btn_load_file.setStyleSheet("""
            QPushButton {
                background-color: #2ec66f;
                border: 2px solid #245d4b;
                color: #245d4b;
            }
            QPushButton:disabled {
                background-color: #8bbeac;
                border: 2px solid #387969;
                color: #15584e;
            }
        """)

        # endregion Load Matrix from File

        # region Clear Matrix Entries

        # Button
        self.btn_clear = QPushButton("Clear Matrix Entries")
        self.btn_clear.setEnabled(False)
        self.btn_clear.clicked.connect(self.clear_ginv_entries)
        button_row.addWidget(self.btn_clear)

        # Style
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #7dc5f5;
                border: 2px solid #0d3d5c;
                color: #092e46;
            }
            QPushButton:disabled {
                background-color: #afd1e8;
                border: 2px solid #264558;
                color: #2a3b46;
            }
        """)

        # endregion Clear Matrix Entries

        # region Calculation Steps

        # Button
        self.btn_calc_steps = QPushButton("Calculation Steps")
        self.btn_calc_steps.setEnabled(False)
        self.btn_calc_steps.clicked.connect(self._on_calc_steps_clicked)
        button_row.addWidget(self.btn_calc_steps)

        # Style
        self.btn_calc_steps.setStyleSheet("""
            QPushButton {
                background-color: #2ec66f;
                border: 2px solid #245d4b;
                color: #245d4b;
            }
            QPushButton:disabled {
                background-color: #8bbeac;
                border: 2px solid #387969;
                color: #15584e;
            }
        """)

        # endregion Calculation Steps

        # region Export PDF

        # Button
        self.btn_export_pdf = QPushButton("Export Steps as PDF")
        self.btn_export_pdf.setEnabled(False)  # start disabled
        self.btn_export_pdf.clicked.connect(self.export_steps_pdf)
        button_row.addWidget(self.btn_export_pdf)

        # Style
        self.btn_export_pdf.setStyleSheet("""
            QPushButton {
                background-color: #7dc5f5;
                border: 2px solid #0d3d5c;
                color: #092e46;
            }
            QPushButton:disabled {
                background-color: #afd1e8;
                border: 2px solid #264558;
                color: #2a3b46;
            }
        """)

        # endregion Export PDF

        # region Show Errors

        # Button
        self.errors_button = QPushButton("Show Errors")
        self.errors_button.setEnabled(False)  # disabled by default
        self.errors_button.clicked.connect(self._on_errors_clicked)
        button_row.addWidget(self.errors_button)

        # Style
        self.errors_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2ec66f;
                        border: 2px solid #245d4b;
                        color: #245d4b;
                    }
                    QPushButton:disabled {
                        background-color: #8bbeac;
                        border: 2px solid #387969;
                        color: #15584e;
                    }
                """)

        # endregion Show Errors

        # Add the row to the main layout
        content_layout.addLayout(button_row)

        return pin_tab

    # endregion Tab

    # region Operations

    def _calculate_pinv(self, function, title):
        sizes, hyper_parameters, M = self._get_matrix(use_ginv=True)

        # record the analytical‐method choice
        hyper_parameters['use_analytical_method'] = self.analytical_checkbox.isChecked()
        hyper_parameters["method"] = title

        print("---------------------------------------------------------")
        print(f"Sizes = {sizes}")
        print(f"Hyper-parameters = {hyper_parameters}")
        print(f"Matrix = {M}")

        if M is not None:
            try:
                result, intermediate_results = function(sizes, hyper_parameters, M)

                # store for later on-demand computations
                self._current_matrix = M
                self._current_ginv_result = result
                self._intermediate_results = intermediate_results
                self._current_hyper = hyper_parameters

                # clear any cached steps/errors from previous runs
                self._last_steps = None
                self._last_errors = None

                # If result is a SymPy Matrix, round numeric entries using your rounding.py
                try:
                    if hasattr(result, "is_Matrix") and result.is_Matrix:
                        rounded_result = round_matrix(result, ndigits=4)
                    else:
                        # If result is scalar or list, try to wrap into 1x1 matrix for rounding,
                        # otherwise just pass it through.
                        rounded_result = result
                except Exception:
                    # If rounding fails for any reason, fallback to original result
                    rounded_result = result

                # Display in the right-hand UI (read-only) created in MatrixInputWidget
                try:
                    self.pinv_input.set_output_matrix(rounded_result)
                except Exception as e:
                    # Fallback: show message box like before if widget update fails
                    QMessageBox.information(self, title, f"{result}")

                # enable the "calculate steps" and "errors" buttons so user can request them on demand
                # they will compute only when clicked
                if hasattr(self, 'btn_calc_steps'):
                    self.btn_calc_steps.setEnabled(True)
                if hasattr(self, 'errors_button'):
                    # only enable if intermediate results exist (defensive)
                    self.errors_button.setEnabled(self._intermediate_results is not None)

                # also enable export pdf (if appropriate)
                if hasattr(self, 'btn_export_pdf'):
                    self.btn_export_pdf.setEnabled(False)  # stays off until steps are generated

            except Exception as e:
                QMessageBox.warning(self, self.tr('failed_compute').format(title=title, error=str(e)),
                                    self.tr('failed_compute').format(title=title, error=str(e)))

    def calculate_pinv_I(self):
        self._calculate_pinv(function=ginv_type_I_II, title=self.tr('moore_i'))

    def calculate_pinv_II(self):
        self._calculate_pinv(function=ginv_type_I_II, title=self.tr('moore_ii'))

    def calculate_pinv_III(self):
        self._calculate_pinv(function=ginv_type_III, title=self.tr('moore_iii'))

    def calculate_pinv_IV(self):
        self._calculate_pinv(function=ginv_type_IV, title=self.tr('moore_iv'))

    # endregion Operations

    # endregion Generalized Inverse Tab

    # endregion Functions
