from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,WebDriverException,TimeoutException
import pyautogui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import uuid
import time
import configparser
import random
from selenium.webdriver.common.by import By
import psycopg2
import logging
from db_connection_IG import DatabaseConnection
from sys import exit

class Scraper_Ig():
    def __init__(self):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Activar modo headless
        #chrome_options.add_argument("--disable-gpu")  # Opcional: mejora en algunos entornos
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-notifications")
        #chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome( options= chrome_options)
        self.driver.maximize_window()
        self.config = configparser.ConfigParser()
        self.config.read('credentials.conf')
        #self.credentials = self._get_credentials()
        self.email = self.config.get('DEFAULT','emailkey')
        #self.username = self.config.get('DEFAULT','usernamekey')
        self.password = self.config.get('DEFAULT','passwordkey')
        self.perfil_links = [
            "https://www.instagram.com/gabrc6979/",
           # 'https://x.com/WH40kbestof',
           # 'https://x.com/EmergenciasEc',
        ]
        self.conexion = DatabaseConnection()
        self.conexion.crear_conexion()  

    def login(self):
        try:
            time.sleep(2)
            target_url = 'https://www.instagram.com/accounts/login/'
            self.driver.get(target_url) 
            
            time.sleep(1)
            try:
                email_input = self.driver.find_element("css selector","input[name='username']")
                email_input.send_keys(self.email)
            except Exception as e :
                print("Algo ocurrio en el inicio de sesión con username: " ,e )
            try:
                password_input = self.driver.find_element("css selector", "input[name='password']")
                password_input.send_keys(self.password)
            except Exception as e:
                print("Aqui tenemos un error dentro de constraseña",e)
            login = self.driver.find_element("css selector", "button[class=' _acan _acap _acas _aj1- _ap30']").click()
        except Exception as e:
                print("Error dentro de login en ",e)
    def obtener_comentario(self,driver):
        try:
                time.sleep(2)
                feed_coments = driver.find_element(By.CSS_SELECTOR, "ul._a9z6._a9za >div> div> div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1")
                return feed_coments.find_elements(By.CSS_SELECTOR, "div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1yztbdb.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1")
            
        except NoSuchElementException as e:
                print(f"Error: Could not locate the 'feed_comments' or 'subelelementos comentario' elements. : {e}")
        except Exception as e:
                print(f"Unexpected error in obtener_posts: {e}" )
        return []
    def obtener_imagen(self,driver):
        try:
                time.sleep(2)
                feed_pictures = driver.find_element(By.CSS_SELECTOR, "div.x1lliihq.x1n2onr6 ul._acay")
                return feed_pictures.find_elements(By.CSS_SELECTOR, "li._acaz")
            
        except NoSuchElementException as e:
                print(f"Error: Could not locate the 'feed_pictures' or 'subelelementos imagen' elements. : {e}")
        except Exception as e:
                print(f"Unexpected error in obtener_pictures: {e}" )
        return []
    def obtener_video(self,publicacion_id,enlace):
         try:
                with self.conexion.connection.cursor() as cursor:
                    consulta_verificacion = "SELECT id FROM video WHERE url = %s AND publicacion_id =%s"
                    cursor.execute(consulta_verificacion, (enlace,publicacion_id))
                    resultado = cursor.fetchone()
                    
                    if resultado is None and enlace is not None:
                            consulta = "INSERT INTO video (url, publicacion_id) VALUES (%s, %s) "
                            cursor.execute(consulta, (enlace,publicacion_id))
                            self.conexion.connection.commit() 
                            print("Comentario video insertado con éxitos")
                    else:
                        print(f"El id repetido en videos es: {resultado}")
                        print("NO SE INSERTO VIDEO ELEMENTO REPETIDO")        
         except psycopg2.Error as e:
                        logging.error(f"Error en la base de datos con la tabla videos: {e}")
         except Exception as e:
                        print(f"Algo está pasando conn el video insertado: {e}")
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
                        print(f"error al llamar funciones en comentarios {e}")
                        print(f"Nueva URL: {url_actual}")
                        pass
                    longitud_actual = len(coments)
                    if longitud_actual == longitud_anterior:
                        contador_repeticiones += 1  # Incrementa el contador si es igual
                    else:
                        contador_repeticiones = 0  # Reinicia el contador si no es igual
                    # Actualiza la longitud anterior con la longitud actual
                    longitud_anterior = longitud_actual
                    # Si la longitud se ha repetido 20 veces, cambia event a False
                    if contador_repeticiones >= 5:
                        logging.info("La longitud de comentarios se ha repetido 5 veces. Terminando la extracción de comentarios del post actual.")
                        event = False  # Termina el bucle
                        pass
                    try:
                            i=0
                            print("cantidad de comentarios" ,len(coments))
                            for coment in coments:
                                contenido_coment=coment.text
                                if contenido_coment not in comentarios_vistos:  # Verifica si el texto ya fue procesado
                                    comentarios_vistos.add(contenido_coment)
                                    print("Estamos en el iterador" , i)
                                    user_coment= coment.find_element(By.CSS_SELECTOR, 'h3 span')
                                    usuario= user_coment.text
                                    user_ref = user_coment.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                                    print("usuario comentador: ", usuario)
                                    print("user ref: " , user_ref)
                                    try:
                                        descripcion_comentario= coment.find_element(By.CSS_SELECTOR, 'div._a9zs span').text
                                        print("comentario ",descripcion_comentario)
                                    except:
                                        print("no tiene un comentario")
                                    try:  
                                        with self.conexion.connection.cursor() as cursor:
                                            consulta_verificacion = "SELECT id FROM comentario WHERE usuario = %s AND descripcion_comentario = %s AND  publicacion_id= %s"
                                            cursor.execute(consulta_verificacion, (usuario, descripcion_comentario,publicacion_id ))
                                            resultado = cursor.fetchone()
                                            if(resultado == None):
                                                consulta = "INSERT INTO comentario (publicacion_id, enlace_usuario, usuario,descripcion_comentario) VALUES (%s,%s, %s,%s) RETURNING id"
                                                cursor.execute(consulta, (publicacion_id,user_ref,usuario, descripcion_comentario))
                                                self.conexion.connection.commit()
                                                comentario_id = cursor.fetchone()[0]
                                                print(f"Comentario insertada con éxito.")
                                            else:
                                                print("comentario ya doble y repetido,no ingestado a la db")
                                                contador_comentarios_repetidos += 1   
                                                if(contador_comentarios_repetidos >= 6):
                                                    print("Se reptitio mas de 6 comentarios , obviamos los demas comentarios")
                                                    event=False 
                                                                    
                                    except psycopg2.Error as e:
                                                print(f"Error en la base de datos con la comentario  {e}" )
                                    except Exception as e:
                                                print(f"algo esta mal con la insercion del comentario") 
                                i +=1;
                                
                    except Exception as e:
                        print ("Error en el desarrollo del bucle",e)
                        pass       
                    try:
                        more_comment_button = driver.find_element(By.CSS_SELECTOR, 'li button._abl-')
                        more_comment_button.click()
                        pass
                    except: 
                        print("No tiene mas comentarios")     
        except Exception as e:
            print("Ocurrio un error obtiendo lo comentarios probablemente dentro del bucle")
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
            print(f'Cantidad total de imagenes: {longitud_actual}')
            if longitud_actual == longitud_anterior:
                contador_repeticiones += 1  # Incrementa el contador si es igual
            else:
                contador_repeticiones = 0  # Reinicia el contador si no es igual
            # Actualiza la longitud anterior con la longitud actual
            longitud_anterior = longitud_actual
            # Si la longitud se ha repetido 20 veces, cambia event a False
            if contador_repeticiones >= 3:
                print("La longitud de divs se ha repetido 3 veces. Terminando la extracción.")
                event = False  # Termina el bucle
            for imagen in imagenes:
                print("Estamos en el iterador de imagenes", i)
                try:
                    img= imagen.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    if img not in imagenes_vistas:  # Verifica si el texto ya fue procesado
                        imagenes_vistas.add(img)
                        print("Imagen enlace:" ,img)
                        try:
                                with self.conexion.connection.cursor() as cursor:
                                    consulta_verificacion = "SELECT id FROM imagen WHERE url = %s "
                                    cursor.execute(consulta_verificacion, (img,))
                                    resultado = cursor.fetchone()
                                    if(resultado == None):
                                        consulta = "INSERT INTO imagen (url,publicacion_id) VALUES (%s, %s)"
                                        cursor.execute(consulta, (img,publicacion_id ))
                                        self.conexion.connection.commit() # Asegúrate de confirmar la transacción
                                        print(f"Imagen insertada con éxito")
                                    else:   
                                        print(f"Imagen duplicada detectada. ID existente pertenece a publicacion con id : {publicacion_id}")
                        except psycopg2.Error as e:
                                        print(f"Error en la base de datos Imagenes con la publicación  con id : {publicacion_id} en el grupo : {e}")
                        except Exception as e:
                                        print(f"Algo está pasando con esto Imagenes: {e}")
                except Exception as e :
                     print("Erro en obtener mas imagenes", e)                        
                i+=1;            
                try: 
                    button_to_next_img= driver.find_element(By.CSS_SELECTOR,"div.x1lliihq.x1n2onr6 div button[aria-label='Siguiente']")
                    button_to_next_img.click()
                    time.sleep(2) 
                except:
                    print("no hay mas inagenes")
        
        pass
    def scroll_hasta_el_final_post(self,driver,min_scroll,max_scroll,min_s,max_s):
        scroll_distance = random.randint(min_scroll, max_scroll)  # Randomize scroll distance
        #logging.info("La distnacia movida en post fue o es :" , scroll_distance)
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        target_scroll_position = current_scroll_position + scroll_distance
        driver.execute_script(f"window.scrollTo(0, {target_scroll_position});")
        time.sleep(random.uniform(min_s, max_s))  # Randomize delay to mimic human behavior       
    def obtener_posts(self,driver):
        try:
            time.sleep(2)
            feed_div = driver.find_element(By.CSS_SELECTOR, "main > div > div:nth-of-type(2)> div")
            return feed_div.find_elements(By.CSS_SELECTOR, "div._ac7v.x1f01sob.xcghwft.xat24cr.xzboxd6")
           
        except NoSuchElementException as e:
            print(f"Error: Could not locate the 'feed_div' or 'subelelementos' elements. : {e}")
        except Exception as e:
            print(f"Unexpected error in obtener_posts: {e}" )
        return []
    def perfil_generador(self,perfil_links):
        for perfil_link in perfil_links:
            yield perfil_link
    def extraer_data(self,driver):
        try:
            elementos_vistos = set()
            event =True  
            contador_repeticiones = 0  # Contador para verificar repeticiones
            longitud_anterior = -1  # Inicializamos en -1 para que sea diferente de la primera longitud
            try:
                while event:  # Bucle infinito hasta que se detenga manualmente
                    try:
                        self.scroll_hasta_el_final_post(driver,300,400,0,1.5)
                        divs = self.obtener_posts(driver)  # Obtiene los elementos actuales
                        i =0
                        longitud_actual = len(divs)
                        print(f'Cantidad total de divs: {longitud_actual}')
                        if longitud_actual == longitud_anterior:
                            contador_repeticiones += 1  # Incrementa el contador si es igual
                        else:
                            contador_repeticiones = 0  # Reinicia el contador si no es igual
                        # Actualiza la longitud anterior con la longitud actual
                        longitud_anterior = longitud_actual
                        # Si la longitud se ha repetido 20 veces, cambia event a False
                        if contador_repeticiones >= 10:
                            print("La longitud de divs se ha repetido 10 veces. Terminando la extracción.")
                            event = False  # Termina el bucle
                        try:
                            for div in divs:
                                posts= div.find_elements(By.CSS_SELECTOR, "div.x1lliihq.x1n2onr6.xh8yej3.x4gyw5p.x1ntc13c.x9i3mqj.x11i5rnm.x2pgyrj")
                                
                                try:
                                    for post in posts:
                                        try:
                                            try:
                                                href_value = WebDriverWait(post, 10).until(
                                                            EC.element_to_be_clickable((By.CSS_SELECTOR, "a"))
                                                        )
                                                #href_value = post.find_element(By.CSS_SELECTOR, "a")
                                                #print("Aqui hay uno:" ,href_value)
                                                i+=1
                                                print("estamos en el iterador post: ", i)
                                                print("total de post actuales: ",len(elementos_vistos))
                                                
                                                enlace= href_value.get_attribute("href")
                                            except Exception as e:
                                                 print("Error en obtener el enlace al inicio de for: ", e)
                                            if enlace not in elementos_vistos:  # Verifica si el texto ya fue procesado
                                               elementos_vistos.add(enlace)
                                               #print(elementos_vistos)
                                               try:
                                                img= href_value.find_element(By.CSS_SELECTOR,"img").get_attribute("src")
                                               except:
                                                    print("Error al obtener imagen")
                                               try:
                                                    type_post= href_value.find_element(By.CSS_SELECTOR,"svg").get_attribute("aria-label")     
                                               except:
                                                    type_post="normal"
                                                    print("post normal ") 
                                               time.sleep(1)
                                               print("La imagen es: ",img)
                                               try:
                                                    href_value.click() 
                                               except Exception as e :
                                                    print("Aqui sucedida el error largo al darle click a un post ", e)
                                               try:
                                                    likes= driver.find_element(By.CSS_SELECTOR,"span> a >span > span").text
                                                    print("Número de likes: ", likes)
                                               except Exception as e :
                                                    print("Error al obtener likes : " ,e )
                                                    pass
                                               try:
                                                post_user= driver.find_element(By.CSS_SELECTOR,"h2 span.xt0psk2")
                                                post_usuario= post_user.text
                                                print("usuario del post :", post_usuario)
                                                post_enlace= post_user.find_element(By.CSS_SELECTOR,"a").get_attribute('href')
                                                print("enlace de post :",post_enlace)
                                               except:
                                                post_usuario="no tiene"
                                                print("Erro dentro de obenter enlace o usuario")
                                                pass
                                               try:
                                                descripcion_post= driver.find_element(By.CSS_SELECTOR,"div._a9zs h1").text
                                                print("descripcion del post: ", descripcion_post)
                                               except:
                                                 descripcion_post="vacio"
                                                 print("Error con dbtener la descripcion")
                                               try:
                                                    with self.conexion.connection.cursor() as cursor:
                                                        consulta_verificacion = "SELECT id FROM publicacion WHERE descripcion = %s AND usuario = %s AND enlace = %s "
                                                        cursor.execute(consulta_verificacion, (descripcion_post, post_usuario,enlace))
                                                        resultado = cursor.fetchone()
                                                        # Si no existe, insertar
                                                        if resultado is None:
                                                            consulta_insercion = "INSERT INTO publicacion (descripcion, usuario,likes,enlace) VALUES (%s, %s,%s,%s) RETURNING id"
                                                            cursor.execute(consulta_insercion, (descripcion_post, post_usuario, likes, enlace ))
                                                            publicacion_id = cursor.fetchone()[0]
                                                            print("El id publiacion es resultaod none: ", publicacion_id)
                                                            self.conexion.connection.commit()
                                                            print(f"Publicación insertada con éxito. ID de la publicación: {publicacion_id}")
                                                        else:
                                                            publicacion_id = resultado[0]
                                                            print("El id publiacion es resultado no none: ", publicacion_id)
                                               except psycopg2.Error as e:
                                                            print(f"Error en la base de datos con la publicación  con id : {publicacion_id}  {e} ")
                                               except Exception as e:
                                                            print(f"algo esta mal con la insercion de la publicacion con id : {publicacion_id} ")
                                               if type_post== "Clip":
                                                        print("post con video")    
                                                        self.obtener_video(enlace,publicacion_id)                                               
                                               elif type_post == "Secuencia":
                                                        self.obtener_imagenes(driver,publicacion_id)
                                                        print("post con varias imagenes o videos")  
                                               try:
                                                    self.obtener_comentarios(driver,publicacion_id)
                                               except:
                                                    print("No tiene comentarios ")
                                                    pass
                                               try:
                                                    close_modal= driver.find_element(By.CSS_SELECTOR,"div.x160vmok.x10l6tqk.x1eu8d0j.x1vjfegm >div[role='button']")
                                                    time.sleep(1)
                                                    close_modal.click()
                                               except Exception as e:
                                                    print("Algo ocurrio al querer darle click al boton de cancelar", e) 
                                               yield href_value
                                        except Exception as e:
                                            print("Error al obtner data dentro de for", e)
                                except Exception as e:
                                        print("Error al obtner data fuera de for", e)
                                
                        except:
                            pass
                    except:
                        pass        
            except:
                pass 
        except:
            print("Error dentro de la funcion de extraer data")
            pass                   
    def cerrar_conexion(self):
        try:
            #self.conexion.connection.close()
            self.driver.quit()
            print("Conexión cerrada y navegador cerrado.")
        except Exception as e:
            print(f"Error al cerrar la conexión o el navegador: {e}")
    def procesar_extraccion(self):
        try:
            generador_perfil = self.perfil_generador(self.perfil_links)
            total_paginas = len(self.perfil_links)  # Total de paginas a procesar
            print("hay perfil:  " ,total_paginas)
            for perfil_link in generador_perfil:
                self.driver.get(perfil_link)
                for dato in self.extraer_data(self.driver):
                    print('siguiente post:')
        except Exception as e:
            print(f"Error dentro de extraer datos fuera {e}")
        pass   
        
def main():    
    scraper_perfil = Scraper_Ig() 
    scraper_perfil.login()
    time.sleep(5)
    scraper_perfil.procesar_extraccion()
    scraper_perfil.cerrar_conexion()
         
if __name__ == "__main__":
    main()
