# Install the Django project

First, create the virtual environment :
```bash
py -m venv venv
venv\Scripts\activate       # on Windows
# source venv/bin/activate  # on macOS / Linux
```
Then install the libraries :
```bash
pip install django
pip install djangorestframework
pip install django-filter # for filtering via URL
pip install drf-spectacular # for API documentation
pip install django-phonenumber-field phonenumbers # for phone number validation
pip install dotenv # for .env secrets
```

Make the migrations :
```bash
py manage.py makemigrations # create database file
py manage.py migrate
```

Create the admin :
```bash
py manage.py createsuperuser
```

Finally, launch the server :
```bash
py manage.py runserver
```

# About the implementation

## API documentation

Created with the 'drf-spectacular' library.

In the '*settings.py*' file :
```python
# config/settings.py
INSTALLED_APPS = [
    ...
    'drf_spectacular',
]
REST_FRAMEWORK = {
    ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'Web project API',
    'DESCRIPTION': 'Web project, this is the API for the Django server',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

Then simply add the URL to the documentation, in the '*urls.py*' file at the project root :
```python
# config/urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
```
The documentation can now be accessed with the '*api/docs/*' URL (and '*api/schema/*' just downloads the API schema).





