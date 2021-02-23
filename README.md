# Getting Started

While in the project directory, create a virtual environment in the env/ folder
```
python -m venv python
```

Next, activate the environment.

On Windows, run:
```
env\Scripts\activate.bat
```

on MacOS, run:
```
source python/bin/activate
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
* Run `pip-compile --upgrade-package 'package-to-install==2.0.0'` to generate a new **requirements.txt** file
* Run `pip-sync` to install the dependencies to the virtual environment

Then commit the modified **requirements.txt** and **requirements.in** files to the repo.
