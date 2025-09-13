import os
from openpyxl import load_workbook
import xlrd
import pandas as pd
from datetime import datetime
import subprocess
import matplotlib.pyplot as plt
from urllib.parse import urljoin
import requests
import zipfile
from bs4 import BeautifulSoup
from difflib import get_close_matches

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

def adjust_figure_size(x_labels, base_width=6, base_height=4, scale_factor=0.2):
    """
    Ajusta el tamaño de la figura basado en la cantidad de etiquetas en el eje X.
    
    :param x_labels: Lista de etiquetas en el eje X.
    :param base_width: Ancho base de la figura.
    :param base_height: Altura base de la figura.
    :param scale_factor: Factor de escalamiento para aumentar el ancho si hay muchas etiquetas.
    :return: Tupla con el nuevo tamaño de la figura.
    """
    max_label_length = max(map(len, x_labels)) if x_labels else 1
    width = base_width + scale_factor * len(x_labels)
    height = base_height + (0.1 * max_label_length)  # Ajuste basado en longitud de etiquetas
    return (width, height)

def generate_time_series_tikz(df, x_column, y_column, output_filename):
    try:
        df = df.dropna(subset=[x_column, y_column]).copy()
        df.loc[:, x_column] = df[x_column].astype(str)
        df.loc[:, y_column] = pd.to_numeric(df[y_column], errors='coerce')
        df = df.dropna(subset=[y_column])

        with open(output_filename, "w") as f:
            f.write("\\begin{tikzpicture}\n")
            f.write("  \\begin{axis}[xlabel={%s}, ylabel={%s}, grid=major]\n" % (x_column, y_column))
            f.write("    \\addplot[color=blue, mark=*] coordinates {\n")
            
            for x, y in zip(df[x_column], df[y_column]):
                f.write(f"      ({x}, {y})\n")
            
            f.write("    };\n")
            f.write("  \\end{axis}\n")
            f.write("\\end{tikzpicture}\n")
        
        print(f"TikZ plot saved to '{output_filename}'")
    except Exception as e:
        print(f"Error generating time series TikZ: {e}")


def generate_bar_chart_tikz(df, x_column, y_column, output_filename):
    try:
        df = df.dropna(subset=[x_column, y_column]).copy()
        df.loc[:, x_column] = df[x_column].astype(str)
        df.loc[:, y_column] = pd.to_numeric(df[y_column], errors='coerce')
        df = df.dropna(subset=[y_column])

        with open(output_filename, "w") as f:
            f.write("\\begin{tikzpicture}\n")
            f.write("  \\begin{axis}[ybar, symbolic x coords={%s}, xtick=data, xlabel={%s}, ylabel={%s}, grid=major]\n" % (', '.join(df[x_column]), x_column, y_column))
            f.write("    \\addplot coordinates {\n")
            
            for x, y in zip(df[x_column], df[y_column]):
                f.write(f"      ({x}, {y})\n")
            
            f.write("    };\n")
            f.write("  \\end{axis}\n")
            f.write("\\end{tikzpicture}\n")
        
        print(f"TikZ bar chart saved to '{output_filename}'")
    except Exception as e:
        print(f"Error generating bar chart TikZ: {e}")
