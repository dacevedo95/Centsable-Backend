# PingdBackend
This repository is built on python and flask, and is the backend service to the iOS app Ping'd. Below will explain how to run the API on your local machine.

## Getting Started
Getting the API to run on your local machine is not difficult, but does require some preliminary steps.

After cloning the repository onto your computer, run the following command to hop into the project root directory.

```
$ cd PingdBackend
```

The following steps will all be executed in the project's root directory. These steps are:

1. [Creating a virtual environment](#creating-a-virtual-environment)
2. [Installing dependencies](#installing-dependencies)
3. [Setting the environment variables](#setting-the-environment-variables)
4. [Running and testing the API](#running-and-testing-the-api)

### Creating a virtual environment
The first step before installing any dependencies is to create a virtual environment for our application to live in. These commands are:

```
### For Python version 3
$ python3 -m venv venv

### For Python version 2
$ python -m venv venv
```
This will create a new folder in the project called <b>venv</b>.

The next step is to activate the virtual environment so that we can start to install dependencies into it. Depending on what machine you are using (Windows vs. Mac), this command could vary.

For Windows:
```
$ venv\Scripts\activate
(venv) $ _
```
For Mac/Linux:
```
$ source venv/bin/activate
(venv) $ _
```
Now that we have created and activated our virtual environment, it is time to install the dependencies.

### Installing dependencies
All dependencies are neatly defined within the requirements.txt file. <b>Before installing, make sure the virtual environment is active!</b> Once you confirm that it is active, run the following command:

```
(venv) $ pip install -r requirements.txt
```

To verify that the dependencies are installed, you can run the python shell and try importing Flask.

```
(venv) $ python
>>> import flask
>>>
```

If no error shows, then you have successfully installed the dependencies into the virtual environment.

### Setting the environment variables
The last step before running and testing the API is to install the following environment variables. <b>Again, make sure that the virtual environment is still activated before setting the environment variables.</b>
```
### For Mac/Linux:
(venv) $ export FLASK_APP=application.py
(venv) $ export FLASK_ENV=development
(venv) $ export FLASK_DEBUG=1

### For Windows:
(venv) $ set FLASK_APP=application.py
(venv) $ set FLASK_ENV=development
(venv) $ set FLASK_DEBUG=1
```
Without going into too much detail, the above defines the environment we created in step 1 as a "Development" environment only meant for debugging (FLASK_DEBUG=1). It also defines an entry point to our application as "application.py". More information can be found [here](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).

### Running and testing the API
Finally, we are all set to run and hit the applications endpoint. In the terminal, with the virtual environment still active, run the following command:

```
(venv) $ flask run
```

The output of this command should look a little something like this:

```
(venv) $ flask run
* Serving Flask app "application.py" (lazy loading)
* Environment: development
* Debug mode: on
* Restarting with stat
* Debugger is active!
* Debugger PIN: 285-532-468
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

These messages now imply that our app is running in a "Development" environment and that "Debug mode" is on.

If you open up your browser and type in the URL http://127.0.0.1:5000/, or if you open up (Postman)[https://www.getpostman.com/] and send a GET request to http://127.0.0.1:5000/, you should see the following output:

```
{
  "message": "Hello, World!"
}
```

If you see this message, you have successfully run the app on your local machine, and you are finished with getting started
