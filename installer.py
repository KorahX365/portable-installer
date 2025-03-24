import os
import shutil
import psutil
import winshell
from win32com.client import Dispatch
import difflib
import subprocess


# Obtener la carpeta actual (donde se ejecuta el script)
origen = os.path.abspath(os.getcwd())

# Obtener el nombre de la carpeta actual para usarlo por defecto
nombre_default = os.path.basename(origen)

# Ruta del archivo de log
log_file = os.path.join(origen, "log.txt")

# Función para escribir en el log
def escribir_log(mensaje):
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"{mensaje}\n")

# Ruta del archivo de configuración en AppData (Roaming)
config_dir = os.path.join(os.getenv('APPDATA'), 'disk_types.txt')

# Función para cargar la configuración de discos desde el archivo de texto
def cargar_configuracion():
    config = {}
    if os.path.exists(config_dir):
        with open(config_dir, "r", encoding="utf-8") as archivo_config:
            for linea in archivo_config:
                letra, tipo = linea.strip().split(":")
                config[letra] = tipo
    return config

# Función para guardar la configuración de discos en un archivo de texto
def guardar_configuracion(config):
    with open(config_dir, "w", encoding="utf-8") as archivo_config:
        for letra, tipo in config.items():
            archivo_config.write(f"{letra}:{tipo}\n")

# Iniciar el log
escribir_log("Inicio del proceso de copia")

# Calcular el tamaño total de la carpeta a copiar
def calcular_tamano_carpeta(carpeta):
    total = 0
    for dirpath, dirnames, filenames in os.walk(carpeta):
        for filename in filenames:
            archivo = os.path.join(dirpath, filename)
            total += os.path.getsize(archivo)
    return total // (1024**3)  # Convertir de bytes a GB

tamano_carpeta = calcular_tamano_carpeta(origen)

# Mostrar la lista de discos disponibles y filtrar por espacio suficiente
discos = psutil.disk_partitions()
print("Discos disponibles (con espacio suficiente):")
configuracion = cargar_configuracion()

# Almacenar los discos SSD y HDD por separado
discos_ssd = []
discos_hdd = []

for i, disco in enumerate(discos):
    if disco.fstype != '':  # Solo mostrar discos con un sistema de archivos
        info_disco = psutil.disk_usage(disco.mountpoint)
        espacio_libre = info_disco.free // (1024**3)  # Espacio libre en GB
        espacio_total = info_disco.total // (1024**3)  # Espacio total en GB
        
        letra = disco.device[0]
        tipo_disco = configuracion.get(letra, "Desconocido")
        
        if espacio_libre >= tamano_carpeta:
            print(f"{i + 1}. {disco.device} - {espacio_libre}GB libres / {espacio_total}GB totales ({tipo_disco})")
            
            if tipo_disco == "SSD":
                discos_ssd.append((disco.device, espacio_libre))
            elif tipo_disco == "HDD":
                discos_hdd.append((disco.device, espacio_libre))

# Preguntar al usuario por el tipo de disco preferido o manual
tipo_preferido = input("¿Prefieres un SSD (1), un HDD (2) o seleccionar manualmente (3)? ").strip()
while tipo_preferido not in ["1", "2", "3"]:
    tipo_preferido = input("Selección inválida. Introduce 1 para SSD, 2 para HDD o 3 para manual: ").strip()

if tipo_preferido == "1":
    discos_disponibles = discos_ssd
elif tipo_preferido == "2":
    discos_disponibles = discos_hdd
else:  # Opción manual
    discos_disponibles = [disco.device for disco in discos]
    print("Discos disponibles:")
    for i, disco in enumerate(discos_disponibles, start=1):
        print(f"{i}. {disco}")
    seleccion_manual = input("Selecciona el número del disco manualmente: ").strip()
    while not seleccion_manual.isdigit() or int(seleccion_manual) < 1 or int(seleccion_manual) > len(discos_disponibles):
        seleccion_manual = input("Selección inválida. Introduce un número válido: ").strip()
    letra_disco = discos_disponibles[int(seleccion_manual) - 1]
    print(f"Disco seleccionado: {letra_disco}")
    escribir_log(f"Letra del disco de destino: {letra_disco}")
    letra_disco = letra_disco[0]  # Solo la letra del disco
    discos_disponibles = [(letra_disco, 0)]  # Se usa una lista de tuplas vacías

