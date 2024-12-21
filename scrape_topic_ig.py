from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,WebDriverException,TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import configparser
import random
from selenium.webdriver.common.by import By
import psycopg2
import logging
from db_connection_IG import DatabaseConnection

class Scraper_Ig():
    def __init__(self):
        #brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        #chrome_driver_path = r"C:\path\to\chromedriver.exe"
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Activar modo headless
        #chrome_options.add_argument("--disable-gpu")  # Opcional: mejora en algunos entornos
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-notifications")
        

        #chrome_options.binary_location = brave_path
        #chrome_options.add_argument('--disable-dev-shm-usage')
        #service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(options= chrome_options)
        self.driver.maximize_window()
        self.config = configparser.ConfigParser()
        self.config.read('credentials.conf')
        self.credentials = self._get_credentials()
        #self.email = self.config.get('DEFAULT','emailkey')
        #self.username = self.config.get('DEFAULT','usernamekey')
        #self.password = self.config.get('DEFAULT','passwordkey')
        self.selectors = [
                    "div.x1qjc9v5.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1lliihq.xdt5ytf.x2lah0s.x1a7h2tk.x14miiyz.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x11njtxf.xph46j.x9i3mqj.xcghwft.x1bzgcud.xgczaz5.x1rzo0p5.x1guec7k",
                    "div.x1qjc9v5.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1lliihq.xdt5ytf.x2lah0s.xrbpyxo.x1a7h2tk.x14miiyz.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x11njtxf.x1bfs520.xph46j.x9i3mqj.xcghwft.x1bzgcud.xhdunbi"
                    ]
        self.selectors_close_modal =['div.x160vmok.x10l6tqk.x1eu8d0j.x1vjfegm > div[role="button"]','button[data-e2e="browse-close"]']
        self.conexion = DatabaseConnection()
        self.conexion.crear_conexion()  
    def _get_credentials(self):
        credentials = []
        # Filtrar las claves que contienen pares coincidentes de username y password
        for key in self.config['DEFAULT']:
            if key.startswith('usernamekey'):
                num = key.replace('usernamekey', '')
                email = self.config.get('DEFAULT', f'emailkey{num}')
                #username = self.config.get('DEFAULT', f'usernamekey{num}')
                password = self.config.get('DEFAULT', f'passwordkey{num}')
                credentials.append((email, password))
        return credentials
    def random_time(self,min_seconds, max_seconds):
        time.sleep(random.uniform(min_seconds, max_seconds))
    def insert_text(self,text,input_element):
        try:
            for char in text:
                input_element.send_keys(char)
                self.random_time(0.05,0.25)  
        except Exception as e:
             logging.error(f"Error en ingresar texto con dealy  {e}")    
    def post_relacionado(self,driver,topic,j):
        try:
            post_contenido= WebDriverWait(driver, 15).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.x78zum5.xdt5ytf.x67bb7w.x1n2onr6.xvbhtw8.x5yr21d.x168nmei.x1yr5g0i.xrt01vj.xo71vjh")))
            post_contenido = post_contenido.text   
            #logging.info(f"post contenido total:  {post_contenido}")
            topic = topic.replace('#', '')
            if topic not in post_contenido:
                    j += 1;
                    logging.info(f"Contador {j} publicaciones sin el contenido del topic {topic} ")
            return j 
        except Exception as e:
            logging.error(f"Error en obterner la relacionde posts {e}")   
    def login(self):
        max_attempts = len(self.credentials)
        attempt = 0
        failed_credentials = set()  # Conjunto para almacenar credenciales fallidas

        while attempt < max_attempts and self.credentials:
            # Elegir credenciales que no estén en el conjunto de fallidas
            email, password = random.choice(self.credentials)
            if (email, password) in failed_credentials:
                continue  # Saltar credenciales fallidas

            logging.info(f"Iniciando sesión con el usuario: {email} (Intento {attempt + 1}/{max_attempts})")

            try:
                time.sleep(1)
                target_url = 'https://www.instagram.com/accounts/login/'
                self.driver.get(target_url)
                self.random_time(0.5,2)
                try:
                    # Introducir email
                    email_text_in_input = WebDriverWait(self.driver, 15).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.xdj266r.x1m39q7l.xzueoph.x540dpk:nth-of-type(1) label._aa48> span"))
                    ).text
                    if "correo electrónico" in email_text_in_input.lower():
                        email_input = WebDriverWait(self.driver, 15).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
                        )
                        self.insert_text(email,email_input)
                except Exception as e:
                     logging.error(f"Error al ubicar input de email") 
                try:
                # Introducir contraseña
                    password_text_in_input = WebDriverWait(self.driver, 15).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.xdj266r.x1m39q7l.xzueoph.x540dpk:nth-of-type(2) label._aa48> span"))
                    ).text
                    time.sleep(1)
                    if "contraseña" in password_text_in_input.lower():
                        password_input = WebDriverWait(self.driver, 15).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
                        )
                        
                        self.insert_text(password,password_input)
                except Exception as e:
                    logging.error(f"Error al ubicar input de email")    

                # Click en el botón de inicio de sesión
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[class=' _acan _acap _acas _aj1- _ap30']")
                login_button.click()
                self.random_time(1,3)

                # Verificar errores de inicio de sesión
                try:
                    error_message = WebDriverWait(self.driver, 8).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "form >span >div"))
                    ).text
                    if "La contraseña no es correcta. Compruébala." in error_message:
                        logging.warning("Credenciales incorrectas.")
                        failed_credentials.add((email, password))  # Añadir a credenciales fallidas
                        continue
                except Exception:
                    pass

                if "login_attempt" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                    logging.warning("Inicio de sesión fallido. Puede ser un perfil bloqueado.")
                    failed_credentials.add((email, password))  # Añadir a credenciales fallidas
                    continue

                logging.info(f"Sesión iniciada con éxito con el usuario: {email}")
                return True

            except Exception as e:
                logging.error(f"Error en el intento {attempt + 1}: {e}")
                failed_credentials.add((email, password))  # Añadir a credenciales fallidas

            attempt += 1

        logging.error("No se pudo iniciar sesión con ninguna credencial.")
        return False
    def configurar_logger(self):
        # Configuración básica del logger
        logging.basicConfig(filename='Logs_Scraper_Busqueda_Instagram.log',  # Archivo donde se guardarán los logs
                            level=logging.INFO,     # Nivel de registro, en este caso errores
                            format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del log
                            datefmt='%Y-%m-%d %H:%M:%S')  # Formato de la fecha y hora  
    def obtener_comentario(self,driver):
        try:
                self.random_time(0.5,2)
                feed_coments = driver.find_element(By.CSS_SELECTOR, "ul._a9z6._a9za >div> div> div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1")
                return feed_coments.find_elements(By.CSS_SELECTOR, "div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1yztbdb.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1")
            
        except NoSuchElementException as e:
                logging.error(f"No presenta comentarios")
        except Exception as e:
                logging.error(f"Unexpected error in obtener_posts: {e}" )
        return []
      
    def obtener_imagen(self,driver):
        try:
                self.random_time(0.5,2)
                feed_pictures = driver.find_element(By.CSS_SELECTOR, "div.x1lliihq.x1n2onr6 ul._acay")
                return feed_pictures.find_elements(By.CSS_SELECTOR, "li._acaz")
            
        except NoSuchElementException as e:
                logging.error(f"Error: Could not locate the 'feed_pictures' or 'subelelementos imagen' elements. : {e}")
        except Exception as e:
                logging.error(f"Unexpected error in obtener_pictures: {e}" )
        return []
    def obtener_video(self,enlace,publicacion_id):
         try:
                with self.conexion.connection.cursor() as cursor:
                    consulta_verificacion = "SELECT id FROM video WHERE url = %s AND publicacion_id =%s"
                    cursor.execute(consulta_verificacion, (enlace,publicacion_id))
                    resultado = cursor.fetchone()
                    
                    if resultado is None and enlace is not None:
                            consulta = "INSERT INTO video (url, publicacion_id) VALUES (%s, %s) "
                            cursor.execute(consulta, (enlace,publicacion_id))
                            self.conexion.connection.commit() 
                            logging.info("Comentario video insertado con éxitos")
                    else:
                        logging.info(f"El id repetido en videos es: {resultado}")
                        logging.info("NO SE INSERTO VIDEO ELEMENTO REPETIDO")        
         except psycopg2.Error as e:
                        logging.error(f"Error en la base de datos con la tabla videos: {e}")
         except Exception as e:
                        logging.error(f"Algo está pasando conn el video insertado: {e}")
    def obtener_comentarios(self,driver,publicacion_id):
        try:
                #obtener por hora publicada
                event=True
                comentarios_vistos = set()
                time.sleep(1)
                # Obtén la nueva URL actual
                url_actual = driver.current_url
                contador_repeticiones = 0 
                contador_comentarios_repetidos = 0
                longitud_anterior = -1 
                while event: 
                # Llama al siguiente método
                    try:
                        coments= self.obtener_comentario(driver)
                        ul_element = driver.find_element(By.CSS_SELECTOR, 'ul._a9z6._a9za')
                        # Desplaza el ul hacia abajo (simulando el scroll al final)
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", ul_element)
                        # Simula que el cursor está sobre el ul (esto activa interacciones como el scroll)
                        actions = ActionChains(driver)
                        actions.move_to_element(ul_element).perform()
                    except Exception as e:
                        logging.info(f"No contiene comentarios")
                        pass
                    longitud_actual = len(coments)
                    if longitud_actual == longitud_anterior:
                        contador_repeticiones += 1  # Incrementa el contador si es igual
                    else:
                        contador_repeticiones = 0  # Reinicia el contador si no es igual
                    # Actualiza la longitud anterior con la longitud actual
                    longitud_anterior = longitud_actual
                    # Si la longitud se ha repetido 20 veces, cambia event a False
                    if contador_repeticiones >= 3:
                        logging.info("La longitud de comentarios se ha repetido 3 veces. Terminando la extracción de comentarios del post actual.")
                        event = False  # Termina el bucle
                        pass
                    try:
                            i=0
                            logging.info(f"cantidad de comentarios {len(coments)}")
                            for coment in coments:
                                contenido_coment=coment.text
                                if contenido_coment not in comentarios_vistos:  # Verifica si el texto ya fue procesado
                                    comentarios_vistos.add(contenido_coment)
                                    logging.info("Estamos en el iterador" , i)
                                    user_coment= coment.find_element(By.CSS_SELECTOR, 'h3 span')
                                    usuario= user_coment.text
                                    user_ref = user_coment.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                                    logging.info(f"usuario comentador:  {usuario}")
                                    logging.info(f"user ref: {user_ref}")
                                    try:
                                        descripcion_comentario= coment.find_element(By.CSS_SELECTOR, 'div._a9zs span').text
                                        logging.info(f"comentario {descripcion_comentario}")
                                    except:
                                        logging.info("no tiene un comentario")
                                    try:
                                        fecha= WebDriverWait(coment, 10).until(
                                                EC.element_to_be_clickable(By.CSS_SELECTOR,"span time"))
                                        fecha=fecha.get_attribute('datetime')
                                        logging.info("Fecha de comentario")
                                    except:
                                        logging.info("Error dentro de obenter fecha")
                                        pass     
                                    try:  
                                        with self.conexion.connection.cursor() as cursor:
                                            consulta_verificacion = "SELECT id FROM comentario WHERE usuario = %s AND descripcion_comentario = %s AND  publicacion_id= %s"
                                            cursor.execute(consulta_verificacion, (usuario, descripcion_comentario,publicacion_id ))
                                            resultado = cursor.fetchone()
                                            if(resultado == None):
                                                consulta = "INSERT INTO comentario (publicacion_id,fecha ,enlace_usuario, usuario,descripcion_comentario) VALUES (%s,%s,%s, %s,%s) RETURNING id"
                                                cursor.execute(consulta, (publicacion_id,fecha,user_ref,usuario, descripcion_comentario))
                                                self.conexion.connection.commit()
                                                comentario_id = cursor.fetchone()[0]
                                                logging.info(f"Comentario insertada con éxito.")
                                            else:
                                                logging.info("comentario ya doble y repetido,no ingestado a la db")
                                                contador_comentarios_repetidos += 1   
                                                if(contador_comentarios_repetidos >= 4):
                                                    logging.info("Se reptitio mas de 4 comentarios , obviamos los demas comentarios")
                                                    event=False 
                                                                    
                                    except psycopg2.Error as e:
                                                logging.error(f"Error en la base de datos con la comentario  {e}" )
                                    except Exception as e:
                                                logging.error(f"algo esta mal con la insercion del comentario") 
                                i +=1;
                                
                    except Exception as e:
                        logging.error (f"Error en el desarrollo del bucle {e}")
                        pass       
                    try:
                        more_comment_button = driver.find_element(By.CSS_SELECTOR, 'li button._abl-')
                        more_comment_button.click()
                        pass
                    except: 
                        logging.info("No se cargo mas comentarios")     
        except Exception as e:
            logging.error("Ocurrio un error obtiendo lo comentarios probablemente dentro del bucle")
            pass
    def obtener_imagenes(self,driver,publicacion_id):
        imagenes_vistas = set()
        event =True  
        contador_repeticiones = 0  # Contador para verificar repeticiones
        longitud_anterior = -1 
        while event:
            i =0
            imagenes=self.obtener_imagen(driver)
            longitud_actual = len(imagenes)
            logging.info(f'Cantidad total de imagenes: {longitud_actual}')
            if longitud_actual == longitud_anterior:
                contador_repeticiones += 1  # Incrementa el contador si es igual
            else:
                contador_repeticiones = 0  # Reinicia el contador si no es igual
            # Actualiza la longitud anterior con la longitud actual
            longitud_anterior = longitud_actual
            # Si la longitud se ha repetido 20 veces, cambia event a False
            if contador_repeticiones >= 3:
                logging.info("La longitud de divs se ha repetido 3 veces. Terminando la extracción.")
                event = False  # Termina el bucle
            for imagen in imagenes:
                logging.info(f"Estamos en el iterador de imagenes {i}")
                try:
                    img= imagen.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    if img not in imagenes_vistas:  # Verifica si el texto ya fue procesado
                        imagenes_vistas.add(img)
                        logging.info(f"Imagen enlace: {img}" )
                        try:    
                            with self.conexion.connection.cursor() as cursor:
                                # Extraer la parte fija de la URL ingresada
                                fixed_url = img.split('?')[0]

                                # Extensiones posibles para las imágenes
                                valid_extensions = ['.webp', '.png', '.svg', '.jpg', '.jpeg']

                                # Verificar si la URL tiene alguna de las extensiones válidas
                                for ext in valid_extensions:
                                    if ext in fixed_url:
                                        # Verificar si existe una URL con la misma parte fija
                                        consulta_verificacion = """
                                            SELECT id FROM imagen 
                                            WHERE LEFT(url, POSITION(%s IN url) + LENGTH(%s) - 1) = %s
                                        """
                                        cursor.execute(consulta_verificacion, (ext, ext, fixed_url))
                                        resultado = cursor.fetchone()

                                        if resultado is None:
                                            # Insertar si no existe
                                            consulta = "INSERT INTO imagen (url, publicacion_id) VALUES (%s, %s)"
                                            cursor.execute(consulta, (img, publicacion_id))  # Aquí se almacena la URL completa
                                            self.conexion.connection.commit()  # Confirmar la transacción
                                            logging.info(f"Imagen insertada con éxito: {publicacion_id}")
                                        else:
                                            # Imagen duplicada detectada
                                            logging.info(f"Imagen duplicada detectada. ID existente pertenece a publicacion con id: {publicacion_id}")
                                        break  # Salir del bucle una vez que se haya procesado la extensión
                        except psycopg2.Error as e:
                            logging.error(f"Error en la base de datos Imagenes con la publicación con id: {publicacion_id} en el grupo: {e}")
                        except Exception as e:
                            logging.error(f"Algo está pasando con esto Imagenes: {e}")
                except Exception as e :
                     logging.info(f"Pasando ala siguiente imagen")                        
                i+=1;            
                try: 
                    button_to_next_img= driver.find_element(By.CSS_SELECTOR,"div.x1lliihq.x1n2onr6 div button[aria-label='Siguiente']")
                    button_to_next_img.click()
                    self.random_time(0.5,2)
                except:
                    logging.info("no hay mas inagenes") 
    def scroll_hasta_el_final_post(self,driver,min_scroll,max_scroll,min_s,max_s):
        scroll_distance = random.randint(min_scroll, max_scroll)  # Randomize scroll distance
        #logging.info("La distnacia movida en post fue o es :" , scroll_distance)
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        target_scroll_position = current_scroll_position + scroll_distance
        driver.execute_script(f"window.scrollTo(0, {target_scroll_position});")
        time.sleep(random.uniform(min_s, max_s))  # Randomize delay to mimic human behavior       
    def obtener_posts(self,driver):
        try:
            self.random_time(1.5,2)
            feed_div = driver.find_element(By.CSS_SELECTOR, "main > div > div:nth-of-type(2)> div")
            return feed_div.find_elements(By.CSS_SELECTOR, "div.x9f619.xjbqb8w.x1lliihq.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1n2onr6.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1")
          
        except NoSuchElementException as e:
            logging.error(f"Error: Could not locate the 'feed_div' or 'subelelementos' elements. : {e}")
        except Exception as e:
            logging.error(f"Unexpected error in obtener_posts: {e}" )
        return []
    def obtener_enlaces_busqueda(self, driver):
        try:
            self.random_time(1.5, 2)
            feed_div = driver.find_element(By.CSS_SELECTOR, "div.x78zum5.xdt5ytf.x5yr21d >div>div.x9f619.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.xh8yej3.xocp1fn")
            enlaces = feed_div.find_elements(By.CSS_SELECTOR, "a[role='link']")
            if not enlaces:
                logging.warning("No se encontraron enlaces en 'feed_div'.")
                print("imprimiendo error",enlaces)
            return enlaces
        except NoSuchElementException as e:
            logging.error(f"Error: No se pudo localizar 'feed_div' o sus elementos. : {e}")
        except Exception as e:
            logging.error(f"Error inesperado en obtener_enlaces_busqueda: {e}")
        return []
    def extraer_data(self,driver,topic):
        try:
            elementos_vistos = set()
            event =True  
            j=0
            contador_repeticiones = 0  # Contador para verificar repeticiones
            longitud_anterior = -1  # Inicializamos en -1 para que sea diferente de la primera longitud
            try:
                while event:  # Bucle infinito hasta que se detenga manualmente
                    try:
                        self.scroll_hasta_el_final_post(driver,300,400,0,1.5)
                        divs = self.obtener_posts(driver)  # Obtiene los elementos actuales
                        i =0
                        longitud_actual = len(divs)
                        logging.info(f'Cantidad total de divs: {longitud_actual}')
                        if longitud_actual == longitud_anterior:
                            contador_repeticiones += 1  # Incrementa el contador si es igual
                        else:
                            contador_repeticiones = 0  # Reinicia el contador si no es igual
                        # Actualiza la longitud anterior con la longitud actual
                        longitud_anterior = longitud_actual
                        # Si la longitud se ha repetido 20 veces, cambia event a False
                        if contador_repeticiones >= 7:
                            logging.info("La longitud de divs se ha repetido 7 veces. Terminando la extracción.")
                            event = False  # Termina el bucle
                        try:
                            for div in divs:
                                for selector in self.selectors:
                                     posts = div.find_elements(By.CSS_SELECTOR, selector)
                                try:
                                    for post in posts:
                                        try:
                                            try:
                                                href_value = WebDriverWait(post, 10).until(
                                                            EC.element_to_be_clickable((By.CSS_SELECTOR, "a"))
                                                        )
                                                #href_value = post.find_element(By.CSS_SELECTOR, "a")
                                                #logging.info("Aqui hay uno:" ,href_value)
                                                i+=1
                                                logging.info(f"estamos en el iterador post: {i}" )
                                                logging.info(f"total de post actuales: {len(elementos_vistos)}")
                                                
                                                enlace= href_value.get_attribute("href")
                                            except Exception as e:
                                                 logging.info(f"Error en obtener el enlace al inicio de for: {e}")
                                            if enlace not in elementos_vistos:  # Verifica si el texto ya fue procesado
                                               elementos_vistos.add(enlace)
                                               #logging.info(elementos_vistos)
                                               try:
                                                img= href_value.find_element(By.CSS_SELECTOR,"img").get_attribute("src")
                                               except:
                                                    logging.info("Error al obtener imagen")
                                               try:
                                                    type_post= href_value.find_element(By.CSS_SELECTOR,"svg").get_attribute("aria-label")     
                                               except:
                                                    type_post="normal"
                                                    logging.info("post normal ") 
                                               time.sleep(1)
                                               logging.info(f"La imagen es: {img}")
                                               try:
                                                    href_value.click() 
                                               except Exception as e :
                                                    logging.info(f"Error en abrir los posts {e}")
                                               j = self.post_relacionado(driver, topic,j)
                                    
                                               if j > 3:
                                                
                                                    logging.info("Se encontraton 2 publicaciones sin el tema a buscar")                                    
                                                    try:
                                                        for selector in self.selectors_close_modal :
                                                            try:
                                                                close_modal = WebDriverWait(driver, 20).until(
                                                                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                                                                )
                                                                if close_modal:  # Validar explícitamente que el modal existe
                                                                    close_modal.click()
                                                                    logging.info(f"Modal cerrado correctamente con el selector: {selector}.")
                                                                    break  # Salimos del bucle después de cerrar un modal.
                                                            except Exception as e:
                                                                logging.debug(f"No se encontró o no se pudo cerrar el modal con el selector: {selector}.")
                                                    except Exception as e:
                                                        logging.error(f"Error al cerrar el modal: {e}")
                                                    finally:
                                                        event = False  # Detener el bucle while
                                                        break  
                                               try:
                                                    likes= WebDriverWait(driver, 10).until(
                                                            EC.presence_of_element_located((By.CSS_SELECTOR, "span> a >span > span"))
                                                        )
                                                    likes= likes.text
                                                    logging.info(f"Número de likes: {likes}")
                                               except Exception as e :
                                                    likes=0
                                                    logging.info("Pblicacion sin likes")
                                                    pass
                                               try:
                                                    post_user= driver.find_element(By.CSS_SELECTOR,"h2 span.xt0psk2")
                                                    post_usuario= post_user.text
                                                    logging.info(f"usuario del post : {post_usuario}")
                                                    post_enlace= post_user.find_element(By.CSS_SELECTOR,"a").get_attribute('href')
                                                    logging.info(f"enlace de post : {post_enlace}")
                                               except:
                                                    post_usuario="no tiene"
                                                    logging.error("Erro dentro de obenter enlace o usuario")
                                                    pass
                                               try:
                                                   fecha = WebDriverWait(driver, 15).until(
                                                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.x1yztbdb.x1h3rv7z.x1swvt13 span time"))
                                                    )
                                                   fecha = fecha.get_attribute('datetime')
                                               except Exception as e:
                                                    logging.error(f"Error dentro de obenter fecha {e}")
                                                    pass     
                                               try:
                                                descripcion_post= driver.find_element(By.CSS_SELECTOR,"div._a9zs h1").text
                                                logging.info(f"descripcion del post:  {descripcion_post}")
                                               except:
                                                 descripcion_post="vacio"
                                                 logging.error("Error con dbtener la descripcion")
                                               try:
                                                    with self.conexion.connection.cursor() as cursor:
                                                        consulta_verificacion = "SELECT id FROM publicacion WHERE descripcion = %s AND usuario = %s AND enlace = %s "
                                                        cursor.execute(consulta_verificacion, (descripcion_post, post_usuario,enlace))
                                                        resultado = cursor.fetchone()
                                                        # Si no existe, insertar
                                                        if resultado is None:
                                                            consulta_insercion = "INSERT INTO publicacion (descripcion,fecha, usuario,likes,enlace) VALUES (%s,%s,%s,%s,%s) RETURNING id"
                                                            cursor.execute(consulta_insercion, (descripcion_post,fecha, post_usuario, likes, enlace ))
                                                            publicacion_id = cursor.fetchone()[0]
                                                            #logging.info("El id publiacion es resultaod none: ", publicacion_id)
                                                            self.conexion.connection.commit()
                                                            logging.info(f"Publicación insertada con éxito. ID de la publicación: {publicacion_id}")
                                                        else:
                                                            publicacion_id = resultado[0]
                                                            logging.info(f"El id publiacion es duplicada no se inserto : {publicacion_id}")
                                               except psycopg2.Error as e:
                                                            logging.error(f"Error en la base de datos con la publicación  con id : {publicacion_id}  {e} ")
                                               except Exception as e:
                                                            logging.error(f"algo esta mal con la insercion de la publicacion con id : {publicacion_id} ")
                                               
                                               try:
                                                    with self.conexion.connection.cursor() as cursor:
                                                        # Extraer la parte fija de la URL ingresada
                                                        fixed_url = img.split('?')[0]

                                                        # Extensiones posibles para las imágenes
                                                        valid_extensions = ['.webp', '.png', '.svg', '.jpg', '.jpeg']

                                                        # Verificar si la URL tiene alguna de las extensiones válidas
                                                        for ext in valid_extensions:
                                                            if ext in fixed_url:
                                                                # Verificar si existe una URL con la misma parte fija
                                                                consulta_verificacion = """
                                                                    SELECT id FROM imagen 
                                                                    WHERE LEFT(url, POSITION(%s IN url) + LENGTH(%s) - 1) = %s
                                                                """
                                                                cursor.execute(consulta_verificacion, (ext, ext, fixed_url))
                                                                resultado = cursor.fetchone()

                                                                if resultado is None:
                                                                    # Insertar si no existe
                                                                    consulta = "INSERT INTO imagen (url, publicacion_id) VALUES (%s, %s)"
                                                                    cursor.execute(consulta, (img, publicacion_id))  # Aquí se almacena la URL completa
                                                                    self.conexion.connection.commit()  # Confirmar la transacción
                                                                    logging.info(f"Imagen insertada con éxito: {publicacion_id}")
                                                                else:
                                                                    # Imagen duplicada detectada
                                                                    logging.info(f"Imagen duplicada detectada. ID existente pertenece a publicacion con id: {publicacion_id}")
                                                                break  # Salir del bucle una vez que se haya procesado la extensión
                                               except psycopg2.Error as e:
                                                    logging.error(f"Error en la base de datos Imagenes con la publicación con id: {publicacion_id} en el grupo: {e}")
                                               except Exception as e:
                                                    logging.error(f"Algo está pasando con esto Imagenes: {e}")  
                                               try:
                                                if type_post== "Clip":
                                                            #logging.info("post con video publicacion id es",publicacion_id)    
                                                            self.obtener_video(enlace,publicacion_id)                                               
                                                elif type_post == "Secuencia":
                                                            #logging.info("post con imagenes publicacion id es",publicacion_id)     
                                                            self.obtener_imagenes(driver,publicacion_id)
                                                            logging.info("post con varias imagenes o videos")  
                                               except Exception as e:
                                                    logging.info("Post sin imagenes o video")
                                                    pass
                                               try:
                                                    self.obtener_comentarios(driver,publicacion_id)
                                               except:
                                                    logging.info("No tiene comentarios ")
                                                    pass
                                               try:
                                                    close_modal= driver.find_element(By.CSS_SELECTOR,"div.x160vmok.x10l6tqk.x1eu8d0j.x1vjfegm >div[role='button']")
                                                    time.sleep(1)
                                                    close_modal.click()
                                               except Exception as e:
                                                    logging.error(f"Algo ocurrio al querer darle click al boton de cancelar {e}") 
                                               yield href_value
                                        except Exception as e:
                                            logging.error(f"Error al obtner data dentro de for {e}")
                                except Exception as e:
                                        logging.error(f"Error al obtner data fuera de for {e}")
                                
                        except:
                            pass
                    except:
                        pass        
            except:
                pass 
        except:
            logging.info("Error dentro de la funcion de extraer data")
            pass                   
    def cerrar_conexion(self):
        try:
            #self.conexion.connection.close()
            self.driver.quit()
            logging.info("Conexión cerrada y navegador cerrado.")
        except Exception as e:
            logging.error(f"Error al cerrar la conexión o el navegador: {e}")
    def procesar_extraccion(self):
        try:
            self.configurar_logger()
            logging.info("Iniciando scrapeo de temas ...")
            try:
                self.login()
            except Exception as e:
                 logging.info(f"Error en login {e}")
            self.config.read('topics.conf')
            try:
                if 'DEFAULT' in self.config and 'topic' in self.config['DEFAULT']:
                    topics_str = self.config.get('DEFAULT', 'topic')
                    self.topics = [topic.strip() for topic in topics_str.strip("[]").replace("'", "").split(",")]
                else:
                    logging.info("La opción 'topic' no se encontró en la sección 'DEFAULT'")
                logging.info(f"Temas a buscar: {self.topics}")
            except Exception as e :
                 logging.error(f"Problemas con  topics  {e}" )
            
            for topic in self.topics:
                try:
                    search_icon = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.x1iyjqo2.xh8yej3 >div:nth-of-type(2) span div.x1n2onr6 a[href='#']"))
                    )
                    search_icon.click()
                except Exception as e:
                    logging.info(f"Error en dar click: {e}")
                tipo='TEMA DE BUSQUEDA'
                try:
                    with self.conexion.connection.cursor() as cursor:
                            consulta_insercion = """INSERT INTO busqueda (busqueda,typo)
                                                    VALUES (%s,%s)"""
                            cursor.execute(consulta_insercion, (topic,tipo ))
                            #logging.info("El id publiacion es resultaod none: ", publicacion_id)
                            self.conexion.connection.commit()
                            logging.info(f"Busqueda insertada con éxito.")  
                except psycopg2.Error as e:
                            logging.error(f"Error en la base de datos con la Busqueda {e}")
                except Exception as e:
                            logging.error(f"algo esta mal con la insercion de la Busqueda ")    
                try:
                    input_topic = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label='Buscar entrada']")
                    input_topic.clear()
                    self.insert_text(topic,input_topic)
                    input_topic.send_keys(Keys.RETURN)
                    enlaces_busqueda = self.obtener_enlaces_busqueda(self.driver)

                    if enlaces_busqueda is None:
                        logging.warning(f"La función obtener_enlaces_busqueda retornó None para el tema: {topic}")
                        #input_topic = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label='Buscar entrada']")
                        search_icon.click()
                        self.random_time(0.3,1)
                        continue  # Pasamos al siguiente tema si hay un problema en obtener los enlaces

                    if not enlaces_busqueda:
                        logging.warning(f"No se encontraron enlaces para el tema: {topic}")
                        #input_topic = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label='Buscar entrada']")
                        search_icon.click()
                        self.random_time(0.3,1)
                        continue  # Pasamos al siguiente tema si no hay enlaces
                    
                    enlaces = [enlace.get_attribute('href') for enlace in enlaces_busqueda]

                    for url in enlaces:
                        try:
                            self.driver.get(url)  # Navegar directamente al enlace
                            for dato in self.extraer_data(self.driver, topic):
                                logging.info('Siguiente post:')
                            logging.info(f"Terminando de extraer enlace: {url}")
                        except Exception as e:
                            logging.error(f"Error al procesar el enlace {url}: {e}")
                            continue
                except Exception as e:
                    logging.error(f"Error al procesar el tema {topic}: {e}")
        except Exception as e:
            logging.error(f"Error dentro de extraer datos fuera {e}")
        pass   
def main():    
    scraper_perfil = Scraper_Ig() 
    scraper_perfil.procesar_extraccion()
    scraper_perfil.cerrar_conexion()
         
if __name__ == "__main__":
    main()
