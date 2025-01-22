@echo off

REM Navigate to your project folder (adjust the path as needed):
cd C:\Users\pedro\PycharmProjects\hycreator2

REM If the .venv folder does not exist, create it
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate the virtual environment
call .venv\Scripts\activate

REM Install dependencies
echo Installing requirements...
pip install -r requirements.txt

REM Run the Python GUI
echo Starting manager_gui.py...
python manager_gui.py

REM Optional: prevent the window from closing immediately
pause
