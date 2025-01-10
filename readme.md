# Сервис рекомендаций людей на основе:
 1. Места жительсва
 2. Описания профиля
 3. Профессии
 4. Возраста
 5. Опыта  
up-tp-work:  
место работы  
друзья  
события  



## Структура проекта
```            
.
├── .env
├── .gitignore
├── alembic.ini
├── app
│   ├── migrations
│   ├── city
│   │   ├── dao.py
│   │   ├── models.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── dao
│   │   └── base.py
│   ├── recommendation
│   │   ├── dao.py
│   │   ├── models.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── tasks
│   │   ├── celery_app.py
│   │   ├── scheduled.py
│   │   └── tasks.py
│   └── users
│   │   ├── dao.py
│   │   ├── models.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
├── docker
├── docker-compose.yml
├── Dockerfile
├── readme.md
├── requirements.txt
└── venv
```
## Запуск приложения
Для запуска FastAPI используется веб-сервер uvicorn. Команда для запуска выглядит так:  
```
uvicorn app.main:app --reload
```  

Ее необходимо запускать в командной строке, обязательно находясь в корневой директории проекта.

### Celery & Flower
Для запуска Celery используется команда  
```
celery --app=app.tasks.celery:celery worker -l INFO -P solo
```
Обратите внимание, что `-P solo` используется только на Windows, так как у Celery есть проблемы с работой на Windows.  
Для запуска Flower используется команда  
```
celery --app=app.tasks.celery:celery flower
``` 

### Dockerfile
Для запуска веб-сервера (FastAPI) внутри контейнера необходимо раскомментировать код внутри Dockerfile и иметь уже запущенный экземпляр PostgreSQL на компьютере.
Код для запуска Dockerfile:  
```
docker build .
```  
Команда также запускается из корневой директории, в которой лежит файл Dockerfile.
### Docker compose
Для запуска всех сервисов (БД, Redis, веб-сервер (FastAPI), Celery, Flower, Grafana, Prometheus) необходимо использовать файл docker-compose.yml и команды
```
docker compose build
docker compose up
```
Причем `build` команду нужно запускать, только если вы меняли что-то внутри Dockerfile, то есть меняли логику составления образа.