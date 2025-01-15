import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QWidget, QMessageBox, QHBoxLayout,  QComboBox, QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView, QCheckBox, QTextEdit
)
import pandas as pd
from openpyxl import load_workbook
import xlrd
import os

BACKEND_URL = "http://127.0.0.1:5000"

class FirstPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.next_button = QPushButton("Siguiente")
        self.status_label = QLabel("Cargando plantillas...")

        self.layout.addWidget(QLabel("Selecciona una Plantilla:"))
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        # Botón para avanzar a la segunda página
        self.next_button.clicked.connect(self.go_to_next_page)

        # Cargar plantillas desde el backend
        self.load_templates()

    def load_templates(self):
        try:
            response = requests.get(f"{BACKEND_URL}/templates")
            if response.status_code == 200:
                templates = response.json()
                for template in templates:
                    self.list_widget.addItem(template["name"])
                self.status_label.setText("Plantillas cargadas correctamente.")
            else:
                self.status_label.setText("Error al cargar plantillas.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def go_to_next_page(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            self.parent().selected_template = selected_item.text()
            self.parent().setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una plantilla.")

class SecondPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.back_button = QPushButton("Regresar")
        self.next_button = QPushButton("Seleccionar Bases de Datos")
        self.status_label = QLabel("Cargando bases de datos...")

        self.layout.addWidget(QLabel("Selecciona las Bases de Datos:"))
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        # Botones
        self.back_button.clicked.connect(self.go_to_previous_page)
        self.next_button.clicked.connect(self.store_selected_databases)

        # Cargar bases de datos desde el backend
        self.load_databases()

    def load_databases(self):
        try:
            response = requests.get(f"{BACKEND_URL}/databases")
            if response.status_code == 200:
                databases = response.json()
                for db in databases:
                    self.list_widget.addItem(f"{db['name']} ({db['path']})")
                self.status_label.setText("Bases de datos cargadas correctamente.")
            else:
                self.status_label.setText("Error al cargar bases de datos.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def store_selected_databases(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            selected_databases = [item.text() for item in selected_items]
            self.parent().selected_databases = selected_databases
            QMessageBox.information(self, "Bases Seleccionadas", f"Bases seleccionadas:\n{', '.join(selected_databases)}")
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona al menos una base de datos.")

    def go_to_previous_page(self):
        self.parent().setCurrentIndex(0)

class ThirdPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        
        # Componentes de la interfaz
        self.file_label = QLabel("Archivo seleccionado:")
        self.sheet_selector = QComboBox()
        self.table_preview = QTableWidget()
        self.header_input = QLineEdit()
        self.preview_button = QPushButton("Previsualizar Hoja")
        self.next_button = QPushButton("Seleccionar Encabezado")
        self.back_button = QPushButton("Regresar")

        # Configurar diseño
        self.layout.addWidget(self.file_label)
        self.layout.addWidget(QLabel("Selecciona una hoja del archivo:"))
        self.layout.addWidget(self.sheet_selector)
        self.layout.addWidget(self.preview_button)
        self.layout.addWidget(QLabel("Vista previa de la hoja:"))
        self.layout.addWidget(self.table_preview)
        self.layout.addWidget(QLabel("Selecciona la fila de encabezados (base 1):"))
        self.layout.addWidget(self.header_input)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

        # Eventos de botones
        self.preview_button.clicked.connect(self.preview_sheet)
        self.next_button.clicked.connect(self.select_header_row)
        self.back_button.clicked.connect(self.go_to_previous_page)

        # Variables
        self.selected_file = None
        self.selected_sheet = None
        self.selected_header_row = None

    def load_file(self, file_path):
        """Carga las hojas del archivo Excel seleccionado en el ComboBox."""
        self.selected_file = file_path
        self.file_label.setText(f"Archivo seleccionado: {file_path}")
        self.sheet_selector.clear()

        try:
            extension = os.path.splitext(file_path)[1].lower()
            if extension == ".xlsx":
                workbook = load_workbook(filename=file_path, read_only=True)
                sheets = workbook.sheetnames
            elif extension == ".xls":
                workbook = xlrd.open_workbook(file_path)
                sheets = workbook.sheet_names()
            else:
                QMessageBox.warning(self, "Error", "Formato de archivo no soportado.")
                return

            self.sheet_selector.addItems(sheets)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el archivo: {e}")

    def preview_sheet(self):
        """Carga y muestra una vista previa de la hoja seleccionada."""
        self.selected_sheet = self.sheet_selector.currentText()
        if not self.selected_file or not self.selected_sheet:
            QMessageBox.warning(self, "Error", "Por favor selecciona un archivo y una hoja.")
            return

        try:
            response = requests.post(f"{BACKEND_URL}/preview-sheet", json={
                'file_path': self.selected_file,
                'sheet_name': self.selected_sheet,
                'header_row': self.selected_header_row
            })
            
            if response.status_code == 200:
                data = response.json()
                self.show_table_from_data(data['columns'], data['data'])
            else:
                QMessageBox.warning(self, "Error", "No se pudo cargar la hoja.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar la hoja: {e}")

    def show_table(self, df):
        """Muestra un DataFrame en la tabla de vista previa."""
        self.table_preview.setColumnCount(len(df.columns))
        self.table_preview.setRowCount(len(df))

        # Agregar encabezados
        self.table_preview.setHorizontalHeaderLabels(df.columns)

        # Agregar datos
        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.table_preview.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

        # Ajustar el ancho de las columnas
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def select_header_row(self):
        """Selecciona la fila de encabezados para usar en el procesamiento."""
        try:
            header_row = int(self.header_input.text()) - 1
            if header_row < 0:
                QMessageBox.warning(self, "Error", "La fila debe ser mayor a 0.")
                return

            self.selected_header_row = header_row
            QMessageBox.information(
                self, "Fila Seleccionada", f"Fila de encabezados seleccionada: {header_row + 1}"
            )
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingresa un número válido.")

    def go_to_previous_page(self):
        self.parent().setCurrentIndex(1)

class FourthPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        # Componentes de la interfaz
        self.sheet_label = QLabel("Hoja seleccionada:")
        self.table_preview = QTableWidget()
        self.graph_selector_label = QLabel("Selecciona los gráficos a realizar:")
        self.bar_chart_checkbox = QCheckBox("Bar Chart")
        self.time_series_checkbox = QCheckBox("Time Series")
        self.column_selector_label = QLabel("Selecciona las columnas para el gráfico:")
        self.x_column_dropdown = QComboBox()
        self.y_column_dropdown = QComboBox()
        self.save_button = QPushButton("Guardar Selección")
        self.back_button = QPushButton("Regresar")

        # Configuración del layout
        self.layout.addWidget(self.sheet_label)
        self.layout.addWidget(self.table_preview)
        self.layout.addWidget(self.graph_selector_label)
        self.layout.addWidget(self.bar_chart_checkbox)
        self.layout.addWidget(self.time_series_checkbox)
        self.layout.addWidget(self.column_selector_label)
        self.layout.addWidget(QLabel("Columna para el eje X:"))
        self.layout.addWidget(self.x_column_dropdown)
        self.layout.addWidget(QLabel("Columna para el eje Y:"))
        self.layout.addWidget(self.y_column_dropdown)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

        # Eventos
        self.save_button.clicked.connect(self.save_selections)
        self.back_button.clicked.connect(self.go_to_previous_page)

        # Variables
        self.selected_sheet = None
        self.selected_file = None
        self.selected_graphs = []
        self.selected_columns = {}

    def load_sheet(self, file_path, sheet_name, header_row):
        """Carga la hoja seleccionada en la tabla y configura las columnas."""
        self.selected_file = file_path
        self.selected_sheet = sheet_name

        self.sheet_label.setText(f"Hoja seleccionada: {sheet_name}")
        try:
            # Leer la hoja con la fila de encabezados seleccionada
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            self.show_table(df)

            # Cargar nombres de columnas en los ComboBox
            self.x_column_dropdown.clear()
            self.y_column_dropdown.clear()
            self.x_column_dropdown.addItems(df.columns)
            self.y_column_dropdown.addItems(df.columns)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar la hoja: {e}")

    def show_table(self, df):
        """Muestra un DataFrame en la tabla de vista previa."""
        self.table_preview.setColumnCount(len(df.columns))
        self.table_preview.setRowCount(len(df))

        # Agregar encabezados
        self.table_preview.setHorizontalHeaderLabels(df.columns)

        # Agregar datos
        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.table_preview.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

        # Ajustar el ancho de las columnas
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def save_selections(self):
        """Guarda las selecciones realizadas para los gráficos y columnas."""
        # Validar que al menos un gráfico esté seleccionado
        if not (self.bar_chart_checkbox.isChecked() or self.time_series_checkbox.isChecked()):
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona al menos un tipo de gráfico.")
            return

        # Obtener gráficos seleccionados
        self.selected_graphs = []
        if self.bar_chart_checkbox.isChecked():
            self.selected_graphs.append("bar_chart")
        if self.time_series_checkbox.isChecked():
            self.selected_graphs.append("time_series")

        # Validar selección de columnas
        x_column = self.x_column_dropdown.currentText()
        y_column = self.y_column_dropdown.currentText()
        if not x_column or not y_column:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona las columnas para los gráficos.")
            return

        # Guardar selección de columnas
        self.selected_columns = {"x_column": x_column, "y_column": y_column}

        QMessageBox.information(
            self, "Selecciones Guardadas",
            f"Gráficos seleccionados: {', '.join(self.selected_graphs)}\n"
            f"Columnas seleccionadas: X = {x_column}, Y = {y_column}"
        )

    def go_to_previous_page(self):
        self.parent().setCurrentIndex(2)

class FinalPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        # Componentes de la interfaz
        self.summary_label = QLabel("Resumen de Decisiones:")
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.generate_button = QPushButton("Generar Reporte")
        self.back_button = QPushButton("Regresar")

        # Configuración del layout
        self.layout.addWidget(self.summary_label)
        self.layout.addWidget(self.summary_text)
        self.layout.addWidget(self.generate_button)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

        # Eventos
        self.generate_button.clicked.connect(self.generate_report)
        self.back_button.clicked.connect(self.go_to_previous_page)

        # Variables
        self.decisions = []  # Decisiones tomadas en todas las páginas
        self.template_path = None  # Ruta de la plantilla seleccionada

    def load_decisions(self, template_path, decisions):
        """Carga las decisiones y la plantilla seleccionada para mostrarlas en la interfaz."""
        self.template_path = template_path
        self.decisions = decisions

        # Mostrar el resumen de las decisiones
        summary = f"Plantilla seleccionada:\n{self.template_path}\n\n"
        for db_decision in self.decisions:
            summary += f"Base de Datos: {db_decision['database']}\n"
            for sheet_decision in db_decision['decisions']:
                summary += f"  Hoja: {sheet_decision['sheet']}\n"
                summary += f"  Fila de encabezados: {sheet_decision['header_row'] + 1}\n"
                summary += f"  Gráficos:\n"
                for graph in sheet_decision['graphs']:
                    summary += f"    - {graph.capitalize()} (X: {sheet_decision['columns']['x_column']}, Y: {sheet_decision['columns']['y_column']})\n"
            summary += "\n"

        self.summary_text.setText(summary)

    def generate_report(self):
        """Genera el reporte basado en las decisiones tomadas."""
        try:
            response = requests.post(f"{BACKEND_URL}/generate-report", json={
                'template_path': self.template_path,
                'decisions': self.decisions
            })
            
            if response.status_code == 200:
                data = response.json()
                QMessageBox.information(
                    self, 
                    "Reporte Generado", 
                    f"El reporte se ha generado correctamente en: {data['output_path']}"
                )
            else:
                QMessageBox.warning(self, "Error", "No se pudo generar el reporte.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al generar el reporte: {e}")

    def go_to_previous_page(self):
        self.parent().setCurrentIndex(3)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selector de Plantillas y Bases de Datos")
        self.setGeometry(100, 100, 800, 600)

        # Configuración de páginas
        self.stack = QStackedWidget()
        self.first_page = FirstPage(self.stack)
        self.second_page = SecondPage(self.stack)
        self.third_page = ThirdPage(self.stack)
        self.fourth_page = FourthPage(self.stack)
        self.final_page = FinalPage(self.stack)

        self.stack.addWidget(self.first_page)
        self.stack.addWidget(self.second_page)
        self.stack.addWidget(self.third_page)
        self.stack.addWidget(self.fourth_page)
        self.stack.addWidget(self.final_page)

        self.setCentralWidget(self.stack)

        # Variables para almacenar selecciones
        self.selected_template = None
        self.selected_databases = []
        self.database_decisions = []

        # Conexión entre páginas
        self.second_page.next_button.clicked.connect(self.start_iteration)
        self.fourth_page.save_button.clicked.connect(self.save_graph_decisions)
        self.fourth_page.save_button.clicked.connect(self.go_to_final_page)

    def go_to_final_page(self):
        """Ir a la página final para revisar decisiones."""
        self.final_page.load_decisions(self.selected_template, self.database_decisions)
        self.stack.setCurrentIndex(4)

    def start_iteration(self):
        """Inicia la iteración de bases de datos seleccionadas."""
        if not self.selected_databases:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona al menos una base de datos.")
            return

        # Preparar para nueva iteración
        self.current_database_index = 0
        self.database_decisions = []
        
        # Cargar el primer archivo
        current_database = self.selected_databases[self.current_database_index]
        database_name = current_database.split(" (")[0]
        database_path = current_database[current_database.find("(")+1:current_database.find(")")]
        
        # Cargar el archivo en la tercera página
        self.third_page.load_file(database_path)
        
        # Avanzar a la tercera página
        self.stack.setCurrentIndex(2)

    def save_graph_decisions(self):
        """Guarda las decisiones de gráficos para la base de datos actual."""
        if not hasattr(self, 'database_decisions'):
            self.database_decisions = []

        current_database = self.selected_databases[self.current_database_index]
        database_path = current_database[current_database.find("(")+1:current_database.find(")")]
        
        # Crear o actualizar las decisiones para la base de datos actual
        current_decision = {
            'database': database_path,
            'decisions': [{
                'sheet': self.third_page.selected_sheet,
                'header_row': self.third_page.selected_header_row,
                'graphs': self.fourth_page.selected_graphs,
                'columns': self.fourth_page.selected_columns
            }]
        }
        
        self.database_decisions.append(current_decision)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())