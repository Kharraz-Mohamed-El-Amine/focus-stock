@echo off
title Focus Stock - Serveur Local
cd /d "%~dp0"
echo ====================================================
echo  Lancement de l'application Focus Quality - Stock
echo ====================================================
echo.
echo Ouverture du navigateur sur http://127.0.0.1:8000/ ...
start http://127.0.0.1:8000/
echo.
echo Demarrage du serveur Django...
echo (Pour arreter le serveur, fermez cette fenetre ou faites Ctrl + C)
echo.
call .\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause
