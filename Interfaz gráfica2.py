import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from URLS6 import (
    obtener_nombres_hojas,
    generate_time_series_pgf,
    generate_bar_chart_pgf,
    update_latex_file,
    compile_latex
)
import os
import pandas as pd

data_selection = {
    'base_name': {
        'file_path': str,
        'header_row': int,
        'sheets': [{
            'name': str,
            'columns': {
                'x': str,
                'y': str
            },
            'graphs': ['time_series', 'bar_chart']
        }]
    }
}

def show_page_five():
    """Quinta página: resumen de selección y confirmación."""
    for widget in root.winfo_children():
        widget.destroy()  # Elimina los widgets de la página actual

    # Título de la aplicación
    title_label = tk.Label(root, text="Generador de reportes", font=("Arial", 18, "bold"), bg="#f7f6e7", fg="#ff6600")
    title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    # Base actual
    report_label = tk.Label(root, text="Reporte actual:", font=("Arial", 12), bg="#f7f6e7", fg="#666")
    report_label.grid(row=0, column=1, padx=10, sticky="e")

    # Título de sección
    section_label = tk.Label(root, text="Resumen de selección", font=("Arial", 16, "bold"), bg="#3366ff", fg="white", width=30)
    section_label.grid(row=1, column=0, columnspan=2, pady=20)

    # Resumen de selección
    summary_frame = tk.Frame(root, bg="#ff4500")
    summary_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    if data_selection:
        for i, (base, graphs) in enumerate(data_selection.items()):
            base_label = tk.Label(summary_frame, text=base, font=("Arial", 12), bg="#ff4500", fg="white")
            base_label.grid(row=i, column=0, pady=5, sticky="w")

            graphs_label = tk.Label(summary_frame, text=", ".join(graphs), font=("Arial", 12), bg="#ff4500", fg="white")
            graphs_label.grid(row=i, column=1, pady=5, sticky="w")
    else:
        no_selection_label = tk.Label(summary_frame, text="No se seleccionaron bases o gráficos.",
                                      font=("Arial", 12), bg="#ff4500", fg="white")
        no_selection_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Botón "Anterior"
    previous_button = tk.Button(root, text="Anterior", command=show_page_four, bg="#ff6600", fg="white")
    previous_button.grid(row=3, column=0, pady=20, sticky="w")

    # Botón "Compilar"
    compile_button = tk.Button(root, text="Compilar", command=lambda: print("Compilación iniciada"), bg="#ff6600", fg="white")
    compile_button.grid(row=3, column=1, pady=20, sticky="e")

    def compile_report():
        try:
            output_directory = r"C:\Users\fglruiz\Desktop\Investigacion_e_informes\Reportes\Automatizados\Pruebas"
            latex_template = r"C:\Users\fglruiz\Desktop\Investigacion_e_informes\Reportes\Plantilla para reportes\Plantilla\main2.tex"
            
            database_sections = {}
            
            for base_name, base_data in data_selection.items():
                database_sections[base_name] = []
                
                for sheet in base_data['sheets']:
                    # Generar gráficos
                    charts = []
                    if 'time_series' in sheet['graphs']:
                        time_series_path = os.path.join(output_directory, f"time_series_{base_name}_{sheet['name']}.pgf")
                        generate_time_series_pgf(
                            df=pd.read_excel(base_data['file_path'], sheet_name=sheet['name']),
                            x_column=sheet['columns']['x'],
                            y_column=sheet['columns']['y'],
                            output_filename=time_series_path
                        )
                        charts.append(time_series_path)
                    
                    if 'bar_chart' in sheet['graphs']:
                        bar_chart_path = os.path.join(output_directory, f"bar_chart_{base_name}_{sheet['name']}.pgf")
                        generate_bar_chart_pgf(
                            df=pd.read_excel(base_data['file_path'], sheet_name=sheet['name']),
                            x_column=sheet['columns']['x'],
                            y_column=sheet['columns']['y'],
                            output_filename=bar_chart_path
                        )
                        charts.append(bar_chart_path)
                    
                    section_info = {
                        'sheet_name': sheet['name'],
                        'charts': charts,
                        # Agregar información de máximos y mínimos si es necesario
                    }
                    database_sections[base_name].append(section_info)
            
            # Actualizar y compilar LaTeX
            updated_latex = update_latex_file(latex_template, [], output_directory, database_sections)
            if updated_latex:
                compile_latex(updated_latex, output_directory)
                tk.messagebox.showinfo("Éxito", "Reporte generado correctamente")
            else:
                tk.messagebox.showerror("Error", "Error al generar el reporte")
                
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al compilar: {str(e)}")

    # Modificar el botón compilar
    compile_button.configure(command=compile_report)

