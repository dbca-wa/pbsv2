# Bushfire Mitigation System

A system to manage risk, planning, implementation and post-implementation review for the mitigation of bushfires in Western Australia

## Backend

The backend of Prescribed Burns System is a [Python](https://www.python.org/) [Django](https://www.djangoproject.com/) project
using [Django REST Framework](https://www.django-rest-framework.org/) backed by a [PostgreSQL](https://www.postgresql.org/)
database. The backend uses pip to manage its dependencies.

### Requirements

- [Python 3.10](https://www.python.org/downloads/release/python-3100/)
- [Pip](https://pypi.org/project/pip/)
- [GDAL](https://gdal.org/download.html)

### Development

#### Installation

To get a standard development environment up and running using Poetry and virtual environments:

```shell

# Ensure Python 3.10 is currently activated
$ python3 --version
Python 3.10.4

# Check GDAL is installed correctly
$ gdal-config --version
3.3.2

# Install Python GDAL
$ pip install gdal==`gdal-config --version`
```

#### Running

To run a development server, use the `Django` `manage.py` script:

```shell
$ DEBUG=True python manage.py runserver
```

### Configuration

The backend requires the following environment variables to be set:

```shell
SECRET_KEY=...
DATABASE_URL=...
PRODUCTION_EMAIL=False
EMAIL_INSTANCE='DEV'
NON_PROD_EMAIL='nonprodemail@dbca.wa.gov.au'
EMAIL_DELIVERY=on
ENABLE_DJANGO_LOGIN=True  <-- Will enable a login screen for developement purposes, set to false for production
```

For convenience, these can also be defined in a `.env` file that will be loaded at runtime.

### Requirements

- [Node.js 18](https://nodejs.org/en/blog/release/v18.0.0/)
- [npm](https://www.npmjs.com/)

### Development

#### Installation

To install and/or appropriately update packages and their dependencies:

```shell
$ npm install
```

#### Building

To build the project:

```shell
$ npm run build
```

#### Development Environment

To run a development server:

```shell
$ npm run dev
```

or to use a different port:

```shell
$ PORT=9072 npm run dev
```

### Structure

They are:

- `govapp`
  - contains the department base templates, base packages and backend code
- `govapp/frontend`
  - Contains node web app frontend code

# Prebuilt GDAL wheel files that can be install with pip (alternative solution when pip install gdal doesn't work)

https://girder.github.io/large_image_wheels/
