import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import re
import threading
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import re
import threading

def sanitize_folder_name(folder_name):
    return re.sub(r'[<>:"/\\|?*]', '_', folder_name)

def download_file_with_progress(url, file_path, timeout=300):
    progress_bar = None
    try:
        response = requests.get(url, stream=True, timeout=100)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))  # Tamaño total en bytes
        
        progress_bar = tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            desc=f"Descargando {os.path.basename(file_path)}"
        )

        with open(file_path, 'wb') as file:
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # Filtrar datos vacíos
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        print(f"Archivo descargado en: {file_path}")
        return True

    except requests.exceptions.RequestException as e:
        if progress_bar:
            progress_bar.close()
        print(f"Error al descargar {os.path.basename(file_path)}: {e}")
        return False

def download_with_timeout(url, file_path, timeout):
    download_success = [False]  # Usamos una lista para modificarla dentro del hilo

    def download():
        download_success[0] = download_file_with_progress(url, file_path)

    thread = threading.Thread(target=download)
    thread.start()
    thread.join(timeout)  # Esperar hasta que el hilo termine o se alcance el timeout

    if thread.is_alive():
        print(f"Tiempo excedido para descargar {os.path.basename(file_path)}. Saltando...")
        if os.path.exists(file_path):
            os.remove(file_path)  # Eliminar archivo incompleto
        thread.join(1)
        return False

    return download_success[0]

def extract_date_from_filename(filename):
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d')
    return None

def obtener_link_interactivo(base_url):
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        database_folder = os.path.join(desktop_path, "Bases de datos para Reportes")
        os.makedirs(database_folder, exist_ok=True)

        archivos_encontrados = []
        links_pendientes = [base_url]
        visitados = set()
        carpetas_usadas = set()

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

                contenedor = soup.find('div', {'id': 'block-solucionweb-content', 'class': 'contenido block block-system block-system-main-block'})
                if not contenedor:
                    print("No se encontró el contenedor especificado en esta página.")
                    continue

                for link in contenedor.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(current_url, href)

                    nombre_carpeta = link.text.strip()
                    nombre_carpeta = sanitize_folder_name(nombre_carpeta)
                    carpeta_destino = os.path.join(database_folder, nombre_carpeta)

                    if absolute_url.lower().endswith(('.pdf', '.xml')):
                        print(f"Saltando archivo no deseado: {absolute_url}")
                        continue

                    if absolute_url.lower().endswith(('.xls', '.xlsx')):
                        file_name = os.path.basename(absolute_url)
                        file_path = os.path.join(carpeta_destino, file_name)
                        
                        # Check if the file already exists and compare dates
                        existing_files = [f for f in os.listdir(carpeta_destino) if f.startswith("Estadísticas_Macroeconomicas_") and f.endswith(".xlsx")]
                        should_download = True
                        
                        if existing_files:
                            new_file_date = extract_date_from_filename(file_name)
                            if new_file_date:
                                for existing_file in existing_files:
                                    existing_file_date = extract_date_from_filename(existing_file)
                                    if existing_file_date and existing_file_date >= new_file_date:
                                        print(f"Archivo más reciente o igual ya existe: {existing_file}")
                                        should_download = False
                                        break
                            else:
                                print(f"No se pudo extraer la fecha del archivo: {file_name}")
                                should_download = False
                        
                        if should_download:
                            archivos_encontrados.append((carpeta_destino, absolute_url))
                            carpetas_usadas.add(carpeta_destino)
                    elif absolute_url not in visitados:
                        links_pendientes.append(absolute_url)

            except Exception as e:
                print(f"Error al procesar {current_url}: {e}")

        if not archivos_encontrados:
            print("No se encontraron archivos Excel nuevos o actualizados en los enlaces explorados.")
            return []

        print("\nDescargando archivos nuevos o actualizados...")
        for carpeta_destino, url in archivos_encontrados:
            file_name = os.path.basename(url)
            file_path = os.path.join(carpeta_destino, file_name)

            os.makedirs(carpeta_destino, exist_ok=True)
            print(f"\nIntentando descargar: {file_name}")
            if not download_with_timeout(url, file_path, timeout=300):
                print(f"Saltando archivo: {file_name} por exceder el tiempo límite.")

        # Eliminar carpetas vacías
        for carpeta in os.listdir(database_folder):
            carpeta_path = os.path.join(database_folder, carpeta)
            if carpeta_path not in carpetas_usadas and os.path.isdir(carpeta_path):
                try:
                    os.rmdir(carpeta_path)
                    print(f"Carpeta vacía eliminada: {carpeta_path}")
                except OSError:
                    print(f"No se pudo eliminar la carpeta: {carpeta_path}")

        return [os.path.join(carpeta_destino, os.path.basename(url)) for carpeta_destino, url in archivos_encontrados]

    except Exception as e:
        print(f"Error: {e}")
        return []

# Ejecución del script con la URL base
if __name__ == "__main__":
    base_url = "https://banguat.gob.gt/page/estadisticas-macroeconomicas"
    obtener_link_interactivo(base_url)