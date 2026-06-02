# Setup Instructions

### Step 1 - Install  `uv`

`uv` is a tool that manages Python and packages for you. You do not need Python installed first.

##### Mac / Linux - open a terminal and run
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

##### Windows - open PowerShell and run
```
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, quit and reopen your terminal so the `uv` command is available.

### Step 2 - Install Python and necessary packages
Run this single command in the same directory as these instructions
```
uv sync
```
This will automatically:
- Download and install Python 3.9
- Create an isolated virtual environment
- Install all required packages with the correct versionss

### Step 3 - Launch Jupyter
```
uv run jupyter notebook
```
Your browser will open with Jupyter. Navigate to the `notebooks/` folder in order to access the different exercises.
