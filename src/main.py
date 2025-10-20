import tkinter as tk                                  # importa tkinter con alias 'tk' para construir la GUI (widgets básicos)
from tkinter import ttk, messagebox, simpledialog, Toplevel  # importa submódulos útiles: ttk (widgets themed), cuadros de diálogo y ventana toplevel
from collections import deque                         # importa deque para usar una cola eficiente (append/popleft)
import threading                                      # importa threading para ejecutar tareas en segundo plano (no bloquear la GUI)
import time                                           # importa time para pausas/simulación de reproducción

# ----------------- MODELOS Y LÓGICA -----------------
class Song:                                           # define la clase Song que representa una canción
    def __init__(self, title, artist, duration):      # constructor que recibe título, artista y duración
        self.title = title                            # atributo 'title': cadena con el título de la canción
        self.artist = artist                          # atributo 'artist': cadena con el nombre del artista
        self.duration = duration                      # atributo 'duration': entero con la duración en segundos

    def __str__(self):                                # método especial para representar la canción como cadena
        return f"{self.title} — {self.artist} ({self.duration}s)"  # retorna una representación legible "Título — Artista (Xs)"

class BeatQueue:                                      # clase que maneja la cola, pila de efectos y playlist
    def __init__(self):                               # constructor de BeatQueue
        self.queue = deque()                          # atributo 'queue': deque que actúa como cola FIFO de canciones
        self.effects_stack = []                       # atributo 'effects_stack': lista que actúa como pila LIFO de efectos
        self.playlist = []                            # atributo 'playlist': lista que almacena el historial de canciones reproducidas
        self.current_song = None                      # atributo 'current_song': canción actualmente en reproducción (None si no hay)
        self.playing = False                          # atributo 'playing': booleano que indica si hay reproducción en curso
        self.available_effects = [                     # atributo 'available_effects': lista con nombres de efectos disponibles
            "Reverb", "Delay", "Echo", "Pitch", "Flanger", "Distortion"
        ]

    def enqueue_song(self, song):                     # método para añadir una canción a la cola
        self.queue.append(song)                       # agrega 'song' al final de la cola (FIFO)

    def dequeue_song(self):                           # método para extraer la primera canción de la cola
        if self.queue:                                # si la cola no está vacía
            return self.queue.popleft()               # devuelve y elimina el elemento del frente
        return None                                   # si está vacía, devuelve None

    def add_effect(self, effect):                     # método para apilar un efecto en la pila LIFO
        """Agrega un nuevo efecto al tope de la pila (LIFO)."""  
        if effect not in self.effects_stack:          # evita duplicados si ya existe ese efecto en la pila
            self.effects_stack.append(effect)         # añade el efecto al final de la lista (tope de la pila)

    def remove_last_effect(self):                     # método para quitar el último efecto apilado (pop LIFO)
        """Quita el último efecto agregado (LIFO).""" 
        if self.effects_stack:                        # si la pila tiene elementos
            return self.effects_stack.pop()           # devuelve y elimina el tope
        return None                                   # si está vacía, devuelve None

    def play_next(self):                              # método que saca la siguiente canción de la cola y la prepara para reproducir
        song = self.dequeue_song()                    # obtiene la siguiente canción (o None)
        if not song:                                  # si no hay canción
            return None                               # devuelve None (no hay reproducción)
        self.current_song = song                      # establece current_song a la canción obtenida
        self.playlist.append(song)                    # añade la canción al historial (playlist)
        self.effects_stack.clear()                    # limpia la pila de efectos al inicio de reproducción
        return song                                   # retorna la canción que se va a reproducir

