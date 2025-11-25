***Agri-Naija Centre***
**by Effiong Uyo**


***OVERVIEW***
______________________________________________


A web application that provides business-oriented agricultural knowledge to aspiring farmers in Nigeria.

***About the Project***
______________________________________________

Agri-Naija Centre is designed to provide accessible, localized agricultural business information.
Users can read guides, search for content, filter by category, and contact administrators.
Admins can log in to add, edit, and delete articles.



***DEMO***
_____________________________________________






***Technologies Used***
____________________________________________

 - Python 3
 - Flask
 - Flask-Admin
 - Flask-Login
 - Flask-Mail
 - Flask-SQLAlchemy
 - Flask-Caching
 - HTML5 + CSS3 + JS
 - SQLite (local)
 - PostgreSQL (Render)
 - Gunicorn
 - Render Web Service (deployment)



***How to Set Up the Project (Local Installation)***
___________________________________________________________

Follow these steps EXACTLY to run the project locally.

1. Clone the Repository;
   
git clone https://github.com/Effiong06/Agri-Naija-Centre.git;

cd Agri-Naija-Centre

3. Create a Virtual Environment
 - python3 -m venv venv;
 - source venv/bin/activate      # Linux/Mac
 - venv\Scripts\activate         # Windows

4. Install Requirements
 - pip install -r requirements.txt

5. Configure Environment Variables

Create a .env file in the project root and add:

SECRET_KEY=your_secret_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_email_password_or_app_password

5. Initialize the Database
flask shell
 - from app import db
 - db.create_all()
 -  exit()


An initial admin user is automatically created:

username: admin
password: supersecretpassword

Change this immediately.

6. Run the App
 - python app.py


Your local app will run at:

http://127.0.0.1:5000




***Deployment on Render (Step-By-Step)***
________________________________________________

1. Push code to GitHub

Make sure your latest code is committed and pushed.

2. Visit Render.com → Create New Web Service
3. Configure Build Settings
Setting	Value
Build Command	 - pip install -r requirements.txt
Start Command	 - gunicorn app:app
Environment	Python 3
4. Add Environment Variables

Add:

SECRET_KEY=
EMAIL_USER=
EMAIL_PASS=

5. Deploy

Render builds your app and gives you a public URL.



***Project Structure***
___________________________________________

 - project/: - 
-              - app.py
-              - requirements.txt
-              - static/:-
-                          - css/
-                          - js/
-              - templates/:-
-                             - base.html
-                             - index.html
-                             - article_list.html
-                             - article_detail.html
-                             - contact.html
-                             - admin/:- 
-                                       - admin_login.html
-                                       - custom_admin_index.html
-               - instance/:-
-                             - site.db
-               - venv/




**Default Admin Account**

Created automatically on first run:

Username:- admin; Password:- supersecretpassword

**Contact Form**

Uses Gmail SMTP.
If using Gmail, enable App Passwords and use that as EMAIL_PASS.

**License**

This project is for educational use.
