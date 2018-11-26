# BuscaMed-Server

#### Configuracion de la BD:

`$`sudo apt-get update

`$`sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib

`$`sudo -u postgres psql

`postgres=#`CREATE DATABASE buscamedserver;

`postgres=#`CREATE USER buscameduser WITH PASSWORD '1234';

`postgres=#`ALTER ROLE buscameduser SET client_encoding TO 'utf8';

`postgres=#`ALTER ROLE buscameduser SET default_transaction_isolation TO 'read committed';

`postgres=#`ALTER ROLE buscameduser SET timezone TO 'UTC';

`postgres=#`GRANT ALL PRIVILEGES ON DATABASE buscamedserver TO buscameduser;

`postgres=#`\q

`$`python manage.py makemigrations 

`$`python manage.py migrate 

`$`python manage.py createsuperuser 
**(user: admin, email: admin@admin.com)**

`$`sudo ufw allow 8000

#### Primera Corrida:
##### Nota: Es recomendable usar un virtual environment

`$`pip install -r requirements.txt
`$`python manage.py loadmeds
`$`python manage.py runserver 0.0.0.0:8000

**Escribir en un browser 127.0.0.1:8000**
