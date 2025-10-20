# Estructuras de Datos en BeatQueue

## 1. Cola (FIFO)
**Clase:** `PlaylistQueue`  
**Implementación:** `collections.deque`  
**Uso:** Manejar el orden de reproducción de canciones.  
**Métodos:** 
- `enqueue(song)`: agrega una canción al final.
- `dequeue()`: reproduce y elimina la primera.

**Motivo:** La reproducción sigue un orden de llegada (primero en entrar, primero en salir).

---

## 2. Pila (LIFO)
**Atributo:** `self.effects_stack`  
**Tipo:** lista nativa de Python (`list`)  
**Uso:** Aplicar y deshacer efectos de sonido en orden inverso.  
**Métodos:** 
- `add_effect(effect)`
- `remove_last_effect()`

**Motivo:** los efectos se aplican en orden inverso (último en entrar, primero en salir).

---

## 3. Arreglo dinámico
**Atributo:** `self.songs`  
**Tipo:** `list`  
**Uso:** Almacenar todas las canciones disponibles.  
**Motivo:** permite acceso rápido y tamaño variable, ideal para la lista de canciones.
