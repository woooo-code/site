# <a name="top">Matcha</a>

Matcha is a full-stack mobile responsive web application for online dating. A user is able to register, connect, fill his/her profile, search and look into the profile of other users, like them, and chat with those that "liked" back.

Matcha is deployed on Heroku [here](https://match-a.herokuapp.com).

## Contents

[Tehnologies Used](#technology) | [Preview Matcha](#preview) | [Features](#features) | [Run Matcha Locally](#run) | [Credits](#credits)

## <a name="technology">Technologies Used</a>

* Flask-SQLAlchemy
* Flask-SocketIO
* Flask-Limiter
* Flask-WTF
* Flask-Login
* Flask-Bcrypt
* PostgreSQL
* Jinja2
* JavaScript (AJAX/JSON)
* HTML, CSS, Bootstrap
* Google Geocoding API
* Google Maps API
* Google reCAPTCHA API

<a href="#top">↥ back to top</a>

## <a name="preview">Preview Matcha</a>

![Matcha Homepage](/resources/preview/Landingpage.png)

![Sorting Demo](/resources/preview/sort_filter_demo-min.gif)

![Notification Demo](/resources/preview/live_notif_demo-min.gif) 

![Chat Demo](/resources/preview/chat_demo-min.gif)

<a href="#top">↥ back to top</a>

## <a name="features">Features</a>

* User registration with account activation via email
* Login, logout, and forgot password processes
* 'My Profile' page displays information and pictures provided by the user; functionalities include:
	- deleting or uploading up to five photos and setting one as profile picture
	- updating location, age, gender, preference, biography and interest tags
	- preview profile as another user
* 'My Matches' page displays custom list of suggested matches for each user; functionalities include:
	- sorting by age, distance, number of matching tags, and rating
	- filtering by range of age, range of rating, location, and list of tags
	- clicking the like/dislike button for any specific user 
	- visiting a user's profile
* 'Chats' page displays list of connected users with whom the current user can chat with; clicking on a username loads a chat box that displays messages between both users
* 'Notifications' page displays notifications for the following events:
	- user received a "like"
	- user's profile has been viewed
	- user received a message
	- a "liked" user "liked" back
	- user has been "unliked"

	A user can mark each notification as read or mark all as read. Live notifications are polled every 5 seconds and a count of 		unread notifications are shown on navigator bar.
* 'Past Visitors' page displays the username, profile picture and the most recent time when another user visited the current user's profile page
* 'Liked Users' page displays information for all users that have been liked by the current user
* 'Blocked Users' page displays inforamation for all users that have been blocked by the current user; clicking on the user's information card will unlock the user
* 'Settings' page displays a form for users to change his/her first name, last name, email, username and/or password 
* 'Reported Users' page shows a list of all users who were reported including a total count of that occurance. Only an admin account can access this page.

<a href="#top">↥ back to top</a>

## <a name="run">Run Matcha Locally</a>

#### `Step 1` - clone the repo

```bash
$ git clone https://github.com/serena-zhu/Matcha.git
```

#### `Step 2` - set up virtual environment

```bash
$ pip3 install virtualenv
$ cd Matcha
$ virtualenv env
$ source env/bin/activate
(env) $ pip3 install -r requirements.txt
```

#### `Step 3` - create new database named matcha

```bash
(env) $ psql postgres
postgres=# CREATE DATABASE matcha;
postgres=# \q
```

#### `Step 4` - set up configurations

* In app.py (line 4): change flask_app = create_app('prod') to flask_app = create_app('dev')
* In config/dev.py (line 3): change SQLALCHEMY_DATABASE_URI with your username and password
* In seed.py (line 23): change flask_app = create_app('prod') to flask_app = create_app('dev')

#### `Step 5` - seed 500 users to database

```bash
(env) $ python3 seed.py
```

#### `Step 6` - start flask server

```bash
(env) $ python3 app.py
```

Go to localhost:5000 on your browser to see the landing page.

<a href="#top">↥ back to top</a>

## <a name="credits">Credits</a>

#### Authors
This project was built on Kanban methodology in a team of two:

| [<img src="https://avatars3.githubusercontent.com/u/4443041?s=460&v=4" width="100px"/><br /><sub><b>Joey Chung</b></sub>](https://github.com/jchung05) | [<img src="https://avatars0.githubusercontent.com/u/31867829?s=460&v=4" width="100px"/><br /><sub><b>Serena Zhu</b></sub>](https://github.com/serena-zhu) |
|---|---|

#### Special Thanks
Special thanks to friends and students at 42 Silicon Valley for feedback, suggestions, and user testing. 

Photo credits go to photographers who posted them on [Unsplash](https://unsplash.com).




Full Stack Python logo Full Stack Python
All topics | Blog | @fullstackpython | Facebook | Books & Videos | What's new?
Setting up PostgreSQL with Python 3 and psycopg on Ubuntu 16.04
Post updated by Matt Makai on December 25, 2017. Originally posted on May 18, 2016.

PostgreSQL is a powerful open source relational database frequently used to create, read, update and delete Python web application data. Psycopg2 is a PostgreSQL database driver that serves as a Python client for access to the PostgreSQL server. This post explains how to install PostgreSQL on Ubuntu 16.04 and run a few basic SQL queries within a Python program.

We won't cover object-relational mappers (ORMs) in this tutorial but these steps can be used as a prerequisite to working with an ORM such as SQLAlchemy or Peewee.
Tools We Need

Our walkthrough should work with either Python 2 or 3 although all the steps were tested specifically with Python 3.5. Besides the Python interpreter, here are the other components we'll use:

    Ubuntu 16.04.2 (these steps should also work fine with other Ubuntu versions)
    pip and virtualenv to handle the psycopg2 application dependency
    PostgreSQL

If you aren't sure how to install pip and virtualenv, review the first few steps of the how to set up Python 3, Bottle and Green Unicorn on Ubuntu 16.04 LTS guide.
Install PostgreSQL

We'll install PostgreSQL via the apt package manager. There are a few packages we need since we want to both run PostgreSQL and use the psycopg2 driver with our Python programs. PostgreSQL will also be installed as a system service so we can start, stop and reload its configuration when necessary with the service command. Open the terminal and run:

sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common python-psycopg2 build-essential python3-dev python3-pip

Enter your sudo password when prompted and enter 'yes' when apt asks if you want to install the new packages.

After a few moments apt will finish downloading, installing and processing.

We now have PostgreSQL installed and the PostgreSQL service is running in the background. However, we need to create a user and a database instance to really start using it. Use the sudo command to switch to the new "postgres" account.
sudo service postgresql start
sudo -i -u postgres

Within the "postgres" account, create a user from the command line with the createuser command. PostgreSQL will prompt you with several questions. Answer "n" to superuser and "y" to the other questions.

createuser matt -P --interactive

Awesome, now we have a PostgreSQL user that matches our Ubuntu login account. Exit out of the postgres account by pressing the "Ctrl" key along with "d" into the shell. We're back in our own user account.

Create a new database we can use for testing. You can name it "testpython" or whatever you want for your application.

createdb testpython

Now we can interact with "testpython" via the PostgreSQL command line tool.
Interacting with PostgreSQL

The psql command line client is useful for connecting directly to our PostgreSQL server without any Python code. Try out psql by using this command at the prompt:

psql testpython

The PostgreSQL client will connect to the localhost server. The client is now ready for input:

Try out PostgreSQL's command prompt a try with commands such as \dt and \dd. We can also run SQL queries such as "SELECT * from testpython", although that won't give us back any data yet because we have not inserted any into the database. A full list of PostgreSQL commands can be found in the psql documentation.
Installing psycopg2

Now that PostgreSQL is installed and we have a non-superuser account, we can install the psycopg2 package. Let's figure out where our python3 executable is located, create a virtualenv with python3, activate the virtualenv and then install the psycopg2 package with pip. Find your python3 executable using the which command.

which python3

We will see output like what is in this screenshot.

Create a new virtualenv in either your home directory or wherever you store your Python virtualenvs. Specify the full path to your python3 installation.

# specify the system python3 installation
virtualenv --python=/usr/bin/python3 venvs/postgrestest

Activate the virtualenv.

source ~/venvs/postgrestest/bin/activate

Next we can install the psycopg2 Python package from PyPI using the pip command.

pip install psycopg2

Sweet, we've got our PostgreSQL driver installed in our virtualenv! We can now test out the installation by writing a few lines of Python code.
Using PostgreSQL from Python

Launch the Python REPL with the python or python3 command. You can also write the following code in a Python file such as "testpostgres.py" then execute it with python testpostgres.py. Make sure to replace the "user" and "password" values with your own.

import psycopg2

try:
    connect_str = "dbname='testpython' user='matt' host='localhost' " + \
                  "password='myOwnPassword'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    # create a psycopg2 cursor that can execute queries
    cursor = conn.cursor()
    # create a new table with a single column called "name"
    cursor.execute("""CREATE TABLE tutorials (name char(40));""")
    # run a SELECT statement - no data in there, but we can try it
    cursor.execute("""SELECT * from tutorials""")
    conn.commit() # <--- makes sure the change is shown in the database
    rows = cursor.fetchall()
    print(rows)
    cursor.close()
    conn.close()
except Exception as e:
    print("Uh oh, can't connect. Invalid dbname, user or password?")
    print(e)

When we run the above code we won't get anything fancy, just an empty list printed out. However, in those few lines of code we've ensured our connection to our new database works and we can create new tables in it as well as query them.

That's just enough of a hook to get started writing more complicated SQL queries using psycopg2 and PostgreSQL. Make sure to check out the PostgreSQL, relational databases and object-relational mappers (ORMs) pages for more tutorials.

Questions? Tweet @fullstackpython or post a message on the Full Stack Python Facebook page.

See something wrong in this post? Fork this page's source on GitHub and submit a pull request.
More Resources
PostgreSQL and Ubuntu logos. Copyright their respective owners.
Operating Systems
Ubuntu
Relational Databases
PostgreSQL
...or view all topics.
Matt Makai 2012-2020






<a href="#top">↥ back to top</a>