def show_page_four():
    """Cuarta página: selección de gráficos y columnas."""
    for widget in root.winfo_children():
        widget.destroy()  # Elimina los widgets de la página actual

    # Título de la aplicación
    title_label = tk.Label(root, text="Generador de reportes", font=("Arial", 18, "bold"), bg="#f7f6e7", fg="#ff6600")
    title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    # Base actual
    report_label = tk.Label(root, text="Base actual:", font=("Arial", 12), bg="#f7f6e7", fg="#666")
    report_label.grid(row=0, column=1, padx=10, sticky="e")

    # Título de sección
    section_label = tk.Label(root, text="Selección de gráficos", font=("Arial", 16, "bold"), bg="#3366ff", fg="white", width=30)
    section_label.grid(row=1, column=0, columnspan=2, pady=20)

    # Frame para la selección de gráficos
    graph_frame = tk.Frame(root, bg="#ff4500")
    graph_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    # Descripción de la selección
    desc_label = tk.Label(graph_frame, text="Selecciona los gráficos que deseas realizar y sus columnas de datos", font=("Arial", 12), bg="#ff4500", fg="white")
    desc_label.grid(row=0, column=0, columnspan=3, pady=10)

    # Gráficos y columnas (dinámico)
    graph_vars = []
    column_vars = []

    for i in range(11):  # Para 11 gráficos
        graph_var = tk.BooleanVar()
        graph_vars.append(graph_var)

        graph_check = tk.Checkbutton(graph_frame, text=f"Gráfico {i+1}", variable=graph_var, bg="#ff4500", fg="white", font=("Arial", 10), selectcolor="#ff7043")
        graph_check.grid(row=i+1, column=0, sticky="w")

        col1_var = tk.StringVar()
        col2_var = tk.StringVar()
        column_vars.append((col1_var, col2_var))

        col1_menu = ttk.Combobox(graph_frame, textvariable=col1_var, values=["Columna A", "Columna B", "Columna C"], state="readonly")
        col1_menu.grid(row=i+1, column=1, padx=5)
        col1_menu.set("Eje x, independiente")

        col2_menu = ttk.Combobox(graph_frame, textvariable=col2_var, values=["Columna A", "Columna B", "Columna C"], state="readonly")
        col2_menu.grid(row=i+1, column=2, padx=5)
        col2_menu.set("Eje y, dependiente")

    # Botón Anterior
    prev_button = tk.Button(root, text="Anterior", command=show_page_three, bg="#ffcc00", fg="black", font=("Arial", 12))
    prev_button.grid(row=3, column=0, pady=20, sticky="w", padx=20)

    # Botón Siguiente
    next_button = tk.Button(root, text="Siguiente", command=show_page_five, bg="#00cc66", fg="white", font=("Arial", 12))
    next_button.grid(row=3, column=1, pady=20, sticky="e", padx=20)

    def save_graph_selection():
        current_base = report_label.cget("text").replace("Base actual: ", "")
        if current_base not in data_selection:
            return
        
        selected_graphs = []
        for i, (graph_var, (col1_var, col2_var)) in enumerate(zip(graph_vars, column_vars)):
            if graph_var.get():
                data_selection[current_base]['sheets'][0]['columns'] = {
                    'x': col1_var.get(),
                    'y': col2_var.get()
                }
                if i < 6:  # Primeros 6 son series de tiempo
                    selected_graphs.append('time_series')
                else:  # Últimos 5 son gráficos de barras
                    selected_graphs.append('bar_chart')
        
        data_selection[current_base]['sheets'][0]['graphs'] = selected_graphs

    # Agregar botón para guardar selección
    save_button = tk.Button(root, text="Guardar selección", command=save_graph_selection, 
                          bg="#ff6600", fg="white")
    save_button.grid(row=3, column=0, columnspan=2, pady=10)