# Descargar bases de datos desde una página
def obtener_link_interactivo():
    """
    Permite al usuario seleccionar uno o más archivos Excel de la carpeta 'Bases de datos para Reportes'
    utilizando el nombre del archivo con autocompletación.
    
    :return: Lista con las rutas completas de los archivos seleccionados
    """
    try:
        # Construir la ruta a la carpeta en el escritorio
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        base_path = os.path.join(desktop_path, 'Bases de datos para Reportes')
        
        # Verificar si la carpeta existe
        if not os.path.exists(base_path):
            print("Error: No se encontró la carpeta 'Bases de datos para Reportes' en el escritorio.")
            return []
            
        archivos_encontrados = {}
        
        # Buscar todos los archivos Excel en la carpeta y subcarpetas
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.lower().endswith(('.xls', '.xlsx')):
                    ruta_completa = os.path.join(root, file)
                    # Generar un identificador único para evitar conflictos
                    clave = f"{os.path.basename(root)}/{file}"
                    archivos_encontrados[clave] = ruta_completa

        if not archivos_encontrados:
            print("No se encontraron archivos Excel en la carpeta.")
            return []

        # Extraer los nombres de los archivos
        nombres_archivos = list(archivos_encontrados.keys())
        
        # Seleccionar archivos
        archivos_seleccionados = []
        while True:
            entrada_usuario = input("\nIngrese el nombre del archivo (o parte del nombre) o 'q' para terminar: ").strip()
            
            if entrada_usuario.lower() == 'q':
                break

            # Autocompletación: buscar coincidencias cercanas
            coincidencias = get_close_matches(entrada_usuario, nombres_archivos, n=5, cutoff=0.2)
            if not coincidencias:
                print(f"No se encontraron coincidencias para: {entrada_usuario}")
                continue
            
            print("\nCoincidencias encontradas:")
            for idx, opcion in enumerate(coincidencias, start=1):
                print(f"[{idx}] {opcion}")
            
            while True:  # Bucle adicional para manejar la selección
                seleccion = input("Seleccione el número correspondiente o 'c' para cancelar: ").strip()
                if seleccion.lower() == 'c':
                    break  # Solo sale del bucle interno, permitiendo una nueva búsqueda
                
                try:
                    idx = int(seleccion) - 1
                    if 0 <= idx < len(coincidencias):
                        clave = coincidencias[idx]
                        archivo = archivos_encontrados[clave]
                        if archivo not in archivos_seleccionados:
                            archivos_seleccionados.append(archivo)
                            print(f"Archivo seleccionado: {clave}")
                        break  # Sale del bucle interno después de una selección exitosa
                    else:
                        print("Selección fuera de rango")
                except ValueError:
                    print("Por favor, ingrese un número válido")

        return archivos_seleccionados

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
        \section*{{Analisis de valores: {database_name} - Hoja: {sheet_name}}}
        El valor maximo observado es: \textbf{{{max_value}}} en \textbf{{{max_x}}}.\\
        El valor minimo observado es: \textbf{{{min_value}}} en \textbf{{{min_x}}}.
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
    Actualiza el archivo LaTeX organizando el contenido por base de datos en dos columnas.

    :param latex_template_path: Ruta al archivo LaTeX original.
    :param chart_paths: Lista de tuplas (database_name, sheet_name, chart_path).
    :param output_directory: Directorio de salida.
    :param database_sections: Diccionario con la información de cada base de datos.
    :return: Ruta al archivo LaTeX actualizado.
    """
    try:
        with open(latex_template_path, 'r') as file:
            latex_content = file.read()

        # Asegurarse de que los paquetes necesarios estén incluidos
        packages_to_include = [
            "\\usepackage{multicol}",
            "\\usepackage{adjustbox}"
        ]
        for package in packages_to_include:
            if package not in latex_content:
                latex_content = latex_content.replace("\\documentclass", f"{package}\n\\documentclass")

        # Generar contenido organizado por base de datos
        content_by_database = ""
        
        for database_name, sections in database_sections.items():
            content_by_database += f"\n\\section*{{Analisis de {database_name}}}\n"
            
            for section_info in sections:
                content_by_database += f"""
                \\subsection*{{Hoja: {section_info['sheet_name']}}}
                \\begin{{multicols}}{{2}}
                \\noindent{{\\textbf{{Analisis:}}\\\\
                El valor maximo observado es: \\textbf{{{section_info['max_value']}}} en \\textbf{{{section_info['max_x']}}}.\\\\
                El valor minimo observado es: \\textbf{{{section_info['min_value']}}} en \\textbf{{{section_info['min_x']}}}.}}

                \\columnbreak

                \\begin{{center}}
                """
                
                for chart_path in section_info['charts']:
                    content_by_database += f"""
                    \\begin{{center}}
                    \\resizebox{{\\columnwidth}}{{!}}{{%
                        \\input{{{chart_path.replace('\\', '/')}}}
                    }}
                    \\end{{center}}
                    \\vspace{{5pt}}
                    """
                
                content_by_database += """
                \\end{center}
                \\end{multicols}
                \\vspace{10pt}
                """

        # Reemplazar el marcador de contenido
        if "char" in latex_content:
            latex_content = latex_content.replace("char", content_by_database)
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

def compile_latex(updated_latex_path, chart_paths, output_directory):
    try:
        # Leer el contenido del archivo LaTeX actualizado
        with open(updated_latex_path, 'r') as file:
            latex_content = file.read()
        
        # Generar el nombre del nuevo archivo .tex con timestamp
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_tex_name = f"Prueba_{current_time}.tex"
        output_directory = output_directory.replace('\\', '/')
        os.chdir(output_directory)
        output_tex_path = os.path.join(output_directory, output_tex_name)
        
        # Guardar el contenido en un nuevo archivo .tex
        with open(output_tex_path, 'w') as file:
            file.write(latex_content)
        
        print(f"LaTeX file successfully saved at: {output_tex_path}")
        
        # Crear el archivo ZIP con el .tex y los gráficos
        zip_filename = os.path.join(output_directory, "output_files.zip")
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            files_to_zip = [output_tex_path] + chart_paths
            for file in files_to_zip:
                if os.path.exists(file):
                    zipf.write(file, os.path.basename(file))
        print(f"ZIP file successfully created at: {zip_filename}")
        
        return zip_filename  # Devuelve la ruta del archivo ZIP
        
    except Exception as e:
        print(f"Error processing files: {e}")
        return None

# Función principal
def main():
    ensure_directory(output_directory)

    # Obtener archivos Excel seleccionados
    downloaded_files = obtener_link_interactivo()
    if not downloaded_files:
        print("No se seleccionaron archivos para procesar.")
        return

    all_sections = []
    all_chart_paths = []
    
    # Modificar la estructura de datos para organizar por base de datos
    database_sections = {}
    
    # Procesar cada archivo seleccionado
    for downloaded_file in downloaded_files:
        database_name = os.path.basename(downloaded_file).replace('.xlsx', '').replace('.xls', '')
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
                generate_time_series_tikz(columnas_df, x_column, y_column, time_series_output_path)
                section_info['charts'].append(time_series_output_path)
                
            if opcion in ["2", "3"]:
                bar_chart_output_path = os.path.join(output_directory, f"bar_chart_plot_{sheet_name}.pgf")
                generate_bar_chart_tikz(columnas_df, x_column, y_column, bar_chart_output_path)
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