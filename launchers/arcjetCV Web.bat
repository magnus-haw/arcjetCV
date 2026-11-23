@echo off
REM Double-click on Windows to launch arcjetCV Web in your browser.
where conda >nul 2>nul && call conda activate arcjetcv
python -c "import flask" 2>nul || (echo Installing Flask (one time)... & python -m pip install flask)
python -m arcjetCV.webapp %*
pause
