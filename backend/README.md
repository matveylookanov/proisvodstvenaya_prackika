## Backend (FastAPI)

### Установка и запуск (Windows PowerShell)

Все команды выполнять из корня проекта `proisvodstvenaya_prackika`:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

После запуска:
- API: `http://127.0.0.1:8000`
- Проверка: `http://127.0.0.1:8000/health`
- Фронтенд: `http://127.0.0.1:8000/` (отдаётся как статика из папки `frontend`)

### Основные эндпоинты

- `GET /health` — проверка, что сервер жив  
- `POST /metrics` — сохранить один замер  
- `GET /metrics?limit=10` — получить последние замеры