def show_page_three():
    """Tercera página: visualización del Excel y selección de encabezados"""
    for widget in root.winfo_children():
        widget.destroy()

    # Título de la aplicación
    title_label = tk.Label(root, text="Generador de reportes", font=("Arial", 18, "bold"), bg="#f7f6e7", fg="#ff6600")
    title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    # Base actual y manejo seguro de la selección actual
    current_file = None
    if data_selection:
        current_file = next(iter(data_selection))  # Obtiene la primera clave de manera segura
    
    report_label = tk.Label(root, text=f"Base actual: {current_file if current_file else 'No hay archivo seleccionado'}", 
                           font=("Arial", 12), bg="#f7f6e7", fg="#666")
    report_label.grid(row=0, column=1, padx=10, sticky="e")

    # Título de sección
    section_label = tk.Label(root, text="Visualización de datos y selección de encabezados", 
                           font=("Arial", 16, "bold"), bg="#3366ff", fg="white", width=30)
    section_label.grid(row=1, column=0, columnspan=2, pady=20)

    # Frame para la tabla
    table_frame = tk.Frame(root, bg="#f7f6e7")
    table_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    def load_excel_preview():
        if not data_selection or not current_file:
            return
        
        try:
            file_path = data_selection[current_file]['file_path']
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "No se encuentra el archivo Excel")
                return
                
            # Leer las primeras 10 filas del Excel
            df = pd.read_excel(file_path, nrows=10)
            
            # Limpiar el frame antes de agregar nuevos widgets
            for widget in table_frame.winfo_children():
                widget.destroy()
            
            # Crear encabezados de columnas
            for j, col in enumerate(df.columns):
                header = tk.Label(table_frame, text=str(col), font=("Arial", 10, "bold"), 
                                bg="#3366ff", fg="white", relief="solid", width=15)
                header.grid(row=0, column=j, padx=1, pady=1)

            # Mostrar datos
            for i in range(len(df)):
                for j, value in enumerate(df.iloc[i]):
                    cell = tk.Label(table_frame, text=str(value), font=("Arial", 10),
                                  bg="#f7f6e7", relief="solid", width=15)
                    cell.grid(row=i+1, column=j, padx=1, pady=1)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo Excel: {str(e)}")

    # Cargar vista previa del Excel
    load_excel_preview()

    # Frame para selección de encabezados
    header_frame = tk.Frame(root, bg="#f7f6e7")
    header_frame.grid(row=3, column=0, columnspan=2, pady=20)

    header_label = tk.Label(header_frame, text="Selecciona la fila de encabezados:", 
                          font=("Arial", 12), bg="#f7f6e7", fg="#333")
    header_label.pack(side="left", padx=10)

    header_var = tk.StringVar()
    header_entry = tk.Entry(header_frame, textvariable=header_var, width=5)
    header_entry.pack(side="left", padx=5)

    def save_header_selection():
        try:
            header_row = int(header_var.get()) - 1  # Convertir a base 0
            if current_file in data_selection:
                data_selection[current_file]['header_row'] = header_row
                messagebox.showinfo("Éxito", "Fila de encabezados guardada correctamente")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un número válido")

    save_button = tk.Button(header_frame, text="Guardar selección", 
                          command=save_header_selection, bg="#ff6600", fg="white")
    save_button.pack(side="left", padx=10)

    # Botones de navegación
    prev_button = tk.Button(root, text="Anterior", command=show_page_two, 
                          bg="#ffcc00", fg="#333", font=("Arial", 12))
    prev_button.grid(row=4, column=0, pady=20, sticky="w", padx=20)

    next_button = tk.Button(root, text="Siguiente", command=show_page_four, 
                          bg="#ffcc00", fg="#333", font=("Arial", 12))
    next_button.grid(row=4, column=1, pady=20, sticky="e", padx=20)

