# > technologies to be use
# django restful api
- extension to django
- built in auth
- viewsets
to create structure of the api
- serializers
to provide validational 
- browsable api

# docker
- for isolation
- easy to manage when fails happen

# travis-ci 
- automate testing and linting
- email notification if build breaks
- identify issues early

# postgresql
- production grade database

# > Test Driven Development (TDD)
- Traditional dev
	Implement --> write tests
- TDD
	write tests --> implement feature
- ? why use TDD ?
 - increases test coverage
 - ensure tests work
 - encourages quality code
 - stay focused

# UNIT TESTS
- Checks that your code works
- isolate specific code
 - Functions
 - Class
 - API endpoints
- ? why write tests ?
 - expected in most professional dev teams
 - makes it easier to change code
 - saves time!
 - testable, better quality code
	 
	# TEST STAGES
	- setup - create sample database objects
	- Execution - Call the code
	- Assertions - confirm expected output

- 6.22 & 6.23
    # EXPLAINS WHAT UNITEST IN ACTION
    - the Django unit test framework looks for any files that begin with tests and it 
    - basically uses them as the tests when you run the Django run unit tests command

    #### root/app/app/tests.py
    from django.test import TestCase
    from app.calc import add, subtract

    class CalcTests(TestCase):
        def test_add_numbers(self): # function shoud starts with "test"_functionname
            """Test that values are added together"""
            self.assertEqual(add(3, 8), 11)
            
        def test_subtract_numbers(self):
            """Test that values are subtracted and returned"""
            self.assertEqual(subtract(5, 11), 6)        

    #### root/app/app/calc.py
    def add(x, y):
        """Add two numbers together and return the result"""
        return x + y

    def subtract(x, y):
        """Subtract x from y and return result"""
        return y - x
        
    # docker-compose build	
    # docker-compose run app sh -c "python manage.py test" 
    - docker-compose run app sh -c "python manage.py test && flake8"
    # note:docker: no such file or directory , go to settings > Shared drive > reset credentials
    # note:docker: ones prompt for shared confirmation during the startproject you may need to signout/signin or better restart your computer

# > Section 7: Configure Django custom user model
# 24 - create core app	
    - it won't be serving anything it will just be simply holding our databasemodels.
    - docker-compose run app sh -c "python manage.py startapp core"
    - clean core app:
        - remove tests(tests files should be in a separate dir, we may need to make multiple test), views
    - migrations, admin, etc, will serve in this app
# 25 - Add tests for custom user model
    #### root/app/app/settings.py
    INSTALLED_APP = [
        ...
        'core',
    ]
    #### root/app/app/core/tests/test_models.py    
    from django.test import TestCase
    from django.contrib.auth import get_user_model


    class ModelTests(TestCase):

        def test_create_user_with_email_successful(self):
            """Test creating a new user with an email is successful"""
            email = 'test@londonappdev.com'
            password = 'Password123'
            user = get_user_model().objects.create_user(
                email=email,
                password=password
            )

            self.assertEqual(user.email, email)
            self.assertTrue(user.check_password(password))
    
# 26 - Implement custom user model
    - the base user manager and the permissions mixin, these are the things that are required to extend the Django user model whilst making use of some of
    the features that come with the django user model out of the box.

    #### root/app/app/core/models.py
    from django.db import models
    from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
        PermissionsMixin


    class UserManager(BaseUserManager): 
    # The manager class is a class that provides the helper functions for creating a user or creating a super user.

        def create_user(self, email, password=None, **extra_fields):
            # **extra_fields > this is a dynamic fields that it will accept multiple fields
            """Creates and saves a new User"""
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)

            return user


    class User(AbstractBaseUser, PermissionsMixin):
        """Custom user model that supports using email instead of username"""
        email = models.EmailField(max_length=255, unique=True)
        name = models.CharField(max_length=255)
        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)

        objects = UserManager()

        USERNAME_FIELD = 'email'
        

    #### root/app/app/settings.py

    ...
    AUTH_USER_MODEL = 'core.User'

    # run command on your terminal
    python manage.py makemigrations core
    python manage.py test

