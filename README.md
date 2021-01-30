# Getting Started

## Installing headless chromedriver
In order for the scripts in this repo to work you'll need to add the headless chromedriver and add it to your path. Follow the instructions on the chromium website to get the correct installation https://chromedriver.chromium.org/downloads.

## Setting up dependency management with pip, venv, and pip-tools

While in the project directory, create a virtual environment in the env/ folder
```
python -m venv env
```

Next, activate the environment.

On Windows, run:
```
env\Scripts\activate.bat
```

on MacOS, run:
```
source env/bin/activate
```

To deactivate your environment on both Windows or Mac, run:
```
deactivate
```

Once your environment is activated, add pip-tools to manage package versions:
```
python -m pip install pip-tools
```

Now install the current dependencies to the project:
```
pip-sync
```

If you need to add a dependency:
* Add the dependency directly to the **requirements.in** file
* Run `pip-compile` to generate a new **requirements.txt** file
* Run `pip-sync` to install the dependencies to the virtual environment

Then commit the modified **requirements.txt** and **requirements.in** files to the repo.
