import tkinter as tk
from tkinter import ttk
import os

data_selection = {}  # Diccionario para almacenar las selecciones de bases y gráficos

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

def show_page_three():
    """Aquí inicia la tercera página"""
    for widget in root.winfo_children():
        widget.destroy()  # Elimina los widgets de la página actual

    # Título de la aplicación
    title_label = tk.Label(root, text="Generador de reportes", font=("Arial", 18, "bold"), bg="#f7f6e7", fg="#ff6600")
    title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    # Reporte actual
    report_label = tk.Label(root, text="Base actual:", font=("Arial", 12), bg="#f7f6e7", fg="#666")
    report_label.grid(row=0, column=1, padx=10, sticky="e")

    # Título de sección
    section_label = tk.Label(root, text="Selección de encabezados y columnas", font=("Arial", 16, "bold"), bg="#3366ff", fg="white", width=30)
    section_label.grid(row=1, column=0, columnspan=2, pady=20)

    # Placeholder para la tabla
    table_label = tk.Label(root, text="Base de datos 1", font=("Arial", 14, "bold"), bg="#f7f6e7", fg="#333")
    table_label.grid(row=2, column=0, columnspan=2, pady=10)

    table_frame = tk.Frame(root, bg="#3366ff")  # Placeholder para funcionalidad
    table_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
    for i in range(5):  # Tabla ficticia (5 filas x 5 columnas)
        for j in range(5):
            cell = tk.Label(table_frame, text=" ", font=("Arial", 12), width=10, height=2, relief="solid", bg="#f7f6e7")
            cell.grid(row=i, column=j, padx=1, pady=1)

    # Dropdown para seleccionar encabezado
    header_label = tk.Label(root, text="Selecciona la fila de encabezados", font=("Arial", 12), bg="#f7f6e7", fg="#333")
    header_label.grid(row=4, column=0, pady=10, sticky="w", padx=20)

    header_dropdown = ttk.Combobox(root, state="readonly", font=("Arial", 12))
    header_dropdown["values"] = ["Fila 1", "Fila 2", "Fila 3", "Fila 4", "Fila 5"]  # Opciones de ejemplo
    header_dropdown.grid(row=4, column=1, pady=10, sticky="e", padx=20)

    # Botones de navegación
    prev_button = tk.Button(root, text="Anterior", font=("Arial", 12), bg="#ffcc66", fg="#333", command=show_page_two)
    prev_button.grid(row=5, column=0, pady=20, sticky="w", padx=20)

    next_button = tk.Button(root, text="Siguiente", font=("Arial", 12), bg="#ffcc66", fg="#333", command=show_page_four)
    next_button.grid(row=5, column=1, pady=20, sticky="e", padx=20)

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
            file_path = files_listbox.get(selection[0])
            if file_path not in selected_files_listbox.get(0, tk.END):
                selected_files_listbox.insert(tk.END, file_path)

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