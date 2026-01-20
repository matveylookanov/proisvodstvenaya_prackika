@echo off
REM Запуск backend с созданием venv при первом старте

cd /d "%~dp0backend"

IF NOT EXIST ".venv" (
    echo Создаю виртуальное окружение...
    py -m venv .venv
)

call .venv\Scripts\activate.bat

IF NOT EXIST "metrics.db" (
    echo Устанавливаю зависимости...
    pip install --upgrade pip
    pip install -r requirements.txt
)

echo Запускаю сервер Uvicorn...
uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause

