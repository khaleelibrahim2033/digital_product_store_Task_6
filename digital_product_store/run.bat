@echo off
echo Start backend in one terminal:
echo cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload --port 8000
echo.
echo Start frontend in another terminal:
echo cd frontend ^&^& npm install ^&^& npm run dev
pause
