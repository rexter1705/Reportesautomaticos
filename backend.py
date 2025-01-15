from flask import Flask, jsonify
import os

app = Flask(__name__)

# Ruta donde se encuentran las plantillas LaTeX
latex_templates_dir = r"C:\Users\fglruiz\Desktop\Investigacion_e_informes\Reportes\Plantilla para reportes\Plantilla"

@app.route('/templates', methods=['GET'])
def get_templates():
    try:
        templates = [
            {'name': os.path.basename(file), 'path': os.path.join(latex_templates_dir, file)}
            for file in os.listdir(latex_templates_dir)
            if file.endswith('.tex')
        ]
        return jsonify(templates)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
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


if __name__ == '__main__':
    app.run(port=5000)
