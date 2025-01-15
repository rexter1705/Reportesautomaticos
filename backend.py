from flask import Flask, jsonify, request
import pandas as pd
import os
from URLS6 import (
    generate_time_series_pgf,
    generate_bar_chart_pgf,
    identificar_maximos_minimos,
    agregar_max_min_latex,
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
        header_row = data.get('header_row', 0)
        
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, nrows=20)
        return jsonify({
            'columns': df.columns.tolist(),
            'data': df.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        template_path = data['template_path']
        decisions = data['decisions']
        output_directory = r"C:\Users\fglruiz\Desktop\Investigacion_e_informes\Reportes\Automatizados\Pruebas"
        
        ensure_directory(output_directory)
        database_sections = {}
        chart_paths = []

        # Procesar cada base de datos y sus decisiones
        for db_decision in decisions:
            database_path = db_decision['database']
            database_name = os.path.basename(database_path).replace('.xlsx', '').replace('.xls', '')
            database_sections[database_name] = []

            for sheet_decision in db_decision['decisions']:
                sheet_name = sheet_decision['sheet']
                header_row = sheet_decision['header_row']
                columns = sheet_decision['columns']
                
                # Leer los datos
                df = pd.read_excel(database_path, sheet_name=sheet_name, header=header_row)
                x_data = df[columns['x_column']]
                y_data = df[columns['y_column']]

                # Generar gráficos según las selecciones
                for graph_type in sheet_decision['graphs']:
                    if graph_type == 'time_series':
                        chart_path = generate_time_series_pgf(
                            x_data, 
                            y_data,
                            output_directory,
                            f"{database_name}_{sheet_name}_time_series"
                        )
                        # Identificar máximos y mínimos
                        max_min_points = identificar_maximos_minimos(x_data, y_data)
                        # Agregar anotaciones de máximos y mínimos al LaTeX
                        latex_content = agregar_max_min_latex(max_min_points)
                        database_sections[database_name].append({
                            'chart_path': chart_path,
                            'annotations': latex_content
                        })
                        chart_paths.append(chart_path)

                    elif graph_type == 'bar_chart':
                        chart_path = generate_bar_chart_pgf(
                            x_data,
                            y_data,
                            output_directory,
                            f"{database_name}_{sheet_name}_bar_chart"
                        )
                        database_sections[database_name].append({
                            'chart_path': chart_path,
                            'annotations': None
                        })
                        chart_paths.append(chart_path)

        # Actualizar el archivo LaTeX con los gráficos y anotaciones
        updated_latex_path = update_latex_file(
            template_path,
            chart_paths,
            output_directory,
            database_sections
        )

        if updated_latex_path:
            compile_latex(updated_latex_path, output_directory)
            return jsonify({'success': True, 'output_path': output_directory})
        else:
            return jsonify({'error': 'No se pudo actualizar el archivo LaTeX.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
