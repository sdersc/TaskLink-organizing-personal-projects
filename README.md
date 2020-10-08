# organizing-personal-projects
Flask website for organizing personal projects and tasks

How to instal and use the website from your computer

1. Extract the archive
2. Open Command Prompt with administrator
3. Use "cd/..." to go to the directory where you extracted the archive
! The command must end in the Derscanu_Smaranda directory
4. Run the following for instalation
	$ py -3 -m venv venv
	$ venv\Scripts\activate
	$ pip install -e .
	$ set FLASK_APP=TaskLink
	$ set FLASK_ENV=development
	$ flask run
5. Open a web browser
6. Search 127.0.0.1:5000

! For future openings just run the following in cmd from anywhere in your computer
	$ set FLASK_APP=TaskLink
	$ set FLASK_ENV=development
	$ flask run