if discos_disponibles:
    disco_seleccionado = max(discos_disponibles, key=lambda x: x[1] if isinstance(x, tuple) else 0)
    if isinstance(disco_seleccionado, tuple):
        letra_disco = disco_seleccionado[0]
    print(f"\nSe seleccionó el disco con más espacio libre: {letra_disco}")
else:
    print(f"No se encontraron discos {('SSD' if tipo_preferido == '1' else 'HDD')} con suficiente espacio.")
    letra_disco = input(f"Introduce la letra del disco de destino (tiene que tener al menos {tamano_carpeta}GB libres): ").strip()

# Obtener la ruta predeterminada
ruta_predeterminada = f"{letra_disco}:\Games"
nueva_ubicacion = input(f"Ubicación de destino [{ruta_predeterminada}]: ").strip()
if not nueva_ubicacion:
    nueva_ubicacion = ruta_predeterminada
escribir_log(f"Ubicación de destino: {nueva_ubicacion}")

# Preguntar el nuevo nombre de la carpeta
nuevo_nombre = input(f"Introduce el nombre de la nueva carpeta [{nombre_default}]: ").strip()
if not nuevo_nombre:
    nuevo_nombre = nombre_default
escribir_log(f"Nombre de la nueva carpeta: {nuevo_nombre}")

# Ruta final de destino
destino = os.path.join(nueva_ubicacion, nuevo_nombre)

# Copiar la carpeta
try:
    shutil.copytree(origen, destino)
    escribir_log(f"Copia completada: {destino}")
    print(f"\nCopia completada: {destino}")
except Exception as e:
    escribir_log(f"Error al copiar: {e}")
    print(f"\nError al copiar: {e}")

# Buscar archivos .exe en la raíz del proyecto
archivos_exe = [f for f in os.listdir(origen) if f.endswith(".exe")]

# Crear el acceso directo
if archivos_exe:
    if len(archivos_exe) == 1:
        exe_seleccionado = archivos_exe[0]
    else:
        print("\nSe encontraron múltiples archivos .exe en la raíz del proyecto:")
        for i, exe in enumerate(archivos_exe, start=1):
            print(f"{i}. {exe}")
        seleccion = input("Elige el número del .exe para crear el acceso directo o presiona Enter para seleccionar automáticamente: ").strip()
        
        if not seleccion:
            # Si no se selecciona ninguno, se elige el que más coincida con el nombre de la carpeta
            coincidencias = [exe for exe in archivos_exe]
            exe_seleccionado = difflib.get_close_matches(nombre_default, coincidencias, n=1)
            if exe_seleccionado:
                exe_seleccionado = exe_seleccionado[0]
            else:
                exe_seleccionado = archivos_exe[0]  # Fallback en caso de que no haya coincidencias
        
        else:
            while not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(archivos_exe):
                seleccion = input("Selección inválida. Introduce un número válido: ").strip()
            
            exe_seleccionado = archivos_exe[int(seleccion) - 1]

    exe_origen = os.path.join(destino, exe_seleccionado)
    if not os.path.exists(exe_origen):
        escribir_log(f"El archivo .exe no existe en la ubicación: {exe_origen}")
        print(f"\nError: El archivo .exe no se encontró en la ubicación: {exe_origen}")
    else:
        acceso_directo = os.path.join(winshell.desktop(), f"{nuevo_nombre}.lnk")

        try:
            # Intentar crear el acceso directo
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(acceso_directo)
            shortcut.TargetPath = exe_origen
            shortcut.WorkingDirectory = destino
            shortcut.IconLocation = exe_origen  # También puedes especificar un icono
            shortcut.Save()

            escribir_log(f"Acceso directo creado: {acceso_directo}")
            print(f"\nAcceso directo creado en el escritorio: {acceso_directo}")
        except Exception as e:
            escribir_log(f"Error al crear acceso directo: {e}")
            print(f"\nError al crear acceso directo: {e}")

else:
    print("\nNo se encontraron archivos .exe en la raíz del proyecto.")
    escribir_log("No se encontraron archivos .exe en la raíz del proyecto.")