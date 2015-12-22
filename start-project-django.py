# start-project-django.py#
# https://github.com/tdsymonds/start-project-django
# A python script to create a new Django project on a Debian/Ubuntu os.
# Nginx, Gunicorn & Django stack using Supervisor with a MySQL DB
# version 1.0, Dec. 2015
# by Tom Symonds

import os
import pwd
import grp
import getpass
import sys



#---- CONFIGURATION ----#
username = 'username'			# The system user that will be created

db_name = 'mydb'				# The database name for our project
db_user = 'dbuser'				# The database user for our project
db_password = 'pass'			# The password for our database user

virtualenv_name = 'venv'		# The name of the virtual environment directory
repo_name = 'project'			# The name of the repo directory
project_name = 'my_project'		# The name of our project

domain_name = 'example.com'		# Your domain name or ip address

os_requirements = [				# Any os requirements can be added and removed
	'python-virtualenv',		# from the list.
	'libpq-dev',
	'python-dev',
	'nginx',
	'supervisor',
	'libmysqlclient-dev', 
	'python-mysqldb',
	'build-essential',
	'libjpeg-dev',
	'mysql-server',
]

requirements = [				# Any requirements can be added and removed
	'gunicorn==19.4.1',			# from the list.
	'mysql-python==1.2.5',
	'Django==1.9.0',
	'Pillow==3.0.0',
]





#---- DIRECTORY SETUP ----#
user_dir = '/home/%s' % username
virtualenv_dir = '%s/%s' % (user_dir, virtualenv_name)
repo_dir = '%s/%s' % (virtualenv_dir, repo_name)
project_dir = '%s/%s' % (repo_dir, project_name)
configuration_dir = '%s/configuration' % (repo_dir)


#---- CREATE FILE FUNCTION ----#
def create_file(filepath, content):
	""" 
	Function to create a file at the 
	specified filepath and set the owner
	to the user specified in the config 
	"""
	
	file = open(filepath,'w') 

	if type(content) == list:
		for elm in content:
			file.write(elm + ' \n')
		file.close()
	else:
		file.write(content)
		file.close()


	uid = pwd.getpwnam(username).pw_uid
	gid = grp.getgrnam(username).gr_gid

	os.chown(filepath, uid, gid)



#---- THE SCRIPT ----#
os.system('apt-get update')

os.system('apt-get install sudo')
os.system('adduser ' + username)
os.system('adduser ' + username + ' sudo')


# install os requirements
os_requirements_string = ' '.join(os_requirements)
os.system('apt-get install ' + os_requirements_string + ' -y')



# create database
db_root_password = getpass.getpass('Please enter mysql root password: ')

mysql_command_list = [
	'CREATE DATABASE %s;' % db_name,
	'ALTER DATABASE %s DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;' % db_name,
	'CREATE USER "%s"@"localhost" IDENTIFIED BY "%s";' % (db_user, db_password),
	'GRANT ALL ON %s.* TO "%s"@"localhost";' % (db_name, db_user),
	'FLUSH PRIVILEGES;'
]

for mysql_command in mysql_command_list:
	mysql_shell_string = "mysql -u root -p%s -e '%s' " % (db_root_password, mysql_command)
	os.system(mysql_shell_string)


# create virutal environment
command = 'su - %s -c "virtualenv %s"' % (username, virtualenv_dir)
os.system(command)


# install requirements
requirements_string = ' '.join(requirements)
command = 'su - %s -c "%s/bin/pip install %s"' % (username, virtualenv_dir, requirements_string)
os.system(command)


# create Django project
command = 'su - %s -c "mkdir %s"' % (username, repo_dir)
os.system(command)
command = 'su - %s -c "mkdir %s"' % (username, project_dir)
os.system(command)
command = 'su - %s -c "mkdir %s"' % (username, configuration_dir)
os.system(command)
command = 'su - %s -c "%s/bin/django-admin.py startproject %s %s"' % (username, virtualenv_dir, project_name, project_dir)
os.system(command)

# save requirements to file
filepath = '%s/os_requirements.txt' % configuration_dir
create_file(filepath, os_requirements)
filepath = '%s/requirements.txt' % configuration_dir
create_file(filepath, requirements)


# create media and static
command = 'su - %s -c "mkdir %s/media"' % (username, project_dir)
os.system(command)
command = 'su - %s -c "mkdir %s/static"' % (username, project_dir)
os.system(command)

# create gunicorn config file
gunicorn = """command = '%s/bin/gunicorn'
pythonpath = '%s'
bind = '127.0.0.1:8000'
""" % (virtualenv_dir, project_dir)

filepath = '%s/gunicorn.py' % configuration_dir
create_file(filepath, gunicorn)


# create supervisor file
supervisor = """[program:%s]
command=%s/bin/gunicorn -c %s/gunicorn.py %s.wsgi
autostart=true
autorestart=true
redirect_stderr=true
stderr_logfile=/var/log/%s.err.log
stdout_logfile=/var/log/%s.out.log
""" % (project_name, virtualenv_dir, configuration_dir, project_name, project_name, project_name)

filepath = '/etc/supervisor/conf.d/%s.conf' % project_name
create_file(filepath, supervisor)

os.system('supervisorctl reread')
os.system('supervisorctl update')



# nginx
os.system('service nginx start')
os.system('rm /etc/nginx/sites-available/default')

nginx_settings = """
server {
   server_name %s;

   access_log off;

   location /static/ {
      alias %s/static/;
   }

   location /media/ {
      alias %s/media/;
   }

   location / {
      proxy_pass http://127.0.0.1:8000;
      proxy_set_header X-Forwarded-Host $server_name;
      proxy_set_header X-Real-IP $remote_addr;
      add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
   }
} 
""" % (domain_name, project_dir, project_dir)

filepath = '/etc/nginx/sites-available/nginx'
create_file(filepath, nginx_settings)

os.system('ln -s /etc/nginx/sites-available/nginx /etc/nginx/sites-enabled/')
os.system('service nginx restart')


# End messages
message = """


************************************************************************************

Your project is now setup!

Navigate to %s and you should see the Django startup page.

There's a couple of bits you need to do now to complete the setup.

First activate the virtualenv by running:

source %s/bin/activate

Then open the settings file:

nano %s/%s/settings.py

And update the database settings to the details provided below this section.

Finally navigate to:

cd %s 

And run:

python manage.py migrate

This will create all the default Django tables in the database.

You are now ready to begin creating your application.

************************************************************************************

""" % (domain_name, virtualenv_dir, project_dir, project_name, project_dir)

sys.stdout.write(message)


# TODO: Write this to the settings file and run the migration
# db settings
db_settings = """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': '%s',
        'USER': '%s',
        'PASSWORD': '%s',
        'HOST': 'localhost', 
        'PORT': '3306',
    }
}


************************************************************************************


""" % (db_name, db_user, db_password)


sys.stdout.write(db_settings)

# switch to new user
command = 'su - %s' % username
os.system(command)