import sympy as sp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QPushButton, QMessageBox, QScrollArea, QCheckBox, QDialog, QTextEdit)

from .matrix_input_widget import MatrixInputWidget
from src.core.pseudoinverse import (pinv_type_I_II, pinv_type_III, pinv_type_IV)

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox


class MainWindow(QMainWindow):
    # region Constructor

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(":/icons/app_icon.png"))

        self.setWindowTitle("Generalized Inverse Calculator")

        self.resize(900, 500)

        # tabs = QTabWidget()
        self.tabs = QTabWidget()

        # Language selector in top-right corner of tab widget
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Հայերեն"])
        self.tabs.setCornerWidget(self.lang_combo, Qt.TopRightCorner)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)

        # Basic operations tab
        self.tabs.addTab(self._create_basic_tab(), "Basic Operations")

        # Generalized-inverse tab
        self.tabs.addTab(self._create_pinv_tab(), "Generalized Inverse")

        self.setCentralWidget(self.tabs)

        self._update_button_states()

        self.analytical_checkbox.stateChanged.connect(self._update_button_states)

        # region Translator

        # --- Translation data (English + Armenian) ---
        self.translations = {
            'en': {
                'app_title': "Generalized-Inverse Calculator",
                'tab_basic': "Basic Operations",
                'tab_pinv': "Generalized-Inverse",
                'btn_determinant': "Determinant",
                'btn_transpose': "Transpose",
                'btn_inverse': "Inverse",
                'analytical_checkbox': "Use analytical method?",
                'btn_calc_steps': "Calculation Steps",
                'btn_clear': "Clear Matrix Entries",
                'btn_export_pdf': "Export Steps as PDF",
                'dialog_save_pdf': "Save Calculation Steps as PDF",
                'dialog_export_complete': "Export Complete",
                'dialog_steps_saved_to': "Steps saved to:",
                'close': "Close",
                'parameters_title': 'Parameters',
                'rows_label': "Rows: m =",
                'cols_label': "Columns: n =",
                'variable_label': "Variable:",
                'k_label': "K =",
                'theta_label': "t\u03F8 =",
                'h_label': "H =",
                'placeholder': "e.g. 1+I*t",
                'input_error': "Input Error",
                'inverse_error': "Inverse Error",
                'cannot_invert': "Cannot invert matrix:\n{error}",
                'failed_compute': "Failed to compute {title}:\n{error}",
                'determinant_title': "Determinant",
                'transpose_title': "Transpose",
                'inverse_title': "Inverse",
                # If you want localized Moore-Penrose labels, add keys here:
                'moore_i': "Moore-Penrose I",
                'moore_ii': "Moore-Penrose II",
                'moore_iii': "Moore-Penrose III",
                'moore_iv': "Moore-Penrose IV",
            },
            'hy': {
                'app_title': "Ընդհանրացված հակադարձի հաշվիչ",
                'tab_basic': "Հիմնական գործողություններ",
                'tab_pinv': "Ընդհանրացված հակադարձ",
                'btn_determinant': "Դետերմինանտ",
                'btn_transpose': "Տրանսպոզ",
                'btn_inverse': "Հակադարձ",
                'analytical_checkbox': "Օգտագործե՞լ անալիտիկ եղանակը",
                'btn_calc_steps': "Հաշվարկի քայլեր",
                'btn_clear': "Մաքրել մատրիցի մուտքերը",
                'btn_export_pdf': "Արտահանել քայլերը PDF",
                'dialog_save_pdf': "Պահպանել հաշվարկի քայլերը PDF ֆորմատով",
                'dialog_export_complete': "Արտահանումն ավարտվեց",
                'dialog_steps_saved_to': "Քայլերը պահպանված են՝",
                'close': "Փակել",
                'parameters_title': 'Պարամետրեր',
                'rows_label': "Տողեր՝ m =",
                'cols_label': "Սյուներ՝ n =",
                'variable_label': "Փոփոխական՝",
                'k_label': "K =",
                'theta_label': "t\u03F8 =",
                'h_label': "H =",
                'placeholder': "օրինակ՝ 1+I*t",
                'input_error': "Մուտքի սխալ",
                'inverse_error': "Հակադարձի սխալ",
                'cannot_invert': "Չի հաջողվում հաշվել մատրիցի հակադարձը:\n{error}",
                'failed_compute': "Չհաջողվեց հաշվել {title}:\n{error}",
                'determinant_title': "Դետերմինանտ",
                'transpose_title': "Տրանսպոզ",
                'inverse_title': "Հակադարձ",
                'moore_i': "Մուր-Պենրոուզ I",
                'moore_ii': "Մուր-Պենրոուզ II",
                'moore_iii': "Մուր-Պենրոուզ III",
                'moore_iv': "Մուր-Պենրոուզ IV",
            }
        }

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

    # region Helper

    def _get_matrix(self, use_pinv=False):
        # region Summary
        """Read entries from the appropriate MatrixInputWidget and build a Sympy Matrix."""
        # endregion Summary

        # region Body

        widget = self.pinv_input if use_pinv else self.basic_input

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
            # QMessageBox.critical(self, "Input Error", str(e))
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

        # Enable Clear button if at least one matrix cell has text
        if hasattr(self, 'btn_clear'):
            has_any_entry = any(w.text().strip() != "" for w in self.pinv_input.entry_widgets)
            self.btn_clear.setEnabled(has_any_entry)

        # Enable Export‑PDF if Calculation Steps is enabled
        if hasattr(self, 'btn_export_pdf'):
            self.btn_export_pdf.setEnabled(self.btn_calc_steps.isEnabled())

        # endregion Pseudo-inverse tab

        # endregion Body

    def show_steps(self):
        # region Summary
        """Display the stored step-by-step derivation in its own scrollable dialog."""
        # endregion Summary

        # region Body

        # Create a modal dialog
        dlg = QDialog(self)
        # dlg.setWindowTitle("Calculation Steps")
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
        # btn_close = QPushButton("Close")
        btn_close = QPushButton(self.tr('close'))
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)

        dlg.exec_()

        # endregion Body

    def clear_pinv_entries(self):
        """Clear all pseudo-inverse matrix entries."""
        self.pinv_input.clear_entries()

    def export_steps_pdf(self):
        """Ask where to save, then write self._last_steps into a PDF."""
        # 1) Prompt for filename
        # fn, _ = QFileDialog.getSaveFileName(self, "Save Calculation Steps as PDF", "", "PDF Files (*.pdf)")
        fn, _ = QFileDialog.getSaveFileName(self, self.tr('dialog_save_pdf'), "", "PDF Files (*.pdf)")
        if not fn:
            return  # user cancelled

        # 2) Prepare a QTextDocument with the steps
        doc = QTextDocument()
        # we will build up an HTML string instead of plain text
        h_title = self.tr('btn_calc_steps')
        html = """
        <html>
          <head>
            <style>
              body { font-family: Helvetica, Arial, sans-serif; font-size: 12pt; }
              h1 { text-align: center; font-size: 16pt; }
              pre { 
                font-family: Courier, monospace; 
                background-color: #f7f7f7; 
                padding: 8px; 
                border: 1px solid #ccc; 
              }
              p { margin: 8px 0; }
            </style>
          </head>
          <body>
            <h1>Calculation Steps</h1>
        """

        # capture how many total steps there are
        total = len(self._last_steps)

        body_steps = self._last_steps[:total - 3]
        tail_steps = self._last_steps[total - 3:]

        html += "<ul>\n"

        # track whether we're inside a <li> for the current K
        in_li = False

        for step in body_steps:
            text = step.strip()
            escaped = (step.replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;'))

            if text.startswith("K ="):
                # close the previous <li> if any
                if in_li:
                    html += "</li>\n"
                # start a new bullet for this K
                html += f"  <li><strong>{escaped}</strong><br/>\n"
                in_li = True

            else:
                # still inside the current <li>, render sub‑lines
                if text.startswith('[') and '\n' in step:
                    # matrix‑style block
                    html += f"<pre>{step}</pre>\n"
                else:
                    # normal sub‑line
                    html += f"{escaped}<br/>\n"

        # after looping, close the last <li> if open
        if in_li:
            html += "</li>\n"

        # finally close the list
        html += "</ul>\n"

        for step in tail_steps:
            if step.strip().startswith('[') and '\n' in step:
                html += f"<pre>{step}</pre>\n"
            else:
                esc = step.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html += f"<p>{esc}</p>\n"

        # html += "</ul>\n"  close the final bullet list
        html += """
          </body>
        </html>
        """

        # now feed it to the QTextDocument
        doc.setHtml(html)

        # 3) Configure a QPrinter that outputs to PDF
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(fn)

        # 4) Render the document into the PDF
        doc.print_(printer)

        # 5) Let the user know we’re done
        # QMessageBox.information(self, "Export Complete", f"Steps saved to:\n{fn}")
        QMessageBox.information(self, self.tr('dialog_export_complete'), f"{self.tr('dialog_steps_saved_to')}\n{fn}")

    # endregion Helper

    # region Translator

    def on_language_changed(self, index):
        # index 0 -> English, 1 -> Armenian
        self.lang = 'en' if index == 0 else 'hy'
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
        # We created them in original order: 0..3 = I..IV
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

    # endregion Translator

    # region Basic

    # region Tab

    def _create_basic_tab(self):
        basic_tab = QWidget()

        # Make the first tab’s background azure
        basic_tab.setStyleSheet("background-color: azure;")

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
            # QMessageBox.information(self, "Determinant", f"{M.det()}")
            QMessageBox.information(self, self.tr('determinant_title'), f"{M.det()}")

    def calculate_transpose(self):
        _, _, M = self._get_matrix()
        if M is not None:
            # QMessageBox.information(self, "Transpose", f"{M.T}")
            QMessageBox.information(self, self.tr('transpose_title'), f"{M.T}")

    def calculate_inverse(self):
        _, _, M = self._get_matrix()
        if M is not None:
            try:
                inv = M.inv()
                # QMessageBox.information(self, "Inverse", f"{inv}")
                QMessageBox.information(self, self.tr('inverse_title'), f"{inv}")
            except Exception as e:
                # QMessageBox.warning(self, "Inverse Error", f"Cannot invert matrix:\n{e}")
                QMessageBox.warning(self, self.tr('inverse_error'), self.tr('cannot_invert').format(error=str(e)))

    # endregion Operations

    # endregion Basic

    # region Pseudo-inverse

    # region Tab

    def _create_pinv_tab(self):
        pin_tab = QWidget()

        # Make the second tab’s background mintcream
        pin_tab.setStyleSheet("background-color: mintcream;")

        layout  = QVBoxLayout(pin_tab)

        # Scroll area for large matrices
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.pinv_input = MatrixInputWidget(show_hyperparameters=True)
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
            # btn.setStyleSheet("""
            #     QPushButton {
            #         background-color: turquoise;
            #         border: 2px solid teal;
            #         color: #154a4a;
            #     }
            #     QPushButton:disabled {
            #         background-color: #95dbd4;
            #         border: 2px solid #477c7c;
            #         color: #487474;
            #     }
            # """)

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
        content_layout.addLayout(button_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Create a horizontal layout for both buttons
        button_row = QHBoxLayout()

        # Calculation Steps button
        self.btn_calc_steps = QPushButton("Calculation Steps")
        self.btn_calc_steps.setEnabled(False)
        self.btn_calc_steps.clicked.connect(self.show_steps)
        button_row.addWidget(self.btn_calc_steps)

        # Style Calculation Steps button
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

        # Clear Matrix Entries button
        self.btn_clear = QPushButton("Clear Matrix Entries")
        self.btn_clear.setEnabled(False)
        self.btn_clear.clicked.connect(self.clear_pinv_entries)
        button_row.addWidget(self.btn_clear)

        # Style Clear Matrix Entries button
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

        # Export PDF button
        self.btn_export_pdf = QPushButton("Export Steps as PDF")
        self.btn_export_pdf.setEnabled(False)  # start disabled
        self.btn_export_pdf.clicked.connect(self.export_steps_pdf)
        button_row.addWidget(self.btn_export_pdf)

        # Style Clear Matrix Entries button
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

        # Add the row to the main layout
        content_layout.addLayout(button_row)

        return pin_tab

    # endregion Tab

    # region Operations

    def _calculate_pinv(self, function, title):
        sizes, hyper_parameters, M = self._get_matrix(use_pinv=True)

        # record the analytical‐method choice
        hyper_parameters['use_analytical_method'] = self.analytical_checkbox.isChecked()

        print("---------------------------------------------------------")
        print(f"Sizes = {sizes}")
        print(f"Hyper-parameters = {hyper_parameters}")
        print(f"Matrix = {M}")

        if M is not None:
            try:
                result, steps = function(sizes, hyper_parameters, M)
                self._last_steps = steps
                QMessageBox.information(self, title, f"{result}")
                self.btn_calc_steps.setEnabled(True)
                self.btn_export_pdf.setEnabled(True)
            except Exception as e:
                # QMessageBox.warning(self, f"{title} Error", f"Failed to compute {title}:\n{e}")
                QMessageBox.warning(self, self.tr('failed_compute').format(title=title, error=str(e)),
                                    self.tr('failed_compute').format(title=title, error=str(e)))

    def calculate_pinv_I(self):
        self._calculate_pinv(function=pinv_type_I_II, title=self.tr('moore_i'))

    def calculate_pinv_II(self):
        self._calculate_pinv(function=pinv_type_I_II, title=self.tr('moore_ii'))

    def calculate_pinv_III(self):
        self._calculate_pinv(function=pinv_type_III, title=self.tr('moore_iii'))

    def calculate_pinv_IV(self):
        self._calculate_pinv(function=pinv_type_IV, title=self.tr('moore_iv'))

    # endregion Operations

    # endregion Pseudo-inverse

    # endregion Functions
