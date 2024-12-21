# INSTAGRAM_SCRAPER

## Setup Instructions

Before you begin, make sure to create the database. You can find the necessary SQL commands in the `instagram_db.sql` file. Execute this file in your PostgreSQL environment to create the required tables.

### Required Files
Ensure the following configuration files are properly configured:
- **`topics.conf`**: Specify topics for scraping.
- **`perfil.conf`**: List of target profiles.
- **`db_credentials.ini`**: Stores database connection details.

```conf
[DEFAULT]
perfiles=['https://www.tiktok.com/@valeria.zevallos0','https://www.tiktok.com/@manuellopez5193']
```
```conf
[DB]
dbname=instagram_db
user=postgres
password=Taicho10
host=localhost
port=5432
```

### Database Configuration

Once you have created the database, update the connection parameters in the code (`user`, `password`, `port`, and `localhost`) to match your PostgreSQL database settings.



### Running the Script

To execute the scraping code, run the following command:

```bash
py scrape_main_ig.py --funcion_ejecutar all # ejcuta tatno perfil como busqueda y procesamiento de videos e imagenes
py scrape_main_ig.py --funcion_ejecutar busqueda # ejecuta srape con busqeuda mas procesamiento de videos  e imagenes
py scrape_main_ig.py --funcion_ejecutar perfil # ejecuta scrape de perfiles mas procesamiento de videos e imagenes

````

## Requirements
To Run this scapre code you'll need to install : 
- Python 
- Seleniuum
- PostgreSQL

### Dependencies
Libraries that you will need:

- **selenium**: 
- **fake_useragent**: 
- **psycopg2**: 
- **pyautogui**:
- **logging**: 
- **configparser**: 
```bash
pip install selenium

pip install fake-useragent

pip install psycopg2

pip install pyautogui

pip install logging 
```
## Appendix

### Links to Scrape

To specify the toopics you want to scrape, enter them in the following files:

- `topics.conf`


In each of these files, update the `self."type_page"_links` list with the URLs you wish to scrape on file `scrape_perfil_ig.py`:

```python
self.perfil_links = [
            "https://www.instagram.com/elcomercio/",
           # more links
        ]
        
````
### Adding Profiles

To add profile credentials, save them in the `credentials.conf` file using the following format:

```conf
emailkey1=blrdmanrique@gmail.com
usernamekey1=AbelardoMa65534
passwordkey1=Abelardo_X_23_01_00

emailkey2=something1
usernamekey2=something2
passwordkey2=something3

emailkey3=some_example@gmail.com
usernamekey3= usernamekey_example
passwordkey3=password_example

emailkey4=some_example1@gmail.com
usernamekey4= usernamekey1_example
passwordkey4=password2_example
````
### Operating Images & Videos
Both `image_procces.py` & `video_procces.py` files transform the links of the PostgreDB in files jpg & mp4 to future use with deep learning
or any other purpose that you have in mind.Those files are saved in their respective folders ,each file inside them has a name obtanied from its id & id publiacion to iddentify them in the db.
 
### Run separately

```bash
py profile_X.py

py process_image.py

py process_video_1.py

py process_video2.py
````