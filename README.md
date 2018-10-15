# BuscaMed-Server

#### Configuracion de la BD:

`<addr>`sudo apt-get update

`<addr>`sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib

`<addr>`sudo -u postgres psql

`<addr>`CREATE DATABASE buscamed;

`<addr>`CREATE USER buscameduser WITH PASSWORD '1234';

`<addr>`ALTER ROLE buscameduser SET client_encoding TO 'utf8';

`<addr>`ALTER ROLE buscameduser SET default_transaction_isolation TO 'read committed';

`<addr>`ALTER ROLE buscameduser SET timezone TO 'UTC';

`<addr>`GRANT ALL PRIVILEGES ON DATABASE buscamedserver TO buscameduser;

`<addr>`\q

`<addr>`python manage.py makemigrations 

`<addr>`python manage.py migrate 

`<addr>`python manage.py createsuperuser 
**user: admin, email: admin@admin.com**

`<addr>`sudo ufw allow 8000

`<addr>`python manage.py runserver 0.0.0.0:8000

**Escribir en un browser 127.0.0.1:8000**
