import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from database.queries import (
    obtener_mes_actual,
    obtener_meses,
    insertar_mes,
    obtener_movimientos,
    insertar_movimiento,
    eliminar_movimiento,
    actualizar_movimiento,
    obtener_resumen_mes,
    obtener_categorias,
    obtener_subcategorias,
)

MESES_NOMBRES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

class MovimientosFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self.mes_actual = None
        self._construir_ui()
        self._inicializar_mes()

    # ─── Construcción de UI ────────────────────────────────────

    def _construir_ui(self):
        self._construir_encabezado()
        self._construir_resumen()
        self._construir_tabla()
        self._construir_barra_acciones()

    def _construir_encabezado(self):
        enc = tk.Frame(self, bg="#ecf0f1")
        enc.pack(fill="x", padx=20, pady=(20, 0))

        tk.Label(
            enc, text="Movimientos",
            bg="#ecf0f1", fg="#2c3e50",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        # Selector de mes
        selector = tk.Frame(enc, bg="#ecf0f1")
        selector.pack(side="right")

        tk.Label(
            selector, text="Mes:",
            bg="#ecf0f1", fg="#2c3e50",
            font=("Arial", 11)
        ).pack(side="left", padx=(0, 6))

        self.combo_mes = ttk.Combobox(selector, width=18, state="readonly")
        self.combo_mes.pack(side="left")
        self.combo_mes.bind("<<ComboboxSelected>>", self._al_cambiar_mes)

        tk.Button(
            selector, text="+ Nuevo mes",
            bg="#2c3e50", fg="white",
            font=("Arial", 10, "bold"),
            bd=0, padx=10, pady=4,
            cursor="hand2",
            command=self._abrir_popup_nuevo_mes
        ).pack(side="left", padx=(10, 0))

    def _construir_resumen(self):
        self.frame_resumen = tk.Frame(self, bg="#ecf0f1")
        self.frame_resumen.pack(fill="x", padx=20, pady=(14, 0))

        def tarjeta(parent, titulo, color):
            card = tk.Frame(parent, bg="white", padx=16, pady=10)
            card.pack(side="left", expand=True, fill="x", padx=(0, 10))
            tk.Label(card, text=titulo, bg="white", fg="#7f8c8d",
                     font=("Arial", 9)).pack(anchor="w")
            lbl = tk.Label(card, text="$ 0,00", bg="white", fg=color,
                           font=("Arial", 15, "bold"))
            lbl.pack(anchor="w")
            return lbl

        self.lbl_saldo_inicial = tarjeta(self.frame_resumen, "Saldo inicial", "#2c3e50")
        self.lbl_ingresos     = tarjeta(self.frame_resumen, "Ingresos", "#27ae60")
        self.lbl_egresos      = tarjeta(self.frame_resumen, "Egresos", "#e74c3c")
        self.lbl_saldo_final  = tarjeta(self.frame_resumen, "Saldo final", "#2980b9")

    def _construir_tabla(self):
        contenedor = tk.Frame(self, bg="#ecf0f1")
        contenedor.pack(fill="both", expand=True, padx=20, pady=14)

        cols = ("fecha", "categoria", "subcategoria", "descripcion", "tipo", "monto")
        self.tabla = ttk.Treeview(contenedor, columns=cols, show="headings", selectmode="browse")

        encabezados = {
            "fecha":        ("Fecha",        90),
            "categoria":    ("Categoría",   130),
            "subcategoria": ("Subcategoría",140),
            "descripcion":  ("Descripción", 200),
            "tipo":         ("Tipo",         80),
            "monto":        ("Monto",        100),
        }
        for col, (texto, ancho) in encabezados.items():
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="center" if col in ("fecha","tipo","monto") else "w")

        scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tabla.bind("<Double-1>", self._al_doble_clic_tabla)

        # Colores por tipo
        self.tabla.tag_configure("ingreso", foreground="#27ae60")
        self.tabla.tag_configure("egreso",  foreground="#e74c3c")

    def _construir_barra_acciones(self):
        barra = tk.Frame(self, bg="#ecf0f1")
        barra.pack(fill="x", padx=20, pady=(0, 16))

        tk.Button(
            barra, text="+ Agregar movimiento",
            bg="#1abc9c", fg="white",
            font=("Arial", 10, "bold"),
            bd=0, padx=12, pady=6,
            cursor="hand2",
            command=self._abrir_popup_movimiento
        ).pack(side="left")

        tk.Button(
            barra, text="🗑 Eliminar seleccionado",
            bg="#e74c3c", fg="white",
            font=("Arial", 10, "bold"),
            bd=0, padx=12, pady=6,
            cursor="hand2",
            command=self._eliminar_seleccionado
        ).pack(side="left", padx=(10, 0))
    
    def _al_doble_clic_tabla(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        mov_id = int(seleccion[0])
        # Buscar el dict completo del movimiento en la lista actual
        movimientos = obtener_movimientos(self.mes_actual["id"])
        mov = next((m for m in movimientos if m["id"] == mov_id), None)
        if mov:
            self._abrir_popup_edicion_movimiento(mov)
    
    def _abrir_popup_edicion_movimiento(self, mov):
        popup = tk.Toplevel(self)
        popup.title("Editar movimiento")
        self._centrar_popup(popup, 360, 340)
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Editar movimiento", font=("Arial", 14, "bold"),
                fg="#2c3e50").pack(pady=(20, 10))

        form = tk.Frame(popup)
        form.pack(padx=24, fill="x")

        # Fecha
        tk.Label(form, text="Fecha (YYYY-MM-DD):", anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        entry_fecha = tk.Entry(form, width=16)
        entry_fecha.insert(0, mov["fecha"])
        entry_fecha.grid(row=0, column=1, sticky="w", padx=(8, 0))

        # Tipo
        tk.Label(form, text="Tipo:", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        combo_tipo = ttk.Combobox(form, values=["ingreso", "egreso"], width=12, state="readonly")
        combo_tipo.set(mov["tipo"].lower())
        combo_tipo.grid(row=1, column=1, sticky="w", padx=(8, 0))

        # Categoría
        tk.Label(form, text="Categoría:", anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        combo_cat = ttk.Combobox(form, width=18, state="readonly")
        combo_cat.grid(row=2, column=1, sticky="w", padx=(8, 0))

        # Subcategoría
        tk.Label(form, text="Subcategoría:", anchor="w").grid(row=3, column=0, sticky="w", pady=4)
        combo_sub = ttk.Combobox(form, width=18, state="readonly")
        combo_sub.grid(row=3, column=1, sticky="w", padx=(8, 0))

        # Descripción
        tk.Label(form, text="Descripción:", anchor="w").grid(row=4, column=0, sticky="w", pady=4)
        entry_desc = tk.Entry(form, width=22)
        entry_desc.insert(0, mov["descripcion"] or "")
        entry_desc.grid(row=4, column=1, sticky="w", padx=(8, 0))

        # Monto
        tk.Label(form, text="Monto:", anchor="w").grid(row=5, column=0, sticky="w", pady=4)
        entry_monto = tk.Entry(form, width=14)
        entry_monto.insert(0, str(mov["monto"]))
        entry_monto.grid(row=5, column=1, sticky="w", padx=(8, 0))

        # ── Cascada tipo → categoría → subcategoría ──
        cats_cache = obtener_categorias()
        cats_filtradas = []
        subs_filtradas = []

        def actualizar_categorias(tipo=None, seleccionar_nombre=None):
            nonlocal cats_filtradas
            t = tipo or combo_tipo.get()
            cats_filtradas = [c for c in cats_cache if c["tipo"] == t]
            combo_cat["values"] = [c["nombre"] for c in cats_filtradas]
            if seleccionar_nombre:
                nombres = [c["nombre"] for c in cats_filtradas]
                if seleccionar_nombre in nombres:
                    combo_cat.current(nombres.index(seleccionar_nombre))
                else:
                    combo_cat.set("")
            else:
                combo_cat.set("")
            actualizar_subcategorias(seleccionar_nombre=None)

        def actualizar_subcategorias(event=None, seleccionar_nombre=None):
            nonlocal subs_filtradas
            idx = combo_cat.current()
            if idx < 0:
                subs_filtradas = []
                combo_sub["values"] = []
                combo_sub.set("")
                return
            cat_id = cats_filtradas[idx]["id"]
            subs_filtradas = obtener_subcategorias(cat_id)
            combo_sub["values"] = [s["nombre"] for s in subs_filtradas]
            nombre = seleccionar_nombre
            if nombre:
                nombres = [s["nombre"] for s in subs_filtradas]
                if nombre in nombres:
                    combo_sub.current(nombres.index(nombre))
                else:
                    combo_sub.set("")
            else:
                combo_sub.set("")

        combo_tipo.bind("<<ComboboxSelected>>", lambda e: actualizar_categorias())
        combo_cat.bind("<<ComboboxSelected>>", actualizar_subcategorias)

    # Poblar con los valores actuales del movimiento
        actualizar_categorias(tipo=mov["tipo"].lower(), seleccionar_nombre=mov["categoria"])
        actualizar_subcategorias(seleccionar_nombre=mov["subcategoria"])

        def guardar():
            try:
                fecha = entry_fecha.get().strip()
                date.fromisoformat(fecha)
                monto = float(entry_monto.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "Fecha inválida o monto incorrecto.", parent=popup)
                return

            if combo_cat.current() < 0:
                messagebox.showerror("Error", "Seleccioná una categoría.", parent=popup)
                return

            if combo_sub.current() < 0 and len(subs_filtradas) > 0:
                messagebox.showerror("Error", "Seleccioná una subcategoría.", parent=popup)
                return

            cat_id = cats_filtradas[combo_cat.current()]["id"]
            sub_id = subs_filtradas[combo_sub.current()]["id"] if combo_sub.current() >= 0 else None
            tipo   = combo_tipo.get()
            desc   = entry_desc.get().strip()

            actualizar_movimiento(mov["id"], fecha, cat_id, sub_id, desc, monto, tipo)
            self._recargar_datos()
            popup.destroy()

        botones = tk.Frame(popup)
        botones.pack(pady=16)

        tk.Button(
            botones, text="Guardar",
            bg="#1abc9c", fg="white",
            font=("Arial", 11, "bold"),
            bd=0, padx=16, pady=6,
            cursor="hand2",
            command=guardar
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            botones, text="Cancelar",
            bg="#95a5a6", fg="white",
            font=("Arial", 11, "bold"),
            bd=0, padx=16, pady=6,
            cursor="hand2",
            command=popup.destroy
        ).pack(side="left")

    # ─── Lógica de inicialización ──────────────────────────────

    def _inicializar_mes(self):
        self._recargar_combo_meses()
        mes = obtener_mes_actual()
        if mes:
            self.mes_actual = mes
            self._seleccionar_mes_en_combo(mes)
            self._recargar_datos()
        # Si no hay ningún mes, el usuario deberá crear uno con "+ Nuevo mes"

    def _recargar_combo_meses(self):
        self._meses_lista = obtener_meses()
        valores = [
            f"{MESES_NOMBRES[m['mes']]} {m['año']}"
            for m in self._meses_lista
        ]
        self.combo_mes["values"] = valores

    def _seleccionar_mes_en_combo(self, mes):
        etiqueta = f"{MESES_NOMBRES[mes['mes']]} {mes['año']}"
        valores = list(self.combo_mes["values"])
        if etiqueta in valores:
            self.combo_mes.current(valores.index(etiqueta))

    def _al_cambiar_mes(self, event=None):
        idx = self.combo_mes.current()
        if idx >= 0:
            self.mes_actual = self._meses_lista[idx]
            self._recargar_datos()

    def _recargar_datos(self):
        self._recargar_tabla()
        self._recargar_resumen()

    def _recargar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        if not self.mes_actual:
            return
        for mov in obtener_movimientos(self.mes_actual["id"]):
            self.tabla.insert("", "end", iid=str(mov["id"]), values=(
                mov["fecha"],
                mov["categoria"],
                mov["subcategoria"],
                mov["descripcion"] or "",
                mov["tipo"].capitalize(),
                f"$ {mov['monto']:,.2f}",
            ), tags=(mov["tipo"],))

    def _recargar_resumen(self):
        if not self.mes_actual:
            return
        resumen = obtener_resumen_mes(self.mes_actual["id"])
        si = self.mes_actual["saldo_inicial"]
        self.lbl_saldo_inicial.config(text=f"$ {si:,.2f}")
        self.lbl_ingresos.config(text=f"$ {resumen['total_ingresos']:,.2f}")
        self.lbl_egresos.config(text=f"$ {resumen['total_egresos']:,.2f}")
        self.lbl_saldo_final.config(text=f"$ {resumen['saldo']:,.2f}")

    # ─── Popup: nuevo mes ──────────────────────────────────────

    def _abrir_popup_nuevo_mes(self):
        popup = tk.Toplevel(self)
        popup.title("Nuevo mes")
        self._centrar_popup(popup, 320, 240)
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Nuevo mes", font=("Arial", 14, "bold"),
                 fg="#2c3e50").pack(pady=(20, 10))

        form = tk.Frame(popup)
        form.pack(padx=24, fill="x")

        hoy = date.today()

        # Año
        tk.Label(form, text="Año:", anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        entry_año = tk.Entry(form, width=10)
        entry_año.insert(0, str(hoy.year))
        entry_año.grid(row=0, column=1, sticky="w", padx=(8, 0))

        # Mes
        tk.Label(form, text="Mes:", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        combo_mes = ttk.Combobox(form, values=MESES_NOMBRES[1:], width=14, state="readonly")
        combo_mes.current(hoy.month - 1)
        combo_mes.grid(row=1, column=1, sticky="w", padx=(8, 0))

        # Saldo inicial
        tk.Label(form, text="Saldo inicial:", anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        entry_saldo = tk.Entry(form, width=14)
        entry_saldo.insert(0, "0")
        entry_saldo.grid(row=2, column=1, sticky="w", padx=(8, 0))

        def guardar():
            try:
                año = int(entry_año.get())
                mes = combo_mes.current() + 1
                saldo = float(entry_saldo.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "Revisá los datos ingresados.", parent=popup)
                return

            # Validación de mes duplicado
            ya_existe = any(m["año"] == año and m["mes"] == mes for m in self._meses_lista)
            if ya_existe:
                nombre_mes = MESES_NOMBRES[mes]
                messagebox.showwarning(
                    "Mes duplicado",
                    f"{nombre_mes} {año} ya existe.\nSeleccionalo desde el selector de mes.",
                    parent=popup
                )
                return

            nuevo_id = insertar_mes(año, mes, saldo)
            self._recargar_combo_meses()
            self.mes_actual = {"id": nuevo_id, "año": año, "mes": mes, "saldo_inicial": saldo}
            self._seleccionar_mes_en_combo(self.mes_actual)
            popup.destroy()
            self._recargar_datos()
            

        tk.Button(
            popup, text="Crear mes",
            bg="#1abc9c", fg="white",
            font=("Arial", 11, "bold"),
            bd=0, padx=16, pady=6,
            cursor="hand2",
            command=guardar
        ).pack(pady=18)

    # ─── Popup: nuevo movimiento ───────────────────────────────
    def _centrar_popup(self, popup, ancho, alto):
        self.update_idletasks()
        ventana = self.winfo_toplevel()
        x = ventana.winfo_x() + (ventana.winfo_width() // 2) - (ancho // 2)
        y = ventana.winfo_y() + (ventana.winfo_height() // 2) - (alto // 2)
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _abrir_popup_movimiento(self):
        if not self.mes_actual:
            messagebox.showwarning("Sin mes", "Primero creá un mes antes de agregar movimientos.")
            return

        popup = tk.Toplevel(self)
        popup.title("Nuevo movimiento")
        self._centrar_popup(popup, 320, 320)
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Nuevo movimiento", font=("Arial", 14, "bold"),
                 fg="#2c3e50").pack(pady=(20, 10))

        form = tk.Frame(popup)
        form.pack(padx=24, fill="x")

        hoy = date.today()

        # Fecha
        tk.Label(form, text="Fecha (YYYY-MM-DD):", anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        entry_fecha = tk.Entry(form, width=16)
        entry_fecha.insert(0, hoy.strftime("%Y-%m-%d"))
        entry_fecha.grid(row=0, column=1, sticky="w", padx=(8, 0))

        # Tipo
        tk.Label(form, text="Tipo:", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        combo_tipo = ttk.Combobox(form, values=["ingreso", "egreso"], width=12, state="readonly")
        combo_tipo.current(1)
        combo_tipo.grid(row=1, column=1, sticky="w", padx=(8, 0))

        # Categoría
        tk.Label(form, text="Categoría:", anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        combo_cat = ttk.Combobox(form, width=18, state="readonly")
        combo_cat.grid(row=2, column=1, sticky="w", padx=(8, 0))

        # Subcategoría
        tk.Label(form, text="Subcategoría:", anchor="w").grid(row=3, column=0, sticky="w", pady=4)
        combo_sub = ttk.Combobox(form, width=18, state="readonly")
        combo_sub.grid(row=3, column=1, sticky="w", padx=(8, 0))

        # Descripción
        tk.Label(form, text="Descripción:", anchor="w").grid(row=4, column=0, sticky="w", pady=4)
        entry_desc = tk.Entry(form, width=22)
        entry_desc.grid(row=4, column=1, sticky="w", padx=(8, 0))

        # Monto
        tk.Label(form, text="Monto:", anchor="w").grid(row=5, column=0, sticky="w", pady=4)
        entry_monto = tk.Entry(form, width=14)
        entry_monto.grid(row=5, column=1, sticky="w", padx=(8, 0))

        # ── Lógica de cascada tipo → categoría → subcategoría ──

        self._cats_cache = obtener_categorias()  # todas, activas

        def actualizar_categorias(event=None):
            tipo = combo_tipo.get()
            cats_filtradas = [c for c in self._cats_cache if c["tipo"] == tipo]
            self._cats_filtradas = cats_filtradas
            combo_cat["values"] = [c["nombre"] for c in cats_filtradas]
            combo_cat.set("")
            combo_sub.set("")
            combo_sub["values"] = []

        def actualizar_subcategorias(event=None):
            idx = combo_cat.current()
            if idx < 0:
                return
            cat_id = self._cats_filtradas[idx]["id"]
            subs = obtener_subcategorias(cat_id)
            self._subs_filtradas = subs
            combo_sub["values"] = [s["nombre"] for s in subs]
            combo_sub.set("")

        combo_tipo.bind("<<ComboboxSelected>>", actualizar_categorias)
        combo_cat.bind("<<ComboboxSelected>>", actualizar_subcategorias)
        actualizar_categorias()  # poblar con el valor inicial ("egreso")

        def guardar():
            try:
                fecha = entry_fecha.get().strip()
                date.fromisoformat(fecha)
                monto = float(entry_monto.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "Fecha inválida o monto incorrecto.", parent=popup)
                return

            if combo_cat.current() < 0:
                messagebox.showerror("Error", "Seleccioná una categoría.", parent=popup)
                return

            if combo_sub.current() < 0 and len(self._subs_filtradas) > 0:
                messagebox.showerror("Error", "Seleccioná una subcategoría.", parent=popup)
                return

            cat_id = self._cats_filtradas[combo_cat.current()]["id"]
            sub_id = self._subs_filtradas[combo_sub.current()]["id"] if combo_sub.current() >= 0 else None
            tipo   = combo_tipo.get()
            desc   = entry_desc.get().strip()

            insertar_movimiento(self.mes_actual["id"], fecha, cat_id, sub_id, desc, monto, tipo)
            self._recargar_datos()
            popup.destroy()

        botones = tk.Frame(popup)
        botones.pack(pady=16)

        tk.Button(
            botones, text="Guardar",
            bg="#1abc9c", fg="white",
            font=("Arial", 11, "bold"),
            bd=0, padx=16, pady=6,
            cursor="hand2",
            command=guardar
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            botones, text="Cancelar",
            bg="#95a5a6", fg="white",
            font=("Arial", 11, "bold"),
            bd=0, padx=16, pady=6,
            cursor="hand2",
            command=popup.destroy
        ).pack(side="left")

    # ─── Eliminar ──────────────────────────────────────────────

    def _eliminar_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccioná un movimiento para eliminar.")
            return
        confirmar = messagebox.askyesno("Confirmar", "¿Eliminar el movimiento seleccionado?")
        if confirmar:
            mov_id = int(seleccion[0])
            eliminar_movimiento(mov_id)
            self._recargar_datos()