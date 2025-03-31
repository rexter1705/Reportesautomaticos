from flask import Flask, jsonify, request
import pandas as pd
import os
import matplotlib.pyplot as plt
import zipfile
from difflib import get_close_matches
from datetime import datetime
import matplotlib as mpl
mpl.use("pgf")

app = Flask(__name__)
output_directory = os.path.join(os.path.expanduser("~"), "Desktop", "Reporte Generado")

def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)

# Función para generar gráficos de series de tiempo
def generate_time_series_tikz(df, x_column, y_column, output_filename):
    try:
        # Clean the data
        df = df.dropna(subset=[x_column, y_column]).copy()
        df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
        df = df.dropna(subset=[y_column])
        df[x_column] = df[x_column].astype(str)

        # Try to convert the X column to datetime and sort if possible
        try:
            df[x_column] = pd.to_datetime(df[x_column])
            df = df.sort_values(by=x_column)
            df[x_column] = df[x_column].dt.strftime('%Y-%m-%d')
        except Exception:
            pass  # If conversion fails, leave the column as is

        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(df[x_column], df[y_column], marker='o', color='blue')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f'Serie de tiempo')
        plt.grid(True)
        plt.xticks(rotation=90)

        # Save the plot as a TikZ file
        plt.savefig(output_filename)
        plt.close()

        print(f"Time series TikZ plot saved to: {output_filename}")

    except Exception as e:
        print(f"Error generating time series TikZ plot: {e}")

# Función para generar gráficos de barras
def generate_bar_chart_tikz(df, x_column, y_column, output_filename):
    try:
        # Clean the data
        df = df.dropna(subset=[x_column, y_column]).copy()
        df[x_column] = df[x_column].astype(str)
        df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
        df = df.dropna(subset=[y_column])

        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.bar(df[x_column], df[y_column], color='blue')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f'Gráfico de barras')
        plt.grid(True)
        plt.xticks(rotation=90)

        # Save the plot as a TikZ file
        plt.savefig(output_filename)
        plt.close()

        print(f"Bar chart TikZ plot saved to: {output_filename}")

    except Exception as e:
        print(f"Error generating bar chart TikZ plot: {e}")

# Función para identificar máximos y mínimos
def identificar_maximos_minimos(df, y_column, x_column):
    max_value = df[y_column].max()
    min_value = df[y_column].min()
    
    # Encontrar los valores de x correspondientes
    max_x = df[df[y_column] == max_value][x_column].iloc[0]
    min_x = df[df[y_column] == min_value][x_column].iloc[0]
    
    return {'max': max_value, 'min': min_value, 'max_x': max_x, 'min_x': min_x}

