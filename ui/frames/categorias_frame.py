import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import (
    obtener_categorias,
    obtener_subcategorias,
    insertar_categoria,
    insertar_subcategoria,
    actualizar_categoria,
    actualizar_subcategoria,
    deshabilitar_categoria,
    deshabilitar_subcategoria,
)

class CategoriasFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self._construir_ui()
        self._cargar_categorias()

    def _construir_ui(self):
        # Encabezado
        encabezado = tk.Frame(self, bg="#ecf0f1")
        encabezado.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            encabezado, text="Categorías",
            bg="#ecf0f1", fg="#2c3e50",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        tk.Button(
            encabezado, text="+ Nueva categoría",
            bg="#1abc9c", fg="white",
            font=("Arial", 10, "bold"),
            bd=0, padx=12, pady=6,
            cursor="hand2",
            command=self._abrir_popup_categoria
        ).pack(side="right")

        # Contenedor de dos columnas
        columnas = tk.Frame(self, bg="#ecf0f1")
        columnas.pack(fill="both", expand=True, padx=20, pady=10)

        self.col_ingresos = self._construir_columna(columnas, "💚 Ingresos", "ingreso")
        self.col_ingresos.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.col_egresos = self._construir_columna(columnas, "🔴 Egresos", "egreso")
        self.col_egresos.pack(side="right", fill="both", expand=True)

    def _construir_columna(self, parent, titulo, tipo):
        frame = tk.Frame(parent, bg="white", relief="flat", bd=1)

        tk.Label(
            frame, text=titulo,
            bg="#34495e", fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        ).pack(fill="x")

        canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        contenedor = tk.Frame(canvas, bg="white")
        canvas_window = canvas.create_window((0, 0), window=contenedor, anchor="nw")

        def ajustar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def ajustar_ancho(event):
            canvas.itemconfig(canvas_window, width=event.width)

        contenedor.bind("<Configure>", ajustar_scroll)
        canvas.bind("<Configure>", ajustar_ancho)

        # Guardar referencias para poder refrescar
        setattr(self, f"contenedor_{tipo}", contenedor)

        return frame

    def _cargar_categorias(self):
        for tipo in ("ingreso", "egreso"):
            contenedor = getattr(self, f"contenedor_{tipo}")
            for widget in contenedor.winfo_children():
                widget.destroy()

            categorias = obtener_categorias(tipo=tipo)
            for cat in categorias:
                self._construir_fila_categoria(contenedor, cat)

    def _construir_fila_categoria(self, parent, cat):
        fila = tk.Frame(parent, bg="white")
        fila.pack(fill="x", pady=(8, 0), padx=10)

        # Nombre de la categoría
        tk.Label(
            fila, text=f"▶ {cat['nombre']}",
            bg="white", fg="#2c3e50",
            font=("Arial", 11, "bold")
        ).pack(side="left")

        # Botones de acción
        acciones = tk.Frame(fila, bg="white")
        acciones.pack(side="right")

        tk.Button(
            acciones, text="Editar",
            bg="#3498db", fg="white",
            font=("Arial", 8, "bold"),
            bd=0, padx=8, pady=3,
            cursor="hand2",
            command=lambda c=cat: self._abrir_popup_categoria(c)
        ).pack(side="left", padx=2)

        tk.Button(
            acciones, text="Baja",
            bg="#e74c3c", fg="white",
            font=("Arial", 8, "bold"),
            bd=0, padx=8, pady=3,
            cursor="hand2",
            command=lambda c=cat: self._confirmar_deshabilitar_categoria(c)
        ).pack(side="left", padx=2)

        tk.Button(
            acciones, text="+ Sub",
            bg="#ecf0f1", fg="#2c3e50",
            font=("Arial", 9), bd=0,
            padx=6, pady=2,
            cursor="hand2",
            command=lambda c=cat: self._abrir_popup_subcategoria(c)
        ).pack(side="left", padx=(6, 0))

        # Subcategorías
        subcategorias = obtener_subcategorias(cat["id"])
        for sub in subcategorias:
            self._construir_fila_subcategoria(parent, sub)

        # Separador
        tk.Frame(parent, bg="#ecf0f1", height=1).pack(fill="x", pady=(8, 0), padx=10)

    def _construir_fila_subcategoria(self, parent, sub):
        fila = tk.Frame(parent, bg="white")
        fila.pack(fill="x", padx=30)

        tk.Label(
            fila, text=f"· {sub['nombre']}",
            bg="white", fg="#555",
            font=("Arial", 10)
        ).pack(side="left")

        acciones = tk.Frame(fila, bg="white")
        acciones.pack(side="right")

        tk.Button(
            acciones, text="Editar",
            bg="#3498db", fg="white",
            font=("Arial", 8, "bold"),
            bd=0, padx=8, pady=3,
            cursor="hand2",
            command=lambda s=sub: self._abrir_popup_subcategoria(None, s)
        ).pack(side="left", padx=2)

        tk.Button(
            acciones, text="Baja",
            bg="#e74c3c", fg="white",
            font=("Arial", 8, "bold"),
            bd=0, padx=8, pady=3,
            cursor="hand2",
            command=lambda s=sub: self._confirmar_deshabilitar_subcategoria(s)
        ).pack(side="left", padx=2)

    # ─── Popups ───────────────────────────────────────────────
    def _centrar_popup(self, popup, ancho, alto):
        self.update_idletasks()
        ventana = self.winfo_toplevel()
        x = ventana.winfo_x() + (ventana.winfo_width() // 2) - (ancho // 2)
        y = ventana.winfo_y() + (ventana.winfo_height() // 2) - (alto // 2)
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _abrir_popup_categoria(self, cat=None):
        popup = tk.Toplevel(self)
        popup.title("Nueva categoría" if cat is None else "Editar categoría")
        self._centrar_popup(popup, 320, 220)
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Nombre:", font=("Arial", 11)).pack(pady=(20, 4))
        entrada_nombre = tk.Entry(popup, font=("Arial", 11), width=28)
        entrada_nombre.pack()

        tk.Label(popup, text="Tipo:", font=("Arial", 11)).pack(pady=(12, 4))
        tipo_var = tk.StringVar(value="egreso")
        frame_tipo = tk.Frame(popup)
        frame_tipo.pack()
        tk.Radiobutton(frame_tipo, text="Ingreso", variable=tipo_var, value="ingreso").pack(side="left", padx=10)
        tk.Radiobutton(frame_tipo, text="Egreso", variable=tipo_var, value="egreso").pack(side="left", padx=10)

        if cat:
            entrada_nombre.insert(0, cat["nombre"])
            tipo_var.set(cat["tipo"])
            for widget in frame_tipo.winfo_children():
                widget.config(state="disabled")

        def guardar():
            nombre = entrada_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Campo vacío", "El nombre no puede estar vacío.", parent=popup)
                return
            if cat:
                actualizar_categoria(cat["id"], nombre)
            else:
                insertar_categoria(nombre, tipo_var.get())
            popup.destroy()
            self._cargar_categorias()

        tk.Button(
            popup, text="Guardar",
            bg="#1abc9c", fg="white",
            font=("Arial", 11, "bold"),
            bd=0, padx=16, pady=6,
            cursor="hand2",
            command=guardar
        ).pack(pady=20)

    def _abrir_popup_subcategoria(self, cat=None, sub=None):
        popup = tk.Toplevel(self)
        popup.title("Nueva subcategoría" if sub is None else "Editar subcategoría")
        self._centrar_popup(popup, 320, 160)
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Nombre:", font=("Arial", 11)).pack(pady=(20, 4))
        entrada = tk.Entry(popup, font=("Arial", 11), width=28)
        entrada.pack()

        if sub:
            entrada.insert(0, sub["nombre"])

        def guardar():
            nombre = entrada.get().strip()
            if not nombre:
                messagebox.showwarning("Campo vacío", "El nombre no puede estar vacío.", parent=popup)
                return
            if sub:
                actualizar_subcategoria(sub["id"], nombre)
            else:
                insertar_subcategoria(cat["id"], nombre)
            popup.destroy()
            self._cargar_categorias()

        tk.Button(
            popup, text="Guardar",
            bg="#1abc9c", fg="white",
            font=("Arial", 11, "bold"),
            bd=0, padx=16, pady=6,
            cursor="hand2",
            command=guardar
        ).pack(pady=16)

    # ─── Confirmaciones de baja ────────────────────────────────

    def _confirmar_deshabilitar_categoria(self, cat):
        confirmar = messagebox.askyesno(
            "Deshabilitar categoría",
            f"¿Deshabilitar '{cat['nombre']}'?\nTambién se deshabilitarán todas sus subcategorías."
        )
        if confirmar:
            deshabilitar_categoria(cat["id"])
            self._cargar_categorias()

    def _confirmar_deshabilitar_subcategoria(self, sub):
        confirmar = messagebox.askyesno(
            "Deshabilitar subcategoría",
            f"¿Deshabilitar '{sub['nombre']}'?"
        )
        if confirmar:
            deshabilitar_subcategoria(sub["id"])
            self._cargar_categorias()