# ----------------- INTERFAZ GRÁFICA -----------------
class BeatQueueGUI:                                   # clase que construye y controla la interfaz gráfica Tkinter
    def __init__(self, root):                         # constructor que recibe la raíz Tk
        self.root = root                              # guarda la instancia de la ventana raíz en self.root
        self.root.title("🎵 BeatQueue FX - Simulador de DJ")  # establece el título de la ventana
        self.root.geometry("950x520")                 # define tamaño inicial de la ventana (ancho x alto)
        self.root.configure(bg="#1e1e1e")             # configura color de fondo de la ventana raíz

        self.beatqueue = BeatQueue()                  # instancia BeatQueue para manejar cola/efectos/playlist
        self.create_widgets()                         # llama al método que crea y organiza todos los widgets

    def create_widgets(self):                         # método que construye la interfaz (widgets y layout)
        # ---------- Frames ----------
        self.left_frame = tk.Frame(self.root, bg="#252525", width=250)  # frame izquierdo para la cola de canciones
        self.left_frame.pack(side="left", fill="y")    # empaqueta el frame en el lado izquierdo ocupando todo el eje y

        self.center_frame = tk.Frame(self.root, bg="#2e2e2e")  # frame central para controles y reproducción
        self.center_frame.pack(side="left", fill="both", expand=True)  # empaqueta central, se expande al espacio disponible

        self.right_frame = tk.Frame(self.root, bg="#252525", width=250)  # frame derecho para playlist/historial
        self.right_frame.pack(side="right", fill="y")   # empaqueta en el lado derecho ocupando todo el eje y

        # ---------- Cola ----------
        tk.Label(self.left_frame, text="🎶 Cola de canciones", bg="#252525", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
        # etiqueta título de la sección cola, empaquetada con padding vertical

        self.queue_listbox = tk.Listbox(self.left_frame, bg="#303030", fg="white", selectbackground="#4e4e4e")
        # Listbox para mostrar las canciones en la cola con estilo de fondo y color de selección
        self.queue_listbox.pack(fill="both", expand=True, padx=10, pady=5)  # empaqueta la listbox para ocupar el espacio disponible
        tk.Button(self.left_frame, text="➕ Añadir canción", command=self.add_song_window, bg="#007acc", fg="white").pack(pady=5)
        # botón para abrir diálogo de añadir canción; vincula a self.add_song_window

        # ---------- Centro ----------
        self.current_label = tk.Label(self.center_frame, text="🎧 Sin canción en reproducción", bg="#2e2e2e", fg="white", font=("Arial", 14))
        # etiqueta que muestra la canción actual o estado de reproducción
        self.current_label.pack(pady=10)                 # empaqueta la etiqueta con separación vertical

        self.progress = ttk.Progressbar(self.center_frame, length=400, mode="determinate")
        # progressbar para simular avance de la canción (ttk themed)
        self.progress.pack(pady=10)                      # empaqueta la barra de progreso

        self.effects_label = tk.Label(self.center_frame, text="Efectos activos: ninguno", bg="#2e2e2e", fg="#cccccc", font=("Arial", 11))
        # etiqueta que muestra los efectos activos (orden LIFO)
        self.effects_label.pack(pady=10)                 # empaqueta la etiqueta de efectos

        controls_frame = tk.Frame(self.center_frame, bg="#2e2e2e")  # frame contenedor para botones de control
        controls_frame.pack(pady=10)                     # empaqueta el frame de controles con padding

        tk.Button(controls_frame, text="▶ Reproducir siguiente", command=self.play_next_song, bg="#28a745", fg="white").grid(row=0, column=0, padx=5)
        # botón que lanza la reproducción de la siguiente canción; usa grid dentro del controls_frame

        tk.Button(controls_frame, text="🎛️ Efectos", command=self.open_effects_window, bg="#17a2b8", fg="white").grid(row=0, column=1, padx=5)
        # botón que abre la ventana de gestión de efectos (apilar/quitar)

        # ---------- Playlist ----------
        tk.Label(self.right_frame, text="📀 Playlist / Historial", bg="#252525", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
        # etiqueta título de la sección playlist en la parte derecha

        self.playlist_listbox = tk.Listbox(self.right_frame, bg="#303030", fg="white", selectbackground="#4e4e4e")
        # listbox para mostrar el historial de canciones reproducidas
        self.playlist_listbox.pack(fill="both", expand=True, padx=10, pady=5)  # empaqueta la playlist para ocupar el espacio disponible

    # ---------- Funciones ----------
    def add_song_window(self):                          # método que abre diálogos para añadir una nueva canción a la cola
        title = simpledialog.askstring("Nueva canción", "Título:")  # solicita al usuario el título con simpledialog
        if not title:                                   # si el usuario cancela o deja vacío
            return                                      # sale sin hacer nada
        artist = simpledialog.askstring("Artista:", "Nombre del artista:") or "Desconocido"
        # pide nombre del artista; si es None/empty, usa "Desconocido" como valor por defecto
        try:
            duration = int(simpledialog.askstring("Duración", "Duración en segundos:"))  # pide duración y la convierte a int
        except:
            duration = 8                                # si hay error en la conversión, asigna 8 segundos por defecto

        song = Song(title, artist, duration)            # crea instancia de Song con los valores ingresados
        self.beatqueue.enqueue_song(song)                # añade la canción a la cola del BeatQueue
        self.refresh_queue()                             # actualiza la visualización de la cola en la GUI
        messagebox.showinfo("Añadida", f"Se añadió '{song.title}' a la cola.")  # muestra confirmación al usuario

    def refresh_queue(self):                            # método que refresca el Listbox de la cola con el contenido actual
        self.queue_listbox.delete(0, tk.END)            # limpia todos los elementos actuales del listbox
        for song in self.beatqueue.queue:               # itera sobre las canciones en la cola
            self.queue_listbox.insert(tk.END, str(song))  # inserta la representación de cada canción al final del listbox

    def refresh_playlist(self):                         # método que actualiza el Listbox del historial/playlist
        self.playlist_listbox.delete(0, tk.END)         # limpia la listbox del playlist
        for song in self.beatqueue.playlist:            # recorre el historial de canciones reproducidas
            self.playlist_listbox.insert(tk.END, str(song))  # inserta cada elemento en la lista

    def update_effects_label(self):                     # método que actualiza la etiqueta que muestra efectos activos
        if self.beatqueue.effects_stack:                # si hay efectos apilados
            order = " → ".join(reversed(self.beatqueue.effects_stack))  # construye cadena mostrando orden de aplicación (tope primero)
            self.effects_label.config(text=f"Efectos activos (LIFO): {order}")  # actualiza el texto de la etiqueta
        else:
            self.effects_label.config(text="Efectos activos: ninguno")  # si no hay efectos, muestra "ninguno"

    def play_next_song(self):                           # método que inicia la reproducción de la siguiente canción en la cola
        if self.beatqueue.playing:                      # si ya hay reproducción en curso
            messagebox.showwarning("Ocupado", "Ya se está reproduciendo una canción.")  # muestra alerta y no hace nada
            return

        song = self.beatqueue.play_next()               # pide al BeatQueue la siguiente canción para reproducir
        if not song:                                    # si no hay canción disponible
            messagebox.showinfo("Cola vacía", "No hay canciones en la cola.")  # informa al usuario
            return

        self.refresh_queue()                            # actualiza la lista de la cola (removida la canción)
        self.refresh_playlist()                         # actualiza el historial con la canción recién reproducida
        self.update_effects_label()                     # actualiza la etiqueta de efectos (se limpió al reproducir)
        self.current_label.config(text=f"🎧 Reproduciendo: {song.title} — {song.artist}")  # muestra la canción actual
        self.progress["value"] = 0                      # reinicia la barra de progreso a 0

        threading.Thread(target=self.simulate_play, args=(song,), daemon=True).start()
        # crea y lanza un hilo daemon para simular la reproducción (evita bloquear la interfaz principal)

    def simulate_play(self, song):                      # método ejecutado en hilo para simular reproducción temporal
        self.beatqueue.playing = True                   # marca que hay reproducción en curso
        for i in range(song.duration + 1):              # iteración desde 0 hasta duration (inclusive para visual)
            time.sleep(1)                               # duerme 1 segundo por iteración (simula tiempo de reproducción)
            self.progress["value"] = (i / song.duration) * 100  # actualiza el valor de la barra de progreso porcentual
            self.root.update_idletasks()                # fuerza actualización de la GUI para que se vea el progreso
        self.beatqueue.playing = False                  # al terminar, marca que no se está reproduciendo
        self.current_label.config(text="🎧 Canción finalizada")  # actualiza etiqueta indicando fin de reproducción
        self.progress["value"] = 0                      # reinicia la barra de progreso a 0 al finalizar

    # ---------- Ventana de efectos ----------
    def open_effects_window(self):                      # método que abre una ventana Toplevel para gestionar la pila de efectos
        if not self.beatqueue.current_song:             # si no hay canción en current_song (no comenzó reproducción)
            messagebox.showinfo("Sin canción", "Reproduce una canción primero.")  # informa que debe reproducir primero
            return

        win = Toplevel(self.root)                       # crea una nueva ventana hija (Toplevel) asociada a la raíz
        win.title("🎚️ Pila de efectos (LIFO)")          # asigna título a la ventana de efectos
        win.geometry("320x300")                         # define tamaño para la ventana de efectos
        win.configure(bg="#2e2e2e")                     # configura color de fondo de la ventana

        win.grab_set()                                  # establece grab (modal): evita interacción con la ventana raíz mientras está abierta

        tk.Label(win, text="Apila o quita efectos (LIFO):", bg="#2e2e2e", fg="white", font=("Arial", 11, "bold")).pack(pady=5)
        # etiqueta instructiva en la ventana de efectos

        # Dropdown para elegir efecto
        selected_effect = tk.StringVar(value=self.beatqueue.available_effects[0])
        # variable ligada al combobox que almacenará el efecto seleccionado; por defecto primer efecto disponible

        ttk.Combobox(win, textvariable=selected_effect, values=self.beatqueue.available_effects, state="readonly").pack(pady=5)
        # combobox readonly que muestra las opciones de efectos y actualiza selected_effect al cambiar

        # Botones
        tk.Button(win, text="➕ Apilar efecto", bg="#007acc", fg="white",
                  command=lambda: self.add_effect_gui(selected_effect.get())).pack(pady=5)
        # botón que apila el efecto seleccionado; usa lambda para pasar el valor actual del combobox a add_effect_gui

        tk.Button(win, text="➖ Quitar último efecto", bg="#dc3545", fg="white",
                  command=self.remove_last_effect_gui).pack(pady=5)
        # botón que ejecuta la función para quitar (pop) el último efecto en la pila

        self.effects_list = tk.Listbox(win, bg="#303030", fg="white")  # listbox dentro de la ventana para mostrar la pila de efectos
        self.effects_list.pack(fill="both", expand=True, padx=10, pady=10)  # empaqueta la listbox para llenar la ventana
        self.refresh_effects_list(win)                    # rellena la listbox con los efectos actualmente en la pila

    def add_effect_gui(self, effect):                    # método que añade un efecto desde la GUI a la pila del BeatQueue
        self.beatqueue.add_effect(effect)                 # delega en BeatQueue.add_effect para añadir el efecto
        self.update_effects_label()                       # actualiza la etiqueta de efectos en la ventana principal
        self.refresh_effects_list()                       # actualiza la listbox de efectos (en la ventana de efectos) si existe

    def remove_last_effect_gui(self):                    # método que quita el último efecto desde la GUI
        removed = self.beatqueue.remove_last_effect()    # llama a BeatQueue.remove_last_effect y recibe el efecto removido o None
        if removed:                                      # si se removió un efecto
            self.update_effects_label()                  # actualiza etiqueta de efectos en la ventana principal
            self.refresh_effects_list()                  # refresca la listbox de la ventana de efectos
        else:
            messagebox.showinfo("Vacío", "No hay efectos en la pila.")  # si no había efectos, informa al usuario

    def refresh_effects_list(self, win=None):            # método que refresca la listbox de efectos (muestra orden LIFO)
        # Encuentra la listbox actual
        lb = self.effects_list if hasattr(self, "effects_list") else None
        # obtiene referencia a self.effects_list solo si existe (evita errores si se llama desde otro contexto)
        if not lb:                                       # si no existe la listbox (no está la ventana abierta)
            return                                       # sale sin hacer nada
        lb.delete(0, tk.END)                             # limpia todos los elementos actuales de la listbox
        for i, effect in enumerate(reversed(self.beatqueue.effects_stack)):  # recorre la pila invertida (tope primero)
            lb.insert(tk.END, f"{i+1}º: {effect}")       # inserta cada efecto con su índice ordinal (1º, 2º, ...)

# ----------------- EJECUCIÓN -----------------
if __name__ == "__main__":                              # punto de entrada: si se ejecuta el script directamente
    root = tk.Tk()                                      # crea la ventana raíz de la aplicación (Tk)
    app = BeatQueueGUI(root)                            # instancia la GUI pasando la raíz para construir widgets
    root.mainloop()                                     # inicia el bucle principal de eventos de Tkinter (mantiene la app activa)
