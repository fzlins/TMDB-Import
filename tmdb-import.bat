@echo off

set DIR=%~dp0

cd /d %DIR%

python3 -m tmdb-import "https://www.mgtv.com/b/444964/16204816.html"

pause
