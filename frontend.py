import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QWidget, QMessageBox, QHBoxLayout, 
    QComboBox, QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView, QCheckBox, 
    QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt
import pandas as pd
from openpyxl import load_workbook
import xlrd
import os

BACKEND_URL = "http://127.0.0.1:5000"

class FirstPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        
        # Botón para seleccionar la carpeta de plantillas
        self.select_folder_button = QPushButton("Seleccionar Carpeta de Plantillas")
        self.select_folder_button.clicked.connect(self.select_template_folder)
        
        self.list_widget = QListWidget()
        self.next_button = QPushButton("Siguiente")
        self.status_label = QLabel("Selecciona una carpeta de plantillas para comenzar.")
        
        # Añadir diccionario para almacenar las plantillas
        self.templates = {}  # Para almacenar {nombre: ruta}

        self.layout.addWidget(self.select_folder_button)
        self.layout.addWidget(QLabel("Selecciona una Plantilla:"))
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        self.next_button.clicked.connect(self.go_to_next_page)

    def select_template_folder(self):
        """Permite al usuario seleccionar la carpeta de plantillas."""
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Plantillas", os.path.expanduser("~"), QFileDialog.ShowDirsOnly)
        
        if folder_path:
            # Verificar si la carpeta contiene la subcarpeta "Plantilla para reportes"
            default_folder = os.path.join(folder_path, "Plantilla para reportes")
            if os.path.exists(default_folder):
                folder_path = default_folder
            
            # Enviar la ruta de la carpeta al backend
            response = requests.post(f"{BACKEND_URL}/set-template-folder", json={'folder_path': folder_path})
            
            if response.status_code == 200:
                self.status_label.setText(f"Carpeta seleccionada: {folder_path}")
                self.load_templates()
            else:
                self.status_label.setText("Error al seleccionar la carpeta de plantillas.")
                QMessageBox.warning(self, "Error", "No se pudo configurar la carpeta de plantillas.")

    def load_templates(self):
        """Carga las plantillas desde la carpeta seleccionada."""
        try:
            response = requests.get(f"{BACKEND_URL}/templates")
            if response.status_code == 200:
                templates = response.json()
                self.templates = {template["name"]: template["path"] for template in templates}
                self.list_widget.clear()
                for template_name in self.templates:
                    self.list_widget.addItem(template_name)
                self.status_label.setText("Plantillas cargadas correctamente.")
            else:
                self.status_label.setText("Error al cargar plantillas.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def go_to_next_page(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            template_name = selected_item.text()
            template_path = self.templates[template_name]
            
            # Obtener referencia a MainWindow y guardar la ruta completa
            main_window = self.parent().parent()
            main_window.selected_template = template_path
            
            print(f"Plantilla seleccionada: {template_path}")  # Para depuración
            self.parent().setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una plantilla.")
            
class SecondPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        
        # Botón para seleccionar la carpeta de bases de datos
        self.select_folder_button = QPushButton("Seleccionar Carpeta de Bases de Datos")
        self.select_folder_button.clicked.connect(self.select_database_folder)
        
        # Barra de búsqueda
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escriba para filtrar bases de datos...")
        self.search_input.textChanged.connect(self.filter_databases)
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        
        self.list_widget = QListWidget()
        self.back_button = QPushButton("Regresar")
        self.next_button = QPushButton("Seleccionar Bases de Datos")
        self.status_label = QLabel("Selecciona una carpeta de bases de datos para comenzar.")

        # Añadir widgets al layout principal
        self.layout.addWidget(self.select_folder_button)
        self.layout.addLayout(self.search_layout)
        self.layout.addWidget(QLabel("Selecciona las Bases de Datos:"))
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        # Botones
        self.back_button.clicked.connect(self.go_to_previous_page)
        self.next_button.clicked.connect(self.store_selected_databases)

        # Lista para almacenar todas las bases de datos
        self.all_databases = []
        # Diccionario para mantener el estado de las casillas
        self.checked_states = {}
        
        # Conectar el evento de cambio de estado de las casillas
        self.list_widget.itemChanged.connect(self.on_item_changed)

    def select_database_folder(self):
        """Permite al usuario seleccionar la carpeta de bases de datos."""
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Bases de Datos", os.path.expanduser("~"), QFileDialog.ShowDirsOnly)
        
        if folder_path:
            # Enviar la ruta de la carpeta al backend
            response = requests.post(f"{BACKEND_URL}/set-database-folder", json={'folder_path': folder_path})
            
            if response.status_code == 200:
                self.status_label.setText(f"Carpeta seleccionada: {folder_path}")
                self.load_databases()
            else:
                self.status_label.setText("Error al seleccionar la carpeta de bases de datos.")
                QMessageBox.warning(self, "Error", "No se pudo configurar la carpeta de bases de datos.")

    def load_databases(self):
        """Carga las bases de datos desde la carpeta seleccionada."""
        try:
            response = requests.get(f"{BACKEND_URL}/databases")
            if response.status_code == 200:
                databases = response.json()
                self.all_databases = databases
                self.list_widget.clear()
                self.checked_states = {}
                for db in databases:
                    full_text = f"{db['name']} ({db['path']})"
                    item = QListWidgetItem(full_text)
                    item.setCheckState(Qt.Unchecked)
                    self.checked_states[full_text] = Qt.Unchecked
                    self.list_widget.addItem(item)
                self.status_label.setText("Bases de datos cargadas correctamente.")
            else:
                self.status_label.setText("Error al cargar bases de datos.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def on_item_changed(self, item):
        """Actualiza el estado global de las casillas cuando cambia una selección."""
        self.checked_states[item.text()] = item.checkState()

    def filter_databases(self, text):
        """Filtra las bases de datos según el texto de búsqueda y mantiene las selecciones."""
        self.list_widget.clear()
        search_text = text.lower()
        
        for db in self.all_databases:
            full_text = f"{db['name']} ({db['path']})"
            if search_text in db['name'].lower():
                item = QListWidgetItem(full_text)
                # Usar el estado guardado o establecer como desmarcado si no existe
                item.setCheckState(self.checked_states.get(full_text, Qt.Unchecked))
                self.list_widget.addItem(item)

    def store_selected_databases(self):
        """Almacena todas las bases de datos seleccionadas usando el estado global."""
        selected_databases = []
        
        # Usar checked_states para obtener todas las selecciones
        for db in self.all_databases:
            full_text = f"{db['name']} ({db['path']})"
            if self.checked_states.get(full_text) == Qt.Checked:
                selected_databases.append(full_text)
                print(f"Base seleccionada: {full_text}")  # Depuración

        if selected_databases:
            # Obtener la referencia a MainWindow
            main_window = self.parent().parent()
            main_window.selected_databases = selected_databases
            QMessageBox.information(
                self, 
                "Bases Seleccionadas", 
                f"Bases seleccionadas:\n{', '.join(selected_databases)}"
            )
            # Llamar a start_iteration desde MainWindow
            main_window.start_iteration()
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
            # Asegurar que header_row tenga un valor por defecto
            header_row = getattr(self, 'selected_header_row', 0)
            if header_row is None:
                header_row = 0
                
            print(f"Enviando solicitud con:")
            print(f"- Archivo: {self.selected_file}")
            print(f"- Hoja: {self.selected_sheet}")
            print(f"- Header row: {header_row}")
            
            response = requests.post(f"{BACKEND_URL}/preview-sheet", json={
                'file_path': self.selected_file,
                'sheet_name': str(self.selected_sheet),
                'header_row': header_row  # Ahora siempre enviará un número
            })
            
            if response.status_code == 200:
                data = response.json()
                self.show_table_from_data(data['columns'], data['data'])
            else:
                error_msg = response.json().get('error', 'Error desconocido')
                QMessageBox.warning(self, "Error", f"No se pudo cargar la hoja. Error: {error_msg}")
                print(f"Error response: {response.text}")
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.warning(self, "Error", f"No se pudo cargar la hoja: {str(e)}")

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
        """Selecciona la fila de encabezados y navega a la siguiente página."""
        try:
            header_row = int(self.header_input.text()) - 1
            if header_row < 0:
                QMessageBox.warning(self, "Error", "La fila debe ser mayor a 0.")
                return

            self.selected_header_row = header_row
            
            # Leer los nombres de las columnas con el encabezado seleccionado
            df = pd.read_excel(
                self.selected_file,
                sheet_name=self.selected_sheet,
                header=header_row,
                nrows=1  # Solo leer la fila de encabezados
            )
            
            # Almacenar los nombres de las columnas (convertidos a string)
            self.column_names = [str(col) for col in df.columns.tolist()]
            
            # Configurar la cuarta página con los nombres de las columnas
            fourth_page = self.parent().widget(3)  # Obtener la cuarta página
            fourth_page.load_sheet(
                self.selected_file,
                self.selected_sheet,
                self.column_names
            )
            
            QMessageBox.information(
                self, "Fila Seleccionada", 
                f"Fila de encabezados seleccionada: {header_row + 1}\n"
                f"Columnas detectadas: {', '.join(self.column_names)}"
            )
            
            # Navegar a la cuarta página
            self.parent().setCurrentIndex(3)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingresa un número válido.")

    def go_to_previous_page(self):
        self.parent().setCurrentIndex(1)

    def show_table_from_data(self, columns, data):
        """Muestra los datos recibidos del backend en la tabla."""
        self.table_preview.setColumnCount(len(columns))
        self.table_preview.setRowCount(len(data))
        
        # Establecer encabezados
        self.table_preview.setHorizontalHeaderLabels(columns)
        
        # Llenar datos
        for row_idx, row_data in enumerate(data):
            for col_idx, column in enumerate(columns):
                item = QTableWidgetItem(str(row_data[column]))
                self.table_preview.setItem(row_idx, col_idx, item)
        
        # Ajustar el ancho de las columnas
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def clear_selections(self):
        """Limpia las selecciones anteriores."""
        self.selected_file = None
        self.selected_sheet = None
        self.selected_header_row = None
        self.sheet_selector.clear()
        self.header_input.clear()
        self.table_preview.setRowCount(0)
        self.table_preview.setColumnCount(0)

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

    def load_sheet(self, file_path, sheet_name, column_names):
        """Carga la información de la hoja y configura los dropdowns de columnas."""
        self.selected_file = file_path
        self.selected_sheet = sheet_name
        self.sheet_label.setText(f"Hoja seleccionada: {sheet_name}")
        
        try:
            # Leer los datos para mostrar en la tabla
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=self.parent().parent().third_page.selected_header_row
            )
            
            # Mostrar los datos en la tabla
            self.table_preview.setColumnCount(len(column_names))
            self.table_preview.setRowCount(len(df))
            
            # Establecer encabezados
            self.table_preview.setHorizontalHeaderLabels(column_names)
            
            # Llenar datos usando iloc para acceder por posición
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    item = QTableWidgetItem(str(df.iloc[i, j]))  # Usar iloc para acceder por posición
                    self.table_preview.setItem(i, j, item)
            
            # Ajustar el ancho de las columnas
            self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Actualizar los dropdowns con los nombres de las columnas
            self.x_column_dropdown.clear()
            self.y_column_dropdown.clear()
            self.x_column_dropdown.addItems(column_names)
            self.y_column_dropdown.addItems(column_names)
            
        except Exception as e:
            print(f"Error al cargar la hoja en la cuarta página: {str(e)}")
            import traceback
            print(traceback.format_exc())
            QMessageBox.warning(self, "Error", f"No se pudo cargar la vista previa: {str(e)}")

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

    def clear_selections(self):
        """Limpia las selecciones anteriores."""
        self.x_column_dropdown.clear()
        self.y_column_dropdown.clear()
        self.bar_chart_checkbox.setChecked(False)
        self.time_series_checkbox.setChecked(False)
        self.table_preview.setRowCount(0)
        self.table_preview.setColumnCount(0)
        self.selected_graphs = []
        self.selected_columns = {}

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
        self.output_label = QLabel("Directorio de salida:")
        
        # Directorio de salida por defecto
        self.output_directory = os.path.join(os.path.expanduser("~"), "Desktop", "Reporte Generado")

        # Configuración del layout
        self.layout.addWidget(self.summary_label)
        self.layout.addWidget(self.summary_text)
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.generate_button)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

        # Eventos
        self.generate_button.clicked.connect(self.generate_report)
        self.back_button.clicked.connect(self.go_to_previous_page)

        # Variables
        self.decisions = []
        self.template_path = None

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
        self.output_label.setText(f"Directorio de salida: {self.output_directory}")

    def generate_report(self):
        """Genera el reporte basado en las decisiones tomadas."""
        try:
            response = requests.post(f"{BACKEND_URL}/generate-report", json={
                'template_path': self.template_path,
                'decisions': self.decisions,
                'output_directory': self.output_directory
            })
            
            if response.status_code == 200:
                data = response.json()
                QMessageBox.information(
                    self, 
                    "Reporte Generado", 
                    f"El reporte se ha generado correctamente en:\n{data['output_path']}"
                )
            else:
                error_msg = response.json().get('error', 'Error desconocido')
                QMessageBox.warning(self, "Error", f"No se pudo generar el reporte: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al generar el reporte: {str(e)}")

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
        self.current_database_index = 0

        # Conexión entre páginas
        self.second_page.next_button.clicked.connect(self.start_iteration)
        self.fourth_page.save_button.clicked.connect(self.save_graph_decisions)

    def save_graph_decisions(self):
        """Guarda las decisiones de gráficos y maneja la iteración de bases de datos."""
        if not hasattr(self, 'database_decisions'):
            self.database_decisions = []

        # Verificar que se hayan hecho las selecciones necesarias
        if not self.fourth_page.selected_graphs or not self.fourth_page.selected_columns:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona los gráficos y columnas antes de continuar.")
            return

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
        
        # Verificar si hay más bases de datos para procesar
        self.current_database_index += 1
        if self.current_database_index < len(self.selected_databases):
            # Cargar la siguiente base de datos
            next_database = self.selected_databases[self.current_database_index]
            database_path = next_database[next_database.find("(")+1:next_database.find(")")]
            
            # Limpiar selecciones anteriores
            self.third_page.clear_selections()
            self.fourth_page.clear_selections()
            
            # Cargar la siguiente base de datos en la tercera página
            self.third_page.load_file(database_path)
            
            # Volver a la tercera página
            self.stack.setCurrentIndex(2)
            
            QMessageBox.information(
                self,
                "Siguiente Base de Datos",
                f"Por favor, procese la siguiente base de datos:\n{next_database.split(' (')[0]}"
            )
        else:
            # Si no hay más bases de datos, ir a la página final
            self.go_to_final_page()

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

    def go_to_final_page(self):
        """Ir a la página final para revisar decisiones."""
        self.final_page.load_decisions(self.selected_template, self.database_decisions)
        self.stack.setCurrentIndex(4)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())