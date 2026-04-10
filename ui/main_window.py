import tkinter as tk
from tkinter import ttk
from database.db import inicializar_db

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Gastos")
        self.geometry("950x600")
        self.resizable(False, False)
        inicializar_db()
        self._construir_ui()

    def _construir_ui(self):
        self._construir_barra_lateral()
        self._construir_area_contenido()
        # Frame activo por defecto
        self.mostrar_frame("categorias")

    def _construir_barra_lateral(self):
        barra = tk.Frame(self, bg="#2c3e50", width=180)
        barra.pack(side="left", fill="y")
        barra.pack_propagate(False)

        titulo = tk.Label(
            barra, text="💰 Control\nde Gastos",
            bg="#2c3e50", fg="white",
            font=("Arial", 14, "bold"),
            pady=20
        )
        titulo.pack(fill="x")

        separador = tk.Frame(barra, bg="#34495e", height=1)
        separador.pack(fill="x", padx=10)

        secciones = [
            ("📋 Categorías", "categorias"),
            ("💸 Movimientos", "movimientos"),
            ("📊 Resumen", "resumen"),
        ]

        self.botones_nav = {}
        for texto, seccion in secciones:
            btn = tk.Button(
                barra, text=texto,
                bg="#2c3e50", fg="white",
                font=("Arial", 11),
                bd=0, pady=12,
                cursor="hand2",
                anchor="w", padx=20,
                activebackground="#1abc9c",
                activeforeground="white",
                command=lambda s=seccion: self.mostrar_frame(s)
            )
            btn.pack(fill="x")
            self.botones_nav[seccion] = btn

    def _construir_area_contenido(self):
        self.area_contenido = tk.Frame(self, bg="#ecf0f1")
        self.area_contenido.pack(side="right", fill="both", expand=True)
        self.frames = {}

    def mostrar_frame(self, seccion):
        # Limpiar contenido actual
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        # Resaltar botón activo
        for nombre, btn in self.botones_nav.items():
            if nombre == seccion:
                btn.config(bg="#1abc9c")
            else:
                btn.config(bg="#2c3e50")

        # Cargar el frame correspondiente 
        frame = tk.Frame(self.area_contenido, bg="#ecf0f1")
        frame.pack(fill="both", expand=True)

        placeholder = tk.Label(
            frame,
            text=f"Sección: {seccion.capitalize()}\n(próximamente)",
            bg="#ecf0f1", fg="#7f8c8d",
            font=("Arial", 16)
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")