# 27 - Normalize email addresses
    # everything after the @ or the domain part will be lowercase
    #### root/app/app/core/tests/test_models.py
        ...
        def test_new_user_email_normalized(self):
            """Test the email for a new user is normalized"""
            email = 'test@LONDONAPPDEV.com'
            user = get_user_model().objects.create_user(email, 'test123')
            
            self.assertEqual(user.email, email.lower())
            
    # run command
    docker-compose run app sh -c "python manage.py test"
    - after running the command, it's failing as expected, 
    test is failing so that's because the londonappdev.com has not been made lower
    case when the user was created here it was still created as upper case

    #### root/app/app/core/models.py
    # edit the user to normailize the email to lowercase  
    -before 
        user = self.model(email=email, **extra_fields)
    -after
        user = self.model(email=self.normalize_email(email), **extra_fields)
    # normalize_email object is under BaseUserManager feature

# 28 - Add validation for email field

    #### root/app/app/test_models.py
    ...
    
    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')
    
    > docker-compose run app sh -c "python manage.py test"
    # valueerror not raised 
    
    #### root/app/app/core/models.py
    def create_user
        if not email:
            raise ValueError('Users must have an email address')
    ...
    
    > docker-compose run app sh -c "python manage.py test"

# 29 - Add support for creating superusers
    
    #### root/app/app/test_models.py
    ...

    def test_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@londonappdev.com',
            'test123'
        )

        self.assertTrue(user.is_superuser) # you cant see it because it is part of permissions mixin
        self.assertTrue(user.is_staff)
    
    > docker-compose run app sh -c "python manage.py test"
    # And you can see that the tests fail because the create super
    # user doesn't exist so let's go ahead and implement this feature and make this
    # test pass.
    
    #### root/app/app/core/models.py
    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    
    > docker-compose run app sh -c "python manage.py test"
    # this time the test should pass
    > docker-compose run app sh -c "python manage.py test && flake8"
    # this time the test should pass however flak8 notifies as that admin is unused
    
    #### root/app/app/core/admin.py
    # just add comment to disable the code
    
# > Section 8: Setup Django admin
    
# 30. Add tests for listing users in Django admin
    #### root/app/app/core/tests/test_admin.py
    # this is where we're going to store all of our admin page unit tests.
    from django.test import TestCase, Client
    from django.contrib.auth import get_user_model
    from django.urls import reverse


    class AdminSiteTests(TestCase):

        def setUp(self):
            self.client = Client()
            self.admin_user = get_user_model().objects.create_superuser(
                email='admin@londonappdev.com',
                password='password123'
            )
            self.client.force_login(self.admin_user)
            self.user = get_user_model().objects.create_user(
                email='test@londonappdev.com',
                password='password123',
                name='Test User Full Name',
            )

        def test_users_listed(self):
            """Test that users are listed on the user page"""
            url = reverse('admin:core_user_changelist') # we don't have to update the url
            res = self.client.get(url)

            self.assertContains(res, self.user.name)
            self.assertContains(res, self.user.email)

# 31. Modify Django admin to list our custom user model

    #### root/app/app/core/admin.py
    from django.contrib import admin
    from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

    from core import models


    class UserAdmin(BaseUserAdmin):
        ordering = ['id']
        list_display = ['email', 'name']


    admin.site.register(models.User, UserAdmin)

# 32. Modify Django admin to support changing user model
    
    #### root/app/app/tests/test_admin.py
    ...
    
    def test_user_page_change(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id]) # url ex. /admin/core/user/
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
    
    > docker-compose run app sh -c "python manage.py test" 
    # And yep it error-ed right away because there's some unknown fields and
    # basically we need to customize our user admin field sets to support our custom
    # model as opposed to the default model that it's expecting.
    
    #### root/app/app/core/admin.py
    ...
    from django.utils.translation import gettext as _ 
    # and this is the recommended convention for converting strings in our
    # Python to human readable text and the reason we do this is just so it gets
    # passed through the translation engine 
    
    
    class UserAdmin(BaseUserAdmin):
        ...
        
        fieldsets = (
            (None, {'fields': ('email', 'password')}),
            (_('Personal Info'), {'fields': ('name',)}),
            (
                _('Permissions'),
                {
                    'fields': (
                        'is_active',
                        'is_staff',
                        'is_superuser',
                    )
                }
            ),
            (_('Important dates'), {'fields': ('last_login',)}),
        )

# 33. Modify Django admin to support creating users
    #### root/app/app/tests/test_admin.py
    
    ...
    
    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
    
    
    > docker-compose run app sh -c "python manage.py test" 
# it failed with the expected error that says the user name is not
# specified for the user.
# So now we can head over to our admin.py and we can
# correct this by adding the add field sets class variable.
    
    #### root/app/app/core/admin.py
    class UserAdmin(BaseUserAdmin):
        ...
        add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }),
        )
        # just took the defaults from the user admin documentation so I didn't want to
        # change it too much so the default is that it has a wide class and that's it


