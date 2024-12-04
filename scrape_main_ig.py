import subprocess
import time
import argparse

# Variables para almacenar los subprocesos en ejecución
processes = []

def ejecutar_script1():
    print("Ejecutando script páginas...")
    process = subprocess.Popen(["python", "scrape_perfil_ig.py"])
    processes.append(process)
    process.wait()  # Espera a que el primer script termine antes de continuar

def ejecutar_script2():
    print("Ejecutando script obtener imágenes...")
    process = subprocess.Popen(["python", "process_image.py"])
    processes.append(process)
    process.wait()  # Espera a que el segundo script termine antes de continuar

def ejecutar_script3():
    print("Ejecutando script obtener videos...")
    process = subprocess.Popen(["python", "process_video1.py"])
    processes.append(process)
    process.wait()  # Espera a que el tercer script termine antes de continuar

def ejecutar_script4():
    print("Ejecutando script obtener videos...")
    process = subprocess.Popen(["python", "process_video2.py"])
    processes.append(process)
    process.wait()

def ejecutar_script5():
    print("Ejecutando script obtener de temas y busqueda...")
    process = subprocess.Popen(["python", "scrape_topicl_ig.py"])
    processes.append(process)
    process.wait()

# Funciones para ejecutar los diferentes conjuntos de scripts
def ejecutar_scripts_perfil():
    ejecutar_script1()  # Ejecuta y espera a que termine el script 1
    ejecutar_script2()  # Ejecuta y espera a que termine el script 2
    ejecutar_script3()  # Ejecuta y espera a que termine el script 3

def ejecutar_scripts_buqueda():
    ejecutar_script5()  # Ejecuta y espera a que termine el script 1
    ejecutar_script2()  # Ejecuta y espera a que termine el script 2
    ejecutar_script4()  # Ejecuta y espera a que termine el script 3

def ejecutar_all_scripts():
    ejecutar_script1()  # Ejecuta y espera a que termine el script 1
    time.sleep(2)  # Pausa de 2 segundos entre scripts
    ejecutar_script5()  # Ejecuta el script de tópicos
    ejecutar_script2()  # Ejecuta y espera a que termine el script 2
    ejecutar_script3()  # Ejecuta y espera a que termine el script 3

# Función para cancelar todos los scripts en ejecución
def cancelar_todos_los_scripts():
    for process in processes:
        if process.poll() is None:  # Verifica si el proceso sigue en ejecución
            print("Cancelando script...")
            process.terminate()
    processes.clear()  # Limpia la lista de procesos

# Función principal para parsear los argumentos y ejecutar los scripts
def main():
    # Crear el parser para los argumentos
    parser = argparse.ArgumentParser(description="Ejecutar scripts específicos.")
    parser.add_argument('--funcion_ejecutar', choices=['perfil', 'busqueda', 'all'],
                        help="Función que deseas ejecutar", required=True)
    args = parser.parse_args()

    # Ejecutar según el valor del argumento
    if args.funcion_ejecutar == 'perfil':
        ejecutar_scripts_perfil()
        print("Scripts perfil ejecutados.")
    elif args.funcion_ejecutar == 'busqueda':
        ejecutar_scripts_buqueda()
        print("Scripts búsqueda ejecutados.")
    elif args.funcion_ejecutar == 'all':
        ejecutar_all_scripts()
        print("Todos los scripts ejecutados.")

# Ejecutar el script principal
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelando todos los scripts...")
        cancelar_todos_los_scripts()
