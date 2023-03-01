@echo off
echo This will start Aladdin GUI process on port 9002...
echo Do not run twice on the same port! (There is no automatic check...)
pause
call \miniconda3\condabin\activate.bat
python "MANBAMM-control-main\AladdinPilotGUI.py" 9002
echo Aladdin GUI process terminated (port 9002)
pause











