import subprocess
import time
import argparse
import logging
# Variables para almacenar los subprocesos en ejecución
processes = []

def ejecutar_script1():
    logging.info("Ejecutando script páginas...")
    process = subprocess.Popen(["python", "scrape_perfil_ig.py"])
    processes.append(process)
    process.wait()  # Espera a que el primer script termine antes de continuar

def ejecutar_script2():
    logging.info("Ejecutando script obtener imágenes...")
    process = subprocess.Popen(["python", "process_image.py"])
    processes.append(process)
    process.wait()  # Espera a que el segundo script termine antes de continuar

def ejecutar_script3():
    logging.info("Ejecutando script obtener videos...")
    process = subprocess.Popen(["python", "process_video_1.py"])
    processes.append(process)
    process.wait()  # Espera a que el tercer script termine antes de continuar

def ejecutar_script4():
    logging.info("Ejecutando script obtener videos...")
    process = subprocess.Popen(["python", "process_video2.py"])
    processes.append(process)
    process.wait()

def ejecutar_script5():
    logging.info("Ejecutando script obtener de temas y busqueda...")
    process = subprocess.Popen(["python", "scrape_topic_ig.py"])
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
            logging.info("Cancelando script...")
            process.terminate()
    processes.clear()  # Limpia la lista de procesos
def configurar_logger():
        # Configuración básica del logger
        logging.basicConfig(filename='Logs_Scraper_Main_Instagram.log',  # Archivo donde se guardarán los logs
                            level=logging.INFO,     # Nivel de registro, en este caso errores
                            format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del log
                            datefmt='%Y-%m-%d %H:%M:%S')  # Formato de la fecha y hora  
# Función principal para parsear los argumentos y ejecutar los scripts
def main():
    # Crear el parser para los argumentos
    configurar_logger()
    parser = argparse.ArgumentParser(description="Ejecutar scripts específicos.")
    parser.add_argument('--funcion_ejecutar', choices=['perfil', 'busqueda', 'all'],
                        help="Función que deseas ejecutar", required=True)
    args = parser.parse_args()

    # Ejecutar según el valor del argumento
    if args.funcion_ejecutar == 'perfil':
        ejecutar_scripts_perfil()
        logging.info("Scripts perfil ejecutados.")
    elif args.funcion_ejecutar == 'busqueda':
        ejecutar_scripts_buqueda()
        logging.info("Scripts búsqueda ejecutados.")
    elif args.funcion_ejecutar == 'all':
        ejecutar_all_scripts()
        logging.info("Todos los scripts ejecutados.")

# Ejecutar el script principal
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.error("Cancelando todos los scripts...")
        cancelar_todos_los_scripts()
