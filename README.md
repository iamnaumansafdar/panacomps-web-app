# panacomps-web-app

Shared Private Repository for the Development of https://web.panacomps.com

Panacomps saved me hours of manually searching the Registro Público de Panamá for comps and  enabled me to provide my international clients with the data they expect. Highly recommend it


## Getting Started

### Clone the repository

```bash
git clone https://github.com/mdmxo/panacomps-web-app.git
```

### Setup Environment

#### Create & activate a virtual environment

```bash
cd panacomps-web-app
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies

```bash 
pip install -r requirements.txt
```

### Configure .env 

Generate a new secret key using the following command:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

```dotenv
DEBUG=True
SECRET_KEY=''
DATABASE_URL='sqlite:///db.sqlite3'
```

### Run migrations

```bash
python manage.py migrate
```

### Run the project

```bash
python manage.py runserver
```
