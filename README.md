# Pinterest-clone API

This is a API for Pinterest like application

### Functionality

- Session authentication with email confirmation
- Customize profile
- Follow other users
- CRUD operations with Board (Collection of Pins)
- CRUD operations with Pins (Post with image)
- Like/unlike a Pins
- CRUD operaions with Comments


### Installation

1. Copy repository
2. Create and activate virtual enviroment </br>
`python3 -m venv venv` </br>
`source venv/bin/activate` or `venv\Scripts\activate` for windows
3. Install requirements </br>
`pip install -r requirements`
4. Go to `src` directory and run migrations </br>
`./manage.py makemigrations` </br>
`./manage.py migrate`
5. Run `./manage.py runserver`
6. Go to [localhost:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)


### Packages that were used

- Django==4.2.5
- django-cors-headers==4.2.0
- djangorestframework==3.14.0
- drf-spectacular==0.26.5
- Pillow==10.0.1
- six==1.16.0
