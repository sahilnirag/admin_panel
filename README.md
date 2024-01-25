# Zukti Inovations Admin Panel

Nirag-Infotech, offer end-to-end web development solutions empowering various enterprises to transform their businesses. Our expertise grows with your business constantly and our intuitive web solutions best suit your business requirements.


# Prerequisites
 To run this project you must have installed these Packages and dependencies.
	
 1.Python3.

	sudo apt-get install python3
	
 2.pip3.
	
	sudo apt-get install python3-pip
	
## Env Create and activate.

Virtual Environment Creation.
    
    python3 -m venv env

For Activation of Environment.    
    
    source venv/bin/activate

## Installation

Use the package manager requirements.

	pip3 install -r requirement.txt

# Getting Started
	
1. Remove migrations from all apps.

2. Run this command for migrations.

   python3 manage.py makemigrations
		
3. Run this command for migrate 
	
   python3 manage.py migrate
		
4. Run this command to create superuser.
	
   python3 manage.py createsuperuser

# Running the project:

To run this project run this command on your terminal:

	python3 manage.py runserver
