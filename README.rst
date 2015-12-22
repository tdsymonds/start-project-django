start-project-django
=====================
When I first started out learning the Django framework, I remember finding it really challenging to setup a server to host a Django project, so I've made this script to try and help people overcome this initial hurdle, so they can move straight on to the fun part, building an application. 

If you do have experience then not to worry, this script should hopefully make configuring the server very quick and easy!

This is my preferred setup, using an Nginx, Gunicorn & Django stack using Supervisor and with a MySQL DB.

**This script is designed to run on a clean server, do not run on a server with existing projects, or you may lose files or get unexpected results!**

I've tested this script on both Debian and Ubuntu machines.


Quick Start
-----------
1. Login as root on your clean install of an Ubuntu or Debian machine.
2. Upload the start-project-django.py file via ftp (or create a new file and copy and paste the content over).
3. Amend the configuration section of the python file to your settings (if you're unsure about the os_requirements and requirements then leave what I have entered for the default):

  username = 'username'           # The system user that will be created

  db_name = 'mydb'                # The database name for our project
  db_user = 'dbuser'              # The database user for our project
  db_password = 'pass'            # The password for our database user

  virtualenv_name = 'venv'        # The name of the virtual environment directory
  repo_name = 'project'           # The name of the repo directory
  project_name = 'my_project'     # The name of our project

  domain_name = 'example.com'     # Your domain name or ip address

  os_requirements = [             # Any os requirements can be added and removed
      'python-virtualenv',        # from the list.
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

  requirements = [                # Any requirements can be added and removed
      'gunicorn==19.4.1',         # from the list.
      'mysql-python==1.2.5',
      'Django==1.9.0',
      'Pillow==3.0.0',
  ]


4. Run the command:
  python start-project-django.py

The script will now run and create your project. 

NOTE: You will be prompted for passwords at a couple of points, so follow the instructions given when prompted.

5. Once the script has complete, if you navigate to your domain or ip you will see the Django start page.
6. Then follow the final instuctions to run the database migration to create Django's default tables in the database.

Good luck!



Useful links
------------
Some links that you may find useful:

https://docs.djangoproject.com/en/1.9/intro/tutorial01/
https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-supervisor-on-ubuntu-and-debian-vps