# Función para actualizar el archivo LaTeX
def update_latex_file(latex_template_path, chart_paths, output_directory, database_sections):
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
                    # Extraer solo el nombre del archivo
                    chart_filename = os.path.basename(chart_path)
                    content_by_database += f"""
                    \\begin{{center}}
                    \\resizebox{{\\columnwidth}}{{!}}{{%%%
                        \\input{{{chart_filename}}}
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

# Función para compilar el archivo LaTeX
def compile_latex(updated_latex_path, chart_paths, output_directory):
    try:
        # Leer el contenido del archivo LaTeX actualizado
        with open(updated_latex_path, 'r') as file:
            latex_content = file.read()
        
        # Generar el nombre del nuevo archivo .tex con timestamp
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_tex_name = f"main.tex"
        output_directory = output_directory.replace('\\', '/')
        os.chdir(output_directory)
        output_tex_path = os.path.join(output_directory, output_tex_name)
        
        # Guardar el contenido en un nuevo archivo .tex
        with open(output_tex_path, 'w') as file:
            file.write(latex_content)
        
        print(f"LaTeX file successfully saved at: {output_tex_path}")
        
        # Crear el archivo ZIP con el .tex y los gráficos
        zip_filename = os.path.join(output_directory, f"output_files_{current_time}.zip")
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

# Variable global para almacenar la ruta de la carpeta de plantillas
carpeta_plantillas = None

@app.route('/set-template-folder', methods=['POST'])
def set_template_folder():
    global carpeta_plantillas
    data = request.json
    carpeta_plantillas = data.get('folder_path')
    if not carpeta_plantillas or not os.path.exists(carpeta_plantillas):
        return jsonify({'error': "La carpeta especificada no existe."}), 404
    return jsonify({'success': True, 'message': f"Carpeta de plantillas configurada: {carpeta_plantillas}"})

@app.route('/templates', methods=['GET'])
def get_templates():
    global carpeta_plantillas
    if not carpeta_plantillas:
        return jsonify({'error': "No se ha seleccionado una carpeta de plantillas."}), 404

    try:
        templates = []
        for file in os.listdir(carpeta_plantillas):
            if file.endswith('.tex'):
                template_path = os.path.join(carpeta_plantillas, file)
                templates.append({
                    'name': file,
                    'path': template_path
                })
        
        if not templates:
            return jsonify({'error': "No se encontraron archivos .tex en el directorio"}), 404
        
        return jsonify(templates)
    except Exception as e:
        return jsonify({'error': f"Error al buscar plantillas: {str(e)}"}), 500

    
# Variable global para almacenar la ruta de la carpeta de bases de datos
carpeta_bases_datos = None

@app.route('/set-database-folder', methods=['POST'])
def set_database_folder():
    global carpeta_bases_datos
    data = request.json
    carpeta_bases_datos = data.get('folder_path')
    if not carpeta_bases_datos or not os.path.exists(carpeta_bases_datos):
        return jsonify({'error': "La carpeta especificada no existe."}), 404
    return jsonify({'success': True, 'message': f"Carpeta de bases de datos configurada: {carpeta_bases_datos}"})

@app.route('/databases', methods=['GET'])
def get_databases():
    global carpeta_bases_datos
    if not carpeta_bases_datos:
        return jsonify({'error': "No se ha seleccionado una carpeta de bases de datos."}), 404

    try:
        databases = []
        for root, _, files in os.walk(carpeta_bases_datos):
            for file in files:
                if file.lower().endswith(('.xls', '.xlsx')):
                    databases.append({'name': file, 'path': os.path.join(root, file)})

        if not databases:
            return jsonify({'error': "No se encontraron archivos Excel en la carpeta."}), 404

        return jsonify(databases)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview-sheet', methods=['POST'])
def preview_sheet():
    try:
        data = request.json
        file_path = data['file_path']
        sheet_name = data['sheet_name']
        header_row = data.get('header_row', 0) if data.get('header_row') is not None else 0
        
        print(f"Intentando cargar archivo: {file_path}")
        print(f"Hoja seleccionada: {sheet_name}")
        print(f"Fila de encabezado: {header_row}")
        
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            print(f"El archivo no existe: {file_path}")
            return jsonify({'error': f"El archivo no existe: {file_path}"}), 404
        
        # Determinar el motor basado en la extensión del archivo
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            # Usar openpyxl para .xlsx y .xlsm, xlrd para .xls
            if file_extension in ['.xlsx', '.xlsm']:
                df = pd.read_excel(
                    file_path, 
                    sheet_name=str(sheet_name),
                    header=int(header_row),
                    nrows=20,
                    engine='openpyxl'
                )
            elif file_extension == '.xls':
                df = pd.read_excel(
                    file_path, 
                    sheet_name=str(sheet_name),
                    header=int(header_row),
                    nrows=20,
                    engine='xlrd'
                )
            else:
                return jsonify({'error': f"Formato de archivo no soportado: {file_extension}. Use archivos .xls, .xlsx o .xlsm"}), 400
            
            print(f"DataFrame cargado exitosamente. Columnas: {df.columns.tolist()}")
            
            # Convertir las columnas a string para evitar problemas de serialización
            df.columns = df.columns.astype(str)
            
            return jsonify({
                'columns': df.columns.tolist(),
                'data': df.to_dict('records')
            })
            
        except Exception as e:
            print(f"Error al leer el archivo Excel: {str(e)}")
            return jsonify({'error': f"Error al leer el archivo Excel: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Error detallado en preview_sheet: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        template_path = data['template_path']
        decisions = data['decisions']
        output_directory = os.path.join(os.path.expanduser("~"), "Desktop", "Reporte Generado")
        
        print(f"Iniciando generación de reporte con:")
        print(f"Template: {template_path}")
        print(f"Output directory: {output_directory}")
        print(f"Decisions: {decisions}")

        try:
            ensure_directory(output_directory)
            print(f"Directorio de salida creado/verificado: {output_directory}")
        except Exception as e:
            error_msg = f"No se pudo crear el directorio de salida: {str(e)}"
            print(error_msg)
            return jsonify({'error': error_msg}), 500

        database_sections = {}
        pgf_files_created = []

        for db_decision in decisions:
            database_path = db_decision['database']
            database_name = os.path.basename(database_path).replace('.xlsx', '').replace('.xls', '')
            print(f"\nProcesando base de datos: {database_name}")
            database_sections[database_name] = []

            for sheet_decision in db_decision['decisions']:
                sheet_name = sheet_decision['sheet']
                header_row = sheet_decision['header_row']
                columns = sheet_decision['columns']
                
                print(f"\nProcesando hoja: {sheet_name}")
                print(f"Header row: {header_row}")
                print(f"Columnas seleccionadas: {columns}")
                
                try:
                    # Determinar el motor basado en la extensión del archivo
                    file_extension = os.path.splitext(database_path)[1].lower()
                    
                    # Usar openpyxl para .xlsx y .xlsm, xlrd para .xls
                    if file_extension in ['.xlsx', '.xlsm']:
                        df = pd.read_excel(
                            database_path,
                            sheet_name=sheet_name,
                            header=header_row,
                            engine='openpyxl'
                        )
                    elif file_extension == '.xls':
                        df = pd.read_excel(
                            database_path,
                            sheet_name=sheet_name,
                            header=header_row,
                            engine='xlrd'
                        )
                    else:
                        raise Exception(f"Formato de archivo no soportado: {file_extension}")
                    
                    # Convertir todas las columnas a string para comparación consistente
                    df.columns = df.columns.astype(str)
                    
                    print(f"DataFrame cargado. Dimensiones: {df.shape}")
                    print(f"Columnas disponibles: {df.columns.tolist()}")
                    print(f"Buscando columnas: x='{columns['x_column']}', y='{columns['y_column']}'")

                    # Convertir nombres de columnas buscadas a string
                    x_column = str(columns['x_column'])
                    y_column = str(columns['y_column'])

                    # Verificar que las columnas existan (con manejo de tipos)
                    if x_column not in df.columns and x_column.lower() not in [col.lower() for col in df.columns]:
                        raise Exception(f"Columna X '{x_column}' no encontrada. Columnas disponibles: {df.columns.tolist()}")
                    if y_column not in df.columns and y_column.lower() not in [col.lower() for col in df.columns]:
                        raise Exception(f"Columna Y '{y_column}' no encontrada. Columnas disponibles: {df.columns.tolist()}")

                    # Obtener los nombres exactos de las columnas (preservando mayúsculas/minúsculas)
                    x_column_exact = next(col for col in df.columns if col.lower() == x_column.lower())
                    y_column_exact = next(col for col in df.columns if col.lower() == y_column.lower())

                    # Crear DataFrame de trabajo con manejo explícito de tipos
                    working_df = pd.DataFrame()
                    working_df['x'] = df[x_column_exact].astype(str)
                    working_df['y'] = pd.to_numeric(df[y_column_exact], errors='coerce')
                    working_df = working_df.dropna()
                    
                    print(f"DataFrame de trabajo creado. Dimensiones: {working_df.shape}")
                    print(f"Muestra de datos:")
                    print(working_df.head())

                    # Identificar máximos y mínimos
                    max_min_points = identificar_maximos_minimos(df, columns['y_column'], columns['x_column'])
                    print(f"Máximos y mínimos identificados: {max_min_points}")

                    section_info = {
                        'sheet_name': sheet_name,
                        'max_value': str(max_min_points['max']),
                        'min_value': str(max_min_points['min']),
                        'max_x': str(max_min_points['max_x']),
                        'min_x': str(max_min_points['min_x']),
                        'charts': []
                    }

                    # Generar gráficos según las selecciones
                    for graph_type in sheet_decision['graphs']:
                        try:
                            if graph_type == 'time_series':
                                output_filename = os.path.join(
                                    output_directory, 
                                    f"{database_name}_{sheet_name}_time_series.pgf"
                                )
                                generate_time_series_tikz(
                                    working_df,
                                    'x',
                                    'y',
                                    output_filename
                                )
                                if os.path.exists(output_filename):
                                    section_info['charts'].append(output_filename)
                                    pgf_files_created.append(output_filename)
                                    print(f"Archivo PGF creado: {output_filename}")
                                else:
                                    raise Exception(f"No se pudo crear el archivo PGF: {output_filename}")

                            elif graph_type == 'bar_chart':
                                output_filename = os.path.join(
                                    output_directory, 
                                    f"{database_name}_{sheet_name}_bar_chart.pgf"
                                )
                                generate_bar_chart_tikz(
                                    working_df,
                                    'x',
                                    'y',
                                    output_filename
                                )
                                if os.path.exists(output_filename):
                                    section_info['charts'].append(output_filename)
                                    pgf_files_created.append(output_filename)
                                    print(f"Archivo PGF creado: {output_filename}")
                                else:
                                    raise Exception(f"No se pudo crear el archivo PGF: {output_filename}")

                        except Exception as e:
                            error_msg = f"Error generando gráfico {graph_type} para {sheet_name}: {str(e)}"
                            print(error_msg)
                            return jsonify({'error': error_msg}), 500

                    database_sections[database_name].append(section_info)

                except Exception as e:
                    error_msg = f"Error procesando hoja {sheet_name}: {str(e)}"
                    print(error_msg)
                    import traceback
                    print(traceback.format_exc())
                    return jsonify({'error': error_msg}), 500

        # Verificar que se hayan creado todos los archivos PGF necesarios
        if not pgf_files_created:
            error_msg = "No se generó ningún archivo PGF"
            print(error_msg)
            return jsonify({'error': error_msg}), 500

        # Actualizar el archivo LaTeX
        updated_latex_path = update_latex_file(
            template_path,
            [],
            output_directory,
            database_sections
        )

        if updated_latex_path and os.path.exists(updated_latex_path):
            zip_path = compile_latex(updated_latex_path, pgf_files_created, output_directory)
            if zip_path and os.path.exists(zip_path):
                return jsonify({
                    'success': True, 
                    'output_path': zip_path,
                    'message': 'Reporte generado y comprimido exitosamente'
                })
            else:
                error_msg = "No se pudo crear el archivo ZIP del reporte"
                print(error_msg)
                return jsonify({'error': error_msg}), 500
        else:
            error_msg = "No se pudo actualizar o encontrar el archivo LaTeX generado"
            print(error_msg)
            return jsonify({'error': error_msg}), 500

    except Exception as e:
        error_msg = f"Error general en generate_report: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': error_msg}), 500
    
if __name__ == '__main__':
    app.run(port=5000)