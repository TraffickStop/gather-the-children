# Getting Started

## Setting up dependency management with venv

While in the project directory, create a virtual environment in the env/ folder
```
python3 -m venv env
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

Once your environment is activated, you can add the current dependencies to the project by running:
```
pip install -r requirements.txt
```

If you add a new dependency to the project using pip install you will need to write these dependencies to the requirements.txt file so other team members have the dependencies.
While your virtual environment is active, run:
```
pip freeze > requirements.txt
```

Then commit the modified requirements.txt to the repo.
