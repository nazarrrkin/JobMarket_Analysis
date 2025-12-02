# JobMarket Analysis - приложение для сбора данных с онлайн биржы труда и его анализа

### Краткое описание
Веб‑приложение, состоящее из backend (Python, Django) и frontend (TypeScript, React/Vite) частей. Оно собирает данные с популярного портала вакансий "HeadHunter", сохраняет данные в csv файлы, а затем в базу данных. Анализ и визуализация происходит в PowerBI.

### Настройки окружения

Создайте/активируйте виртуальное окружение и установите зависимости:

```
python -m venv .venv
.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

### Сбор и обработка данных
```
psql -U postgres -c "CREATE DATABASE hh_db;" 2>$null
cd data_collecting
python crawler.py
psql -U postgres -d hh_db -f csv_handler.sql
```


Для одновременной работы клиента и сервера откройте два терминала.

### Терминал 1: Frontend

Перейдите в папку фронтенда, установите зависимости и запустите режим разработки:

```bash
cd frontend
npm i
npm run dev
```

### Терминал 2: Backend

Перейдите в папку бэкенда и запустите сервер:

```
cd backend
python manage.py runserver
```

### Просмотр данных в БД

```
cd backend
sqlite3 db.sqlite3
```
