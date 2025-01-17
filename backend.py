from flask import Flask, jsonify, request
import pandas as pd
import os
from URLS6 import (
    generate_time_series_pgf,
    generate_bar_chart_pgf,
    identificar_maximos_minimos,
    update_latex_file,
    compile_latex,
    ensure_directory
)

app = Flask(__name__)

# Ruta donde se encuentran las plantillas LaTeX
latex_templates_dir = r"C:\Users\fglruiz\OneDrive - Administradora del Fondo de Garantia MICOOPE\Escritorio\Investigacion_e_informes\Reportes\Plantilla para reportes\Plantilla"

@app.route('/templates', methods=['GET'])
def get_templates():
    try:
        # Imprimir la ruta para depuración
        print(f"Buscando plantillas en: {latex_templates_dir}")
        
        # Verificar si el directorio existe
        if not os.path.exists(latex_templates_dir):
            print(f"El directorio no existe: {latex_templates_dir}")
            # Intentar crear el directorio
            os.makedirs(latex_templates_dir, exist_ok=True)
            return jsonify({'error': f"No se encontró el directorio: {latex_templates_dir}"}), 404

        templates = []
        for file in os.listdir(latex_templates_dir):
            if file.endswith('.tex'):
                template_path = os.path.join(latex_templates_dir, file)
                print(f"Encontrada plantilla: {template_path}")
                templates.append({
                    'name': file,
                    'path': template_path
                })
        
        if not templates:
            print("No se encontraron archivos .tex en el directorio")
            return jsonify({'error': "No se encontraron archivos .tex en el directorio"}), 404
        
        print(f"Plantillas encontradas: {templates}")    
        return jsonify(templates)
    except Exception as e:
        print(f"Error al buscar plantillas: {str(e)}")
        return jsonify({'error': f"Error al buscar plantillas: {str(e)}"}), 500
    
@app.route('/databases', methods=['GET'])
def get_databases():
    try:
        # Directorio de las bases de datos
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        base_path = os.path.join(desktop_path, 'Bases de datos para reportes')
        
        if not os.path.exists(base_path):
            return jsonify({'error': "No se encontró la carpeta 'Bases de datos para reportes'."}), 404
        
        databases = []
        for root, _, files in os.walk(base_path):
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
        output_directory = data.get('output_directory', r"C:\Users\fglruiz\Desktop\Investigacion_e_informes\Reportes\Automatizados\Pruebas")
        
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
                                generate_time_series_pgf(
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
                                generate_bar_chart_pgf(
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
            compile_latex(updated_latex_path, output_directory)
            return jsonify({
                'success': True, 
                'output_path': output_directory,
                'pgf_files': pgf_files_created
            })
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