def show_page_two():
    """Aquí inicia la segunda página"""
    for widget in root.winfo_children():
        widget.destroy()

    # Título de la aplicación
    title_label = tk.Label(root, text="Generador de reportes", font=("Arial", 18, "bold"), bg="#f7f6e7", fg="#ff6600")
    title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    # Reporte actual
    report_label = tk.Label(root, text="Reporte actual:", font=("Arial", 12), bg="#f7f6e7", fg="#666")
    report_label.grid(row=0, column=1, padx=10, sticky="e")

    # Título de sección
    section_label = tk.Label(root, text="Selección de bases de datos", font=("Arial", 16, "bold"), bg="#3366ff", fg="white", width=30)
    section_label.grid(row=1, column=0, columnspan=2, pady=20)

    # Frame para la búsqueda y selección de archivos
    search_frame = tk.Frame(root, bg="#ff4500")
    search_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    # Entrada de búsqueda
    search_label = tk.Label(search_frame, text="Buscar archivo:", font=("Arial", 12), bg="#ff4500", fg="white")
    search_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")

    search_entry = tk.Entry(search_frame, font=("Arial", 12), width=40)
    search_entry.grid(row=0, column=1, pady=5, padx=5)

    # Lista de archivos encontrados
    files_listbox = tk.Listbox(search_frame, font=("Arial", 12), width=50, height=8)
    files_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

    # Lista de archivos seleccionados
    selected_label = tk.Label(search_frame, text="Archivos seleccionados:", font=("Arial", 12), bg="#ff4500", fg="white")
    selected_label.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="w")

    selected_files_listbox = tk.Listbox(search_frame, font=("Arial", 12), width=50, height=4)
    selected_files_listbox.grid(row=3, column=0, columnspan=2, pady=5, padx=5)

    def search_files():
        search_term = search_entry.get().strip()
        files_listbox.delete(0, tk.END)
        
        # Construir la ruta a la carpeta en el escritorio
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        base_path = os.path.join(desktop_path, 'Bases de datos para Reportes')
        
        if not os.path.exists(base_path):
            files_listbox.insert(tk.END, "No se encontró la carpeta 'Bases de datos para Reportes'")
            return

        # Buscar archivos Excel que coincidan con el término de búsqueda
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.lower().endswith(('.xls', '.xlsx')) and search_term.lower() in file.lower():
                    relative_path = os.path.relpath(root, base_path)
                    display_path = os.path.join(relative_path, file)
                    files_listbox.insert(tk.END, display_path)

    def add_selected_file():
        selection = files_listbox.curselection()
        if selection:
            relative_path = files_listbox.get(selection[0])
            # Construir la ruta completa
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            base_path = os.path.join(desktop_path, 'Bases de datos para Reportes')
            file_path = os.path.join(base_path, relative_path)
            
            if file_path not in selected_files_listbox.get(0, tk.END):
                selected_files_listbox.insert(tk.END, relative_path)
                # Guardar en data_selection con la ruta completa
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                data_selection[base_name] = {
                    'file_path': file_path,
                    'header_row': 0,
                    'sheets': [{
                        'name': '',
                        'columns': {
                            'x': '',
                            'y': ''
                        },
                        'graphs': []
                    }]
                }

    # Botones de búsqueda y selección
    search_button = tk.Button(search_frame, text="Buscar", command=search_files, bg="#ffcc66", fg="#333")
    search_button.grid(row=0, column=2, pady=5, padx=5)

    add_button = tk.Button(search_frame, text="Agregar", command=add_selected_file, bg="#ffcc66", fg="#333")
    add_button.grid(row=1, column=2, pady=5, padx=5)

    # Botones de navegación
    prev_button = tk.Button(root, text="Anterior", font=("Arial", 12), bg="#ffcc66", fg="#333", command=show_page_one)
    prev_button.grid(row=4, column=0, pady=20, sticky="w", padx=20)

    next_button = tk.Button(root, text="Siguiente", font=("Arial", 12), bg="#ffcc66", fg="#333", command=show_page_three)
    next_button.grid(row=4, column=1, pady=20, sticky="e", padx=20)

def show_page_one():
    # Elimina los widgets existentes
    for widget in root.winfo_children():
        widget.destroy()

    # Primera página
    root.title("Generador de Reportes")
    root.configure(bg="#f7f6e7")  # Color de fondo

    # Etiqueta del título
    title_label = tk.Label(root, text="Generador de reportes", font=("Arial", 18, "bold"), bg="#f7f6e7", fg="#ff6600")
    title_label.pack(pady=20)

    # Marco para el selector de reporte
    frame = tk.Frame(root, bg="#f7f6e7")
    frame.pack(pady=20)

    # Etiqueta para el selector
    label = tk.Label(frame, text="Elije el reporte que quieres realizar:", font=("Arial", 12), bg="#f7f6e7", fg="#333")
    label.pack(anchor="w")

    # Variable para el reporte seleccionado
    report_var = tk.StringVar()

    # Menú desplegable (combobox)
    report_dropdown = ttk.Combobox(frame, textvariable=report_var, state="readonly", font=("Arial", 12))
    report_dropdown["values"] = ["Reporte de Ejemplo"]  # Modificado para mostrar solo una opción
    report_dropdown.set("Reporte de Ejemplo")  # Establecer valor por defecto
    report_dropdown.pack(pady=5)

    # Botón "Siguiente"
    next_button = tk.Button(root, text="Siguiente", font=("Arial", 12), bg="#ffcc66", fg="#333", command=show_page_two)
    next_button.pack(pady=20)

# Crear la ventana principal
root = tk.Tk()
root.geometry("600x400")
root.configure(bg="#f7f6e7")  # Color de fondo

# Mostrar la primera página
show_page_one()

# Ejecutar la aplicación
root.mainloop()