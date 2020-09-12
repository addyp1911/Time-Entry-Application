# Time-Entry-Application
Time Entry App is a Django application to track user's time to tasks in a project with the use of model viewsets and django rest framework.
# Tech stack
Web application based on Django Rest Framework (server-side)

# Features
Authentication
- [x] Signup using email/password

Time entry
- [x] Can add time entry
- [x] Can track time spent on a task and stop a time entry tracking
- [x] Can list time entries
- [x] Delete time entry

Task
- [x] Can add tasks with name, project and timestamp
- [x] Delete/Update/List tasks for an authenticated user
- CRUD tasks


# Developer notes
Can clone the repository using command: git clone https://github.com/addyp1911/Time-Entry-Application
Hosted on AWS EC2 server on host- http://15.206.28.50:8080/

Install packages
```pip install

Prerequisites
=============
Django==3.0.6
djangorestframework==3.11.0
djangorestframework-simplejwt==4.4.0
python-dotenv==0.14.0
```

Getting Started
===============
#. Install prerequisites
#. Sign up as a user with email/username and log in
#. JWT authentication gives out an access token which can be used to create tasks, projects, and add time entries to each task.
#. List out all time entries for tasks of previous days and you can manage your tasks well.


