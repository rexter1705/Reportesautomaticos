import os
from openpyxl import load_workbook
import xlrd
import pandas as pd
from datetime import datetime
import subprocess
import matplotlib.pyplot as plt
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Configuración de rutas
latex_template_path = r"C:\Users\fglruiz\Desktop\Investigacion_e_informes\Reportes\Plantilla para reportes\Plantilla\main2.tex"
output_directory = r"C:\Users\fglruiz\Desktop\Investigacion_e_informes\Reportes\Automatizados\Pruebas"

# Función para asegurar que un directorio exista
def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)

# Obtener nombres de hojas en un archivo Excel
def obtener_nombres_hojas(ruta_archivo):
    """
    Detecta los nombres de las hojas en un archivo Excel (xls o xlsx).
    Permite al usuario seleccionar las hojas con las que desea trabajar.

    :param ruta_archivo: Ruta al archivo Excel.
    :return: Lista de hojas seleccionadas por el usuario.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo '{ruta_archivo}' no existe.")

    # Detectar extensión del archivo
    extension = os.path.splitext(ruta_archivo)[1].lower()

    if extension == ".xlsx":
        workbook = load_workbook(filename=ruta_archivo, read_only=True)
        hojas = workbook.sheetnames
    elif extension == ".xls":
        workbook = xlrd.open_workbook(ruta_archivo)
        hojas = workbook.sheet_names()
    else:
        raise ValueError("Formato de archivo no soportado. Use un archivo .xls o .xlsx.")

    # Mostrar opciones al usuario
    if len(hojas) == 1:
        print(f"El archivo contiene solo una hoja: '{hojas[0]}'. Esta será seleccionada automáticamente.")
        return hojas
    else:
        print("Las hojas disponibles son:")
        for idx, hoja in enumerate(hojas, start=1):
            print(f"{idx}. {hoja}")

        seleccion = input("Ingrese los números de las hojas que desea seleccionar, separados por comas: ")
        indices_seleccionados = [int(x.strip()) for x in seleccion.split(",") if x.strip().isdigit()]

        hojas_seleccionadas = [hojas[i - 1] for i in indices_seleccionados if 1 <= i <= len(hojas)]

        if not hojas_seleccionadas:
            print("No se seleccionó ninguna hoja válida. Inténtelo de nuevo.")
            return obtener_nombres_hojas(ruta_archivo)

        return hojas_seleccionadas

# Seleccionar columnas de un DataFrame
def seleccionar_columnas(ruta_archivo, hoja, fila_titulos=None):
    """
    Lee las columnas de un archivo de Excel y permite al usuario seleccionar las columnas con las que desea trabajar.

    :param ruta_archivo: Ruta al archivo de Excel.
    :param hoja: Nombre o índice de la hoja a leer.
    :param fila_titulos: Número de fila (base 0) donde están los títulos de las columnas.
    :return: DataFrame con las columnas seleccionadas por el usuario.
    """
    try:
        # Solicitar al usuario la fila de encabezados si no se proporciona
        if fila_titulos is None:
            fila_titulos = int(input("Por favor, ingresa el número de fila que contiene los encabezados (base 1): ")) - 1

        # Leer el archivo con la fila de encabezados especificada
        df = pd.read_excel(ruta_archivo, sheet_name=hoja, header=fila_titulos)

        # Convertir los encabezados a cadenas para evitar problemas con números
        df.columns = df.columns.map(str)

        # Mostrar los nombres de las columnas
        print("Columnas disponibles:")
        for idx, col in enumerate(df.columns):
            print(f"[{idx}] {col}")

        # Solicitar al usuario que elija las columnas
        seleccion = input("Ingresa los números de las columnas que deseas trabajar (separados por comas): ")
        indices_seleccionados = [int(x) for x in seleccion.split(",") if x.isdigit()]

        # Filtrar las columnas seleccionadas
        columnas_seleccionadas = df.iloc[:, indices_seleccionados]

        print("\nHas seleccionado las siguientes columnas:")
        print(columnas_seleccionadas.head())

        return columnas_seleccionadas

    except FileNotFoundError:
        print("Error: No se encontró el archivo especificado.")
    except ValueError as e:
        print(f"Error de formato: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

def generate_time_series_pgf(df, x_column, y_column, output_filename):
    try:
        # Asegurarse de que no haya valores nulos en las columnas
        df = df.dropna(subset=[x_column, y_column]).copy()  # Crear una copia explícita del DataFrame

        # Convertir la columna del eje X a cadenas
        df.loc[:, x_column] = df[x_column].astype(str)  # Usar .loc para modificar el DataFrame
        
        # Convertir la columna del eje Y a números
        df.loc[:, y_column] = pd.to_numeric(df[y_column], errors='coerce')

        # Filtrar valores no convertibles en el eje Y
        df = df.dropna(subset=[y_column])

        # Configurar Matplotlib para exportar en formato PGF
        plt.rcParams.update({
            "pgf.texsystem": "pdflatex",  # Usar LaTeX para graficar
            "font.family": "serif",
            "text.usetex": True,
            "pgf.rcfonts": False,
        })

        plt.figure(figsize=(6, 4))
        plt.plot(df[x_column], df[y_column], label=y_column, color='blue')
        plt.title(f'Time Series of {y_column}')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.grid(True)
        plt.xticks(rotation=45)

        plt.savefig(output_filename, format="pgf")
        plt.close()
        print(f"PGF plot saved to '{output_filename}'")
    except Exception as e:
        print(f"Error generating time series PGF: {e}")

def generate_bar_chart_pgf(df, x_column, y_column, output_filename):
    """
    Genera un gráfico de barras en formato PGF.

    :param df: DataFrame con los datos.
    :param x_column: Columna para el eje X.
    :param y_column: Columna para el eje Y.
    :param output_filename: Ruta donde se guardará el gráfico PGF.
    """
    try:
        # Limpiar valores nulos
        df = df.dropna(subset=[x_column, y_column])
        
        # Configurar Matplotlib para PGF
        plt.rcParams.update({
            "pgf.texsystem": "pdflatex",
            "font.family": "serif",
            "text.usetex": True,
            "pgf.rcfonts": False,
        })

        plt.figure(figsize=(6, 4))
        plt.bar(df[x_column], df[y_column], color='green')
        plt.title(f'Bar Chart of {y_column}')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.xticks(rotation=45)

        plt.savefig(output_filename, format="pgf")
        plt.close()
        print(f"Bar chart PGF saved to '{output_filename}'")
    except Exception as e:
        print(f"Error generating bar chart PGF: {e}")

# Descargar bases de datos desde una página
def obtener_link_interactivo(base_url):
    try:
        # Configurar la carpeta en el escritorio
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        database_folder = os.path.join(desktop_path, "Bases de Datos")
        os.makedirs(database_folder, exist_ok=True)

        archivos_encontrados = []
        links_pendientes = [base_url]
        visitados = set()

        while links_pendientes:
            current_url = links_pendientes.pop(0)
            if current_url in visitados:
                continue

            visitados.add(current_url)
            print(f"\nAccediendo a: {current_url}")

            try:
                response = requests.get(current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extraer título del contenedor <h1 class="page-title">
                titulo = soup.find('h1', class_='page-title')
                titulo_texto = titulo.text.strip() if titulo else "Archivo sin título"

                # Buscar enlaces dentro de la página actual
                contenedor = soup.find('div', {'id': 'block-solucionweb-content', 'class': 'contenido block block-system block-system-main-block'})
                if not contenedor:
                    print("No se encontró el contenedor especificado en esta página.")
                    continue

                for link in contenedor.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(current_url, href)

                    if absolute_url.lower().endswith(('.xls', '.xlsx')):
                        archivos_encontrados.append((titulo_texto, absolute_url))
                    elif absolute_url not in visitados:
                        links_pendientes.append(absolute_url)

            except Exception as e:
                print(f"Error al procesar {current_url}: {e}")

        if not archivos_encontrados:
            print("No se encontraron archivos Excel en los enlaces explorados.")
            return []

        # Mostrar menú con los archivos encontrados
        print("\nArchivos Excel disponibles:")
        for idx, (titulo, url) in enumerate(archivos_encontrados, start=1):
            print(f"[{idx}] {titulo} -> {url}")

        # Seleccionar archivos para descargar
        seleccionados = []
        while True:
            user_input = input("\nSeleccione archivos para descargar (números separados por comas, o 'q' para salir): ").strip()
            if user_input.lower() == 'q':
                break

            try:
                indices = [int(x.strip()) for x in user_input.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(archivos_encontrados):
                        titulo, url = archivos_encontrados[idx - 1]
                        file_name = os.path.basename(url)
                        file_path = os.path.join(database_folder, file_name)

                        print(f"\nDescargando: {file_name}")
                        try:
                            file_response = requests.get(url)
                            file_response.raise_for_status()
                            with open(file_path, 'wb') as file:
                                file.write(file_response.content)
                            print(f"Archivo guardado en: {file_path}")
                            seleccionados.append(file_path)
                        except Exception as e:
                            print(f"Error al descargar {file_name}: {e}")

            except ValueError:
                print("Entrada inválida. Por favor, ingrese números separados por comas.")

        return seleccionados

    except Exception as e:
        print(f"Error: {e}")
        return []

def identificar_maximos_minimos(df, y_column, x_column):
    """
    Identifica el valor máximo y mínimo en una columna específica de un DataFrame y las posiciones correspondientes en otra columna.
    
    :param df: DataFrame con los datos.
    :param y_column: Nombre de la columna para analizar los valores.
    :param x_column: Nombre de la columna para identificar las posiciones de los valores.
    :return: Diccionario con el máximo, mínimo, y las posiciones correspondientes.
    """
    max_value = df[y_column].max()
    min_value = df[y_column].min()
    
    # Encontrar los valores de x correspondientes
    max_x = df[df[y_column] == max_value][x_column].iloc[0]
    min_x = df[df[y_column] == min_value][x_column].iloc[0]
    
    return {'max': max_value, 'min': min_value, 'max_x': max_x, 'min_x': min_x}

def agregar_max_min_latex(latex_path, database_name, sheet_name, max_value, min_value, max_x, min_x):
    """
    Inserta los valores máximos y mínimos junto con sus posiciones en un archivo LaTeX.

    :param latex_path: Ruta al archivo LaTeX.
    :param database_name: Nombre de la base de datos procesada.
    :param sheet_name: Nombre de la hoja procesada.
    :param max_value: Valor máximo.
    :param min_value: Valor mínimo.
    :param max_x: Valor de x correspondiente al máximo.
    :param min_x: Valor de x correspondiente al mínimo.
    """
    try:
        with open(latex_path, 'r') as file:
            latex_content = file.read()

        # Crear la sección para la base de datos y la hoja
        max_min_text = f"""
        \section*{{Análisis de valores: {database_name} - Hoja: {sheet_name}}}
        El valor máximo observado es: \textbf{{{max_value}}} en \textbf{{{max_x}}}.\\
        El valor mínimo observado es: \textbf{{{min_value}}} en \textbf{{{min_x}}}.
        """

        # Reemplazar el marcador correspondiente o añadir al final del archivo
        if "PLACEHOLDER_MAX_MIN" in latex_content:
            latex_content = latex_content.replace("PLACEHOLDER_MAX_MIN", max_min_text + "\nPLACEHOLDER_MAX_MIN")
        else:
            latex_content += max_min_text

        with open(latex_path, 'w') as file:
            file.write(latex_content)
    except Exception as e:
        print(f"Error actualizando LaTeX con máximos y mínimos: {e}")

def update_latex_file(latex_template_path, chart_paths, output_directory, database_sections):
    """
    Actualiza el archivo LaTeX organizando el contenido por base de datos.

    :param latex_template_path: Ruta al archivo LaTeX original.
    :param chart_paths: Lista de tuplas (database_name, sheet_name, chart_path).
    :param output_directory: Directorio de salida.
    :param database_sections: Diccionario con la información de cada base de datos.
    :return: Ruta al archivo LaTeX actualizado.
    """
    try:
        with open(latex_template_path, 'r') as file:
            latex_content = file.read()

        # Generar contenido organizado por base de datos
        content_by_database = ""
        
        for database_name, sections in database_sections.items():
            # Título de la base de datos
            content_by_database += f"""
            \\section*{{Analisis de {database_name}}}
            """
            
            # Agregar información de máximos y mínimos por hoja
            for section_info in sections:
                content_by_database += f"""
                \\subsection*{{Hoja: {section_info['sheet_name']}}}
                El valor maximo observado es: \\textbf{{{section_info['max_value']}}} en \\textbf{{{section_info['max_x']}}}.\\\\
                El valor minimo observado es: \\textbf{{{section_info['min_value']}}} en \\textbf{{{section_info['min_x']}}}.

                \\begin{{center}}
                """
                
                # Agregar gráficas correspondientes
                for chart_path in section_info['charts']:
                    content_by_database += f"""
                    \\input{{{chart_path.replace('\\', '/')}}}
                    \\vspace{{10pt}}
                    """
                
                content_by_database += "\\end{center}\n"

        # Reemplazar el marcador de contenido
        if "CHAR_PATH_1" in latex_content:
            latex_content = latex_content.replace("CHAR_PATH_1", content_by_database)
        else:
            latex_content += content_by_database

        # Guardar el archivo LaTeX actualizado
        updated_latex_path = os.path.join(output_directory, "Updated_Prueba.tex")
        with open(updated_latex_path, 'w') as file:
            file.write(latex_content)

        return updated_latex_path
    except Exception as e:
        print(f"Error updating LaTeX file: {e}")
        return None

def compile_latex(updated_latex_path, output_directory):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_pdf_name = f"Prueba_{current_time}.pdf"
        output_directory = output_directory.replace('\\', '/')
        os.chdir(output_directory)
        subprocess.run(["pdflatex", "-shell-escape", "--interaction=nonstopmode", updated_latex_path.replace('\\', '/'), "-jobname", output_pdf_name.split('.')[0]], check=True)
        print(f"PDF successfully created at: {os.path.join(output_directory, output_pdf_name)}")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling LaTeX: {e}")
    except Exception as e:
        print(f"Error compiling LaTeX: {e}")

# Función principal
def main():
    ensure_directory(output_directory)

    # Descargar bases de datos
    base_url = "https://banguat.gob.gt/page/estadisticas-macroeconomicas"
    downloaded_files = obtener_link_interactivo(base_url)
    if not downloaded_files:
        print("No se pudieron descargar las bases de datos.")
        return

    all_sections = []
    all_chart_paths = []
    
    # Modificar la estructura de datos para organizar por base de datos
    database_sections = {}
    
    # Procesar cada archivo descargado
    for downloaded_file in downloaded_files:
        database_name = os.path.basename(downloaded_file).replace('.xlsx', '')
        database_sections[database_name] = []
        print(f"\nProcesando archivo: {database_name}")
        
        # Obtener nombres de hojas dinámicamente
        hojas_seleccionadas = obtener_nombres_hojas(downloaded_file)
        if not hojas_seleccionadas:
            print("No se seleccionaron hojas para analizar.")
            continue

        for sheet_name in hojas_seleccionadas:
            # Seleccionar columnas desde la hoja
            columnas_df = seleccionar_columnas(downloaded_file, sheet_name)
            if columnas_df is None or columnas_df.empty:
                print(f"No se seleccionaron columnas de la hoja '{sheet_name}'.")
                continue

            # Solicitar al usuario las columnas para los ejes
            x_column = input("Selecciona el nombre de la columna para el eje X: ").strip()
            y_column = input("Selecciona el nombre de la columna para el eje Y: ").strip()

            if x_column not in columnas_df.columns or y_column not in columnas_df.columns:
                print("Una de las columnas seleccionadas no existe. Verifica los nombres.")
                continue

            # Preguntar al usuario qué gráfico desea incluir
            print("\nSeleccione los gráficos a generar:")
            print("1. Serie de tiempo\n2. Gráfico de barras\n3. Ambos")
            opcion = input("Ingrese el número de su elección: ").strip()

            # Detectar máximos y mínimos
            valores_extremos = identificar_maximos_minimos(columnas_df, y_column, x_column)

            # Crear información de la sección
            section_info = {
                'sheet_name': sheet_name,
                'max_value': valores_extremos['max'],
                'min_value': valores_extremos['min'],
                'max_x': valores_extremos['max_x'],
                'min_x': valores_extremos['min_x'],
                'charts': []
            }
            
            # Agregar rutas de gráficos según la opción seleccionada
            if opcion in ["1", "3"]:
                time_series_output_path = os.path.join(output_directory, f"time_series_plot_{sheet_name}.pgf")
                generate_time_series_pgf(columnas_df, x_column, y_column, time_series_output_path)
                section_info['charts'].append(time_series_output_path)
                
            if opcion in ["2", "3"]:
                bar_chart_output_path = os.path.join(output_directory, f"bar_chart_plot_{sheet_name}.pgf")
                generate_bar_chart_pgf(columnas_df, x_column, y_column, bar_chart_output_path)
                section_info['charts'].append(bar_chart_output_path)
            
            database_sections[database_name].append(section_info)

    # Actualizar el archivo LaTeX con la nueva estructura
    updated_latex_path = update_latex_file(
        latex_template_path,
        all_chart_paths,
        output_directory,
        database_sections
    )

    if updated_latex_path:
        compile_latex(updated_latex_path, output_directory)
    else:
        print("Error al actualizar el archivo LaTeX.")

if __name__ == "__main__":
    main()