# > Section 9: Setting up database

# 34. Add postgres to docker compose
    ### root/app/docker-compose.yml
           
      ...
      
      environment:
        - DB_HOST=db
        - DB_NAME=app
        - DB_USER=postgres
        - DB_PASS=supersecretpassword
      depends_on:
        - db
    db:
      image: postgres:10-alpine
      environment:
        - POSTGRES_DB=app
        - POSTGRES_USER=postgres
        - POSTGRES_PASSWORD=supersecretpassword

# 35. Add postgres support to Dockerfile
    #### root/app/requirements.txt
    ...
    psycopg2>=2.7.5,<2.8.0
    # that django recommends for communicating between Django and postgres is called
    
    # this and if we try to build this now it wouldn't work because there's some
    # dependencies that are required in order to install this package on any system.
    # So let's head over to the docker file and we're going to add these dependencies here
    
    #### root/app/Dockerfile
    ...

    # Install dependencies
    COPY ./requirements.txt /requirements.txt
    RUN apk add --update --no-cache postgresql-client
    RUN apk add --update --no-cache --virtual .tmp-build-deps \
          gcc libc-dev linux-headers postgresql-dev
    RUN pip install -r /requirements.txt
    RUN apk del .tmp-build-deps

# 36. Configure database in Django
    #### root/app/app/settings.py
    before
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
    after
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': os.environ.get('DB_HOST'), # the way to pull-in the environment vars is os.environ.get <-(dockerfile)
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASS'),
        }
    }
    

# > Section 10: Waiting for postgres to start

# 37. Mocking with unittests
    - mocking - Mocking is when you override or change the behavior of the dependencies
    of the code that you're testing.
    - We use mocking to avoid any unintended side   
    effects and also to isolate the specific piece of code that we want to test.
    # if your making an email app, your not sending an actual email. just for testing, testing multiple times will you were like spamming

# 38. Add tests for wait_for_db command 
    #FIX: this is requirements for running postgresql service, 
    
    #### root/app/app/tests/test_commands.py
    from unittest.mock import patch

    from django.core.management import call_command
    from django.db.utils import OperationalError # throws when the database is unavailable.
    from django.test import TestCase


    class CommandsTestCase(TestCase):

        def test_wait_for_db_ready(self):
            """Test waiting for db when db is available"""

            with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
                gi.return_value = True
                call_command('wait_for_db')
                self.assertEqual(gi.call_count, 1)

        @patch('time.sleep', return_value=None)
        def test_wait_for_db(self, ts):
            """Test waiting for db"""

            with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
                gi.side_effect = [OperationalError] * 5 + [True]
                call_command('wait_for_db')
                self.assertEqual(gi.call_count, 6)

# 39. Add wait_for_db command
    #create dirs and file root/app/core
                # /management/__init__.py
                # /commands/__init__.py
    
    #### ../commands/wait_for_db.py
    import time

    from django.db import connections 
    # to import the connections module which is what we can use to test if the
    # database connection is available.
    from django.db.utils import OperationalError
    # next we're going to import the operational error that Django will
    # throw if the database isn't available.
    from django.core.management.base import BaseCommand


    class Command(BaseCommand):
        """Django command to pause execution until database is available"""

        def handle(self, *args, **options):
        # So what these two allow is for passing in custom arguments and
        # options to our management commands so if we wanted to let's say customize the
        # wait time or something
            """Handle the command"""
            self.stdout.write('Waiting for database...')
            db_conn = None
            while not db_conn:
                try:
                    db_conn = connections['default']
                except OperationalError:
                    self.stdout.write('Database unavailable, waiting 1 second...')
                    time.sleep(1)

            self.stdout.write(self.style.SUCCESS('Database available!'))

# 40. Make docker compose wait for db

# now we have our wait for DB command we can go ahead and configure docker
# compose to use this command before it starts our django app.

    #### .../docker-compose.yml
    ...
    command: >
      sh -c "python manage.py wait_for_db && 
              python manage.py migrate &&
              python manage.py runserver 0.0.0.0:8000"
  
# 41. Test in browser
    > docker-compose up
    # ones running without errors, head over to 127.0.0.1:8000/admin
    > docker-compose run app sh -c "python manage.py createsuperuser" 
    # use this account to login to the admin page

############### ENOUGH FOR DEV SETUP HAHAHA ####################

# Create users app

    > docker-compose run --rm app sh -c "python manage.py startapp user" # --rm it removes the container after the command
    















	