# Flask restful api with blue_print on ubuntu 

# Technology stack:
    - python 3.7,
    - Flask 1.0,
    - flake8 3.5.0,
    - docker 18.06.1-ce,
    - docker-compose 1.22.0,
    - Mysql
    - postgres 11.4,
    - Flask-Testing 2.1.1,
    - Flask-SQLAlchemy 2.3.2,
    - flask-bcrypt 0.7.1
    - flask-migrate 2.1.1
    - pyjwt 1.5.3
    - flask_mail

## How to run the App!

- Install Docker version 18.06.1-ce, build e68fc7a
- Install docker-compose version 1.22.0, build f46880fe
- Install docker-machine version 0.14.0, build 89b8332

\$ cd to the project directory/

### Build the modules and subsections using docker-compose

\$ docker-compose -f docker-compose-dev.yml up -d --build

### Recreate the needed databases

\$ docker-compose -f docker-compose-dev.yml run lostfound-app python manage.py recreate-db

### Run the project

\$ docker-compose -f docker-compose-dev.yml up

### To test email verification, uncomment

- #token = generate_confirmation_token(new_user.email)
- #confirm_url = url_for('auth.confirm_email', token=token, _external=True)
- #content = confirm_url
- #subject = "Please confirm your email"
- #send_email(new_user.email, subject, content)
            
in the 'project/api/auth.py' in registration method.
define the smtp server parameter in the config file 
and also the mail authentication paramters in the docker-compose file.