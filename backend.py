from flask import Flask, jsonify, request
import pandas as pd
import os
import matplotlib.pyplot as plt
import zipfile
from datetime import datetime
import matplotlib as mpl
mpl.use("pgf")

class ReportGenerator:
    def __init__(self, output_directory):
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
        self.customization = GraphCustomization()
        self._setup_plot_style()

    def _setup_plot_style(self):
        # Usar un estilo por defecto de matplotlib en lugar de seaborn
        plt.style.use('default')
        plt.rcParams.update({
            'pgf.texsystem': 'pdflatex',
            'font.family': 'serif',
            'text.usetex': True,
            'pgf.rcfonts': False,
            'figure.figsize': (6, 4),
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1,
            # Añadir algunos estilos básicos para mejorar la apariencia
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.linestyle': '--',
            'axes.labelsize': 10,
            'axes.titlesize': 12,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8
        })

    def generate_time_series(self, df, x_column, y_column, output_filename, options=None, report_type="latex"):
        try:
            if options is None:
                options = self.customization.default_options

            df = df.dropna(subset=[x_column, y_column]).copy()
            df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
            df = df.dropna(subset=[y_column])
            df[x_column] = df[x_column].astype(str)

            # Agrupar y sumar los valores de y para cada x
            df = df.groupby(x_column)[y_column].sum().reset_index()

            try:
                df[x_column] = pd.to_datetime(df[x_column])
                df = df.sort_values(by=x_column)
                df[x_column] = df[x_column].dt.strftime('%Y-%m-%d')
            except Exception:
                pass

            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Plot con opciones personalizadas
            line = ax.plot(df[x_column], df[y_column], 
                          color=options['colors']['line'],
                          marker='o' if options['labels']['show_points'] else None,
                          markersize=4)[0]

            # Configurar etiquetas y título
            ax.set_xlabel(options['axes']['x_label'] or x_column, 
                        fontdict=self.customization.get_font_properties(options['axes']['label_font']))
            ax.set_ylabel(options['axes']['y_label'] or y_column,
                        fontdict=self.customization.get_font_properties(options['axes']['label_font']))
            ax.set_title(options['axes']['title'] or 'Serie de tiempo',
                        fontdict=self.customization.get_font_properties(options['axes']['title_font']))

            # Configurar grid
            if options['grid']['show']:
                ax.grid(True, linestyle=options['grid']['style'], 
                       alpha=options['grid']['alpha'], 
                       color=options['colors']['grid'])

            # Rotar etiquetas del eje X
            plt.xticks(rotation=options['labels']['rotation'], ha='right')

            # Agregar etiquetas de valores si está habilitado
            if options['labels']['show_values']:
                for x, y in zip(df[x_column], df[y_column]):
                    ax.annotate(
                        str(y),  # Mostrar el valor exacto como string
                        xy=(x, y),
                        xytext=(0, 10),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=options['labels']['font_size']
                    )

            plt.tight_layout(pad=1.0)

            # Modificar la extensión del archivo según el tipo de reporte
            if report_type == "word":
                output_filename = output_filename.replace('.pgf', '.jpg')
                plt.savefig(output_filename, format='jpg', bbox_inches='tight', pad_inches=0.2, dpi=300)
            else:
                plt.savefig(output_filename, bbox_inches='tight', pad_inches=0.2)
            
            plt.close()
            return True
        except Exception as e:
            print(f"Error generando gráfico de serie temporal: {e}")
            return False

    def generate_bar_chart(self, df, x_column, y_column, output_filename, options=None, report_type="latex"):
        try:
            if options is None:
                options = self.customization.default_options

            df = df.dropna(subset=[x_column, y_column]).copy()
            df[x_column] = df[x_column].astype(str)
            df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
            df = df.dropna(subset=[y_column])

            # Agrupar y sumar los valores de y para cada x
            df = df.groupby(x_column)[y_column].sum().reset_index()

            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Plot con opciones personalizadas
            bars = ax.bar(df[x_column], df[y_column], 
                         color=options['colors']['bar'])

            # Configurar etiquetas y título
            ax.set_xlabel(options['axes']['x_label'] or x_column,
                        fontdict=self.customization.get_font_properties(options['axes']['label_font']))
            ax.set_ylabel(options['axes']['y_label'] or y_column,
                        fontdict=self.customization.get_font_properties(options['axes']['label_font']))
            ax.set_title(options['axes']['title'] or 'Gráfico de barras',
                        fontdict=self.customization.get_font_properties(options['axes']['title_font']))

            # Configurar grid
            if options['grid']['show']:
                ax.grid(True, linestyle=options['grid']['style'],
                       alpha=options['grid']['alpha'],
                       color=options['colors']['grid'])

            # Rotar etiquetas del eje X
            plt.xticks(rotation=options['labels']['rotation'], ha='right')

            # Agregar etiquetas de valores si está habilitado
            if options['labels']['show_values']:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(
                        str(height),  # Mostrar el valor exacto como string
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=options['labels']['font_size']
                    )

            plt.tight_layout(pad=1.0)

            # Modificar la extensión del archivo según el tipo de reporte
            if report_type == "word":
                output_filename = output_filename.replace('.pgf', '.jpg')
                plt.savefig(output_filename, format='jpg', bbox_inches='tight', pad_inches=0.2, dpi=300)
            else:
                plt.savefig(output_filename, bbox_inches='tight', pad_inches=0.2)
            
            plt.close()
            return True
        except Exception as e:
            print(f"Error generando gráfico de barras: {e}")
            return False

    def generate_word_report(self, database_sections):
        """Genera un archivo de texto con el contenido del reporte para Word."""
        report_content = []
        
        for database_name, sections in database_sections.items():
            report_content.append(f"\nAnálisis de {database_name}\n")
            report_content.append("=" * 50 + "\n")
            
            for section_info in sections:
                report_content.append(f"\nHoja: {section_info['sheet_name']}\n")
                report_content.append("-" * 30 + "\n")
                
                # Agregar análisis con datos agrupados
                report_content.append("Análisis:")
                report_content.append(f"El valor máximo observado (suma total) es: {section_info['max_value']} en {section_info['max_x']}")
                report_content.append(f"El valor mínimo observado (suma total) es: {section_info['min_value']} en {section_info['min_x']}\n")
                
                # Agregar rutas de las imágenes
                report_content.append("Gráficos generados:")
                for chart_path in section_info['charts']:
                    report_content.append(f"- {os.path.basename(chart_path)}")
                report_content.append("\n")
        
        # Guardar el contenido en un archivo de texto
        report_path = os.path.join(self.output_directory, "reporte_word.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        return report_path

class DataAnalyzer:
    @staticmethod
    def get_max_min_values(df, y_column, x_column):
        # Primero eliminamos las filas donde y_column es NaN
        df = df.dropna(subset=[y_column])
        
        # Convertimos la columna Y a numérico y eliminamos cualquier valor NaN resultante
        df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
        df = df.dropna(subset=[y_column])
        
        # Agrupamos y sumamos los valores
        df = df.groupby(x_column)[y_column].sum().reset_index()
        
        # Ahora obtenemos los valores máximos y mínimos de los datos agrupados
        max_value = df[y_column].max()
        min_value = df[y_column].min()
        max_x = df[df[y_column] == max_value][x_column].iloc[0]
        min_x = df[df[y_column] == min_value][x_column].iloc[0]
        return {'max': max_value, 'min': min_value, 'max_x': max_x, 'min_x': min_x}

class LatexGenerator:
    def __init__(self, output_directory):
        self.output_directory = output_directory

    def _generate_section_content(self, section_info):
        content = f"""
        \\subsection*{{Hoja: {section_info['sheet_name']}}}
        \\begin{{multicols}}{{2}}
        \\noindent{{\\textbf{{Analisis:}}\\\\
        El valor maximo observado (suma total) es: \\textbf{{{section_info['max_value']}}} en \\textbf{{{section_info['max_x']}}}.\\\\
        El valor minimo observado (suma total) es: \\textbf{{{section_info['min_value']}}} en \\textbf{{{section_info['min_x']}}}.}}

        \\columnbreak
        \\begin{{center}}
        """
        
        for chart_path in section_info['charts']:
            chart_filename = os.path.basename(chart_path)
            content += f"""
            \\begin{{center}}
            \\begin{{adjustbox}}{{width=\\columnwidth,height=0.4\\textheight,keepaspectratio}}
            \\input{{{chart_filename}}}
            \\end{{adjustbox}}
            \\end{{center}}
            \\vspace{{10pt}}
            """
        
        content += """
        \\end{center}
        \\end{multicols}
        \\vspace{15pt}
        """
        return content

    def _generate_database_content(self, database_sections):
        content = ""
        for database_name, sections in database_sections.items():
            content += f"\n\\section*{{Analisis de {database_name}}}\n"
            for section_info in sections:
                content += self._generate_section_content(section_info)
        return content

    def update_latex_file(self, latex_template_path, database_sections):
        try:
            with open(latex_template_path, 'r') as file:
                latex_content = file.read()

            packages_to_include = [
                "\\usepackage{multicol}",
                "\\usepackage{adjustbox}",
                "\\usepackage{graphicx}",
                "\\usepackage{pgf}",
                "\\usepackage{pgfplots}",
                "\\pgfplotsset{compat=1.18}"
            ]
            for package in packages_to_include:
                if package not in latex_content:
                    latex_content = latex_content.replace("\\documentclass", f"{package}\n\\documentclass")

            content_by_database = self._generate_database_content(database_sections)
            latex_content = latex_content.replace("char", content_by_database) if "char" in latex_content else latex_content + content_by_database

            updated_latex_path = os.path.join(self.output_directory, "Updated_Prueba.tex")
            with open(updated_latex_path, 'w') as file:
                file.write(latex_content)
            return updated_latex_path
        except Exception as e:
            print(f"Error actualizando archivo LaTeX: {e}")
            return None

class FileManager:
    def __init__(self, output_directory):
        self.output_directory = output_directory

    def compile_latex(self, updated_latex_path, chart_paths):
        try:
            with open(updated_latex_path, 'r') as file:
                latex_content = file.read()
            
            output_tex_path = os.path.join(self.output_directory, "main.tex")
            with open(output_tex_path, 'w') as file:
                file.write(latex_content)
            
            zip_filename = os.path.join(self.output_directory, f"output_files_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip")
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file in [output_tex_path] + chart_paths:
                    if os.path.exists(file):
                        zipf.write(file, os.path.basename(file))
            return zip_filename
        except Exception as e:
            print(f"Error procesando archivos: {e}")
            return None

class GraphCustomization:
    def __init__(self):
        self.default_options = {
            'colors': {
                'line': '#1f77b4',  # Azul
                'bar': '#1f77b4',
                'point': '#1f77b4',
                'grid': '#cccccc'
            },
            'data_format': {
                'y_axis': 'number',  # 'number', 'percentage', 'currency'
                'decimal_places': 2,
                'thousand_separator': ',',
                'currency_symbol': '$'
            },
            'labels': {
                'show_values': True,
                'show_points': True,
                'font_size': 8,
                'rotation': 45
            },
            'axes': {
                'x_label': '',
                'y_label': '',
                'title': '',
                'title_font': {
                    'family': 'serif',
                    'size': 12,
                    'weight': 'normal',
                    'style': 'normal'
                },
                'label_font': {
                    'family': 'serif',
                    'size': 10,
                    'weight': 'normal',
                    'style': 'normal'
                }
            },
            'grid': {
                'show': True,
                'style': '--',
                'alpha': 0.3
            },
            'legend': {
                'show': True,
                'position': 'best',
                'font_size': 10
            }
        }

    def format_value(self, value, format_type='number'):
        if format_type == 'percentage':
            return f"{value:.2f}%"
        elif format_type == 'currency':
            return f"${value:,.2f}"
        else:  # number
            return f"{value:,.2f}"

    def get_font_properties(self, font_config):
        return {
            'family': font_config['family'],
            'size': font_config['size'],
            'weight': font_config['weight'],
            'style': font_config['style']
        }

class BackendAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.output_directory = os.path.join(os.path.expanduser("~"), "Desktop", "Reporte Generado")
        self.report_generator = ReportGenerator(self.output_directory)
        self.data_analyzer = DataAnalyzer()
        self.latex_generator = LatexGenerator(self.output_directory)
        self.file_manager = FileManager(self.output_directory)
        self.carpeta_plantillas = None
        self.carpeta_bases_datos = None
        self.template_path = None
        self.graph_customization = GraphCustomization()
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/set-template-folder', methods=['POST'])
        def set_template_folder():
            data = request.json
            self.carpeta_plantillas = data.get('folder_path')
            if not self.carpeta_plantillas or not os.path.exists(self.carpeta_plantillas):
                return jsonify({'error': "La carpeta especificada no existe."}), 404
            return jsonify({'success': True, 'message': f"Carpeta de plantillas configurada: {self.carpeta_plantillas}"})

        @self.app.route('/templates', methods=['GET'])
        def get_templates():
            if not self.carpeta_plantillas:
                return jsonify({'error': "No se ha seleccionado una carpeta de plantillas."}), 404

            try:
                templates = [{'name': file, 'path': os.path.join(self.carpeta_plantillas, file)}
                           for file in os.listdir(self.carpeta_plantillas)
                           if file.endswith('.tex')]
                
                if not templates:
                    return jsonify({'error': "No se encontraron archivos .tex en el directorio"}), 404
                
                return jsonify(templates)
            except Exception as e:
                return jsonify({'error': f"Error al buscar plantillas: {str(e)}"}), 500

        @self.app.route('/set-database-folder', methods=['POST'])
        def set_database_folder():
            data = request.json
            self.carpeta_bases_datos = data.get('folder_path')
            if not self.carpeta_bases_datos or not os.path.exists(self.carpeta_bases_datos):
                return jsonify({'error': "La carpeta especificada no existe."}), 404
            return jsonify({'success': True, 'message': f"Carpeta de bases de datos configurada: {self.carpeta_bases_datos}"})

        @self.app.route('/databases', methods=['GET'])
        def get_databases():
            if not self.carpeta_bases_datos:
                return jsonify({'error': "No se ha seleccionado una carpeta de bases de datos."}), 404

            try:
                databases = [{'name': file, 'path': os.path.join(root, file)}
                           for root, _, files in os.walk(self.carpeta_bases_datos)
                           for file in files
                           if file.lower().endswith(('.xls', '.xlsx'))]

                if not databases:
                    return jsonify({'error': "No se encontraron archivos Excel en la carpeta."}), 404

                return jsonify(databases)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/preview-sheet', methods=['POST'])
        def preview_sheet():
            try:
                data = request.json
                file_path = data['file_path']
                sheet_name = data['sheet_name']
                header_row = data.get('header_row', 0)
                
                if not os.path.exists(file_path):
                    return jsonify({'error': f"El archivo no existe: {file_path}"}), 404
                
                file_extension = os.path.splitext(file_path)[1].lower()
                engine = 'openpyxl' if file_extension in ['.xlsx', '.xlsm'] else 'xlrd' if file_extension == '.xls' else None
                
                if not engine:
                    return jsonify({'error': f"Formato de archivo no soportado: {file_extension}"}), 400
                
                df = pd.read_excel(file_path, sheet_name=str(sheet_name), header=int(header_row), nrows=20, engine=engine)
                df.columns = df.columns.astype(str)
                
                return jsonify({
                    'columns': df.columns.tolist(),
                    'data': df.to_dict('records')
                })
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/set-template', methods=['POST'])
        def set_template():
            data = request.json
            template_path = data.get('template_path')
            if not template_path or not os.path.exists(template_path):
                return jsonify({'error': "La plantilla especificada no existe."}), 404
            self.template_path = template_path
            return jsonify({'success': True, 'message': f"Plantilla configurada: {self.template_path}"})

        @self.app.route('/generate-report', methods=['POST'])
        def generate_report():
            try:
                data = request.json
                report_type = data.get('report_type', 'latex')
                decisions = data['decisions']
                
                if report_type == "latex" and not self.template_path:
                    raise Exception("No se ha seleccionado una plantilla LaTeX")

                database_sections = {}
                chart_files_created = []

                for db_decision in decisions:
                    database_path = db_decision['database']
                    database_name = os.path.basename(database_path).replace('.xlsx', '').replace('.xls', '')
                    database_sections[database_name] = []

                    for sheet_decision in db_decision['decisions']:
                        sheet_name = sheet_decision['sheet']
                        header_row = sheet_decision['header_row']
                        columns = sheet_decision['columns']
                        
                        try:
                            file_extension = os.path.splitext(database_path)[1].lower()
                            engine = 'openpyxl' if file_extension in ['.xlsx', '.xlsm'] else 'xlrd' if file_extension == '.xls' else None
                            
                            if not engine:
                                raise Exception(f"Formato de archivo no soportado: {file_extension}")
                            
                            df = pd.read_excel(database_path, sheet_name=sheet_name, header=header_row, engine=engine)
                            df.columns = df.columns.astype(str)
                            
                            x_column = str(columns['x_column'])
                            y_column = str(columns['y_column'])

                            if x_column not in df.columns and x_column.lower() not in [col.lower() for col in df.columns]:
                                raise Exception(f"Columna X '{x_column}' no encontrada")
                            if y_column not in df.columns and y_column.lower() not in [col.lower() for col in df.columns]:
                                raise Exception(f"Columna Y '{y_column}' no encontrada")

                            x_column_exact = next(col for col in df.columns if col.lower() == x_column.lower())
                            y_column_exact = next(col for col in df.columns if col.lower() == y_column.lower())

                            working_df = pd.DataFrame()
                            working_df['x'] = df[x_column_exact].astype(str)
                            working_df['y'] = pd.to_numeric(df[y_column_exact], errors='coerce')
                            working_df = working_df.dropna()

                            max_min_points = self.data_analyzer.get_max_min_values(df, columns['y_column'], columns['x_column'])

                            section_info = {
                                'sheet_name': sheet_name,
                                'max_value': str(max_min_points['max']),
                                'min_value': str(max_min_points['min']),
                                'max_x': str(max_min_points['max_x']),
                                'min_x': str(max_min_points['min_x']),
                                'charts': []
                            }

                            for graph_type in sheet_decision['graphs']:
                                output_filename = os.path.join(
                                    self.output_directory, 
                                    f"{database_name}_{sheet_name}_{graph_type}.pgf"
                                )
                                
                                if graph_type == 'time_series':
                                    if self.report_generator.generate_time_series(
                                        working_df, 
                                        'x', 
                                        'y', 
                                        output_filename,
                                        options=sheet_decision['columns'].get('graph_options'),
                                        report_type=report_type
                                    ):
                                        section_info['charts'].append(output_filename)
                                        chart_files_created.append(output_filename)
                                elif graph_type == 'bar_chart':
                                    if self.report_generator.generate_bar_chart(
                                        working_df, 
                                        'x', 
                                        'y', 
                                        output_filename,
                                        options=sheet_decision['columns'].get('graph_options'),
                                        report_type=report_type
                                    ):
                                        section_info['charts'].append(output_filename)
                                        chart_files_created.append(output_filename)

                            database_sections[database_name].append(section_info)

                        except Exception as e:
                            raise Exception(f"Error procesando hoja {sheet_name}: {str(e)}")

                if not chart_files_created:
                    raise Exception("No se generó ningún archivo PGF")

                if report_type == "word":
                    report_path = self.report_generator.generate_word_report(database_sections)
                    
                    zip_filename = os.path.join(self.output_directory, f"reporte_word_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip")
                    with zipfile.ZipFile(zip_filename, 'w') as zipf:
                        zipf.write(report_path, os.path.basename(report_path))
                        for chart_path in chart_files_created:
                            if os.path.exists(chart_path):
                                zipf.write(chart_path, os.path.basename(chart_path))
                    
                    return jsonify({
                        'success': True,
                        'output_path': zip_filename,
                        'message': 'Reporte Word generado y comprimido exitosamente'
                    })
                else:
                    updated_latex_path = self.latex_generator.update_latex_file(self.template_path, database_sections)
                    if not updated_latex_path or not os.path.exists(updated_latex_path):
                        raise Exception("No se pudo actualizar o encontrar el archivo LaTeX generado")

                    zip_path = self.file_manager.compile_latex(updated_latex_path, chart_files_created)
                    if not zip_path or not os.path.exists(zip_path):
                        raise Exception("No se pudo crear el archivo ZIP del reporte")

                    return jsonify({
                        'success': True,
                        'output_path': zip_path,
                        'message': 'Reporte LaTeX generado y comprimido exitosamente'
                    })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def run(self, port=5000):
        self.app.run(port=port)

if __name__ == '__main__':
    api = BackendAPI()
    api.run()