@echo off
cd /d "C:\RODRIGO_ARBONES_VAZQUEZ\UNIVERSIDAD\MASTER\ICAI\MUIAAp\DE\biodatapharma"
"C:\Users\arbon\.local\bin\uv.exe" run python -m biodatapharma.schezofrenia_esquizofrenia >> tarea.log 2>&1
exit /b %ERRORLEVEL%