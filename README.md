<h2 align="center">Blog FastAPI</h2>


### Описание проекта:
Менеджер команД написаный на FastAPI.
- JWT авторизация
- CRUD пользователей (users)
- CRUD команд (teams)
- CRUD задач (tasks)
- CRUD встреч (meetings)
- Календарь

### Инструменты разработки

**Стек:**
- Python >= 3.14
- FastAPI == 0.141.1
- PostgreSQL
- Docker

## Разработка


##### 1) Клонировать репозиторий:

    git clone https://github.com/KoTaRoMaster/team-manager.git
    
##### 2) Перейти в директорию проекта:

    cd team-manager

##### 3) Создать виртуальное окружение:

    python -m venv venv
    
##### 4) Скопировать образ .env файла для корректной работы(PowerShell):

    cp .env.example .env

##### 5) Собрать образы и поднять приложение и базу данных одной командой:

    docker compose up --build


##### 6) Перейти по адресу

    http://127.0.0.1:8000/docs

#### Одна команда для всех пунктов

     git clone https://github.com/KoTaRoMaster/team-manager.git; cd team-manager; python -m venv venv; cp .env.example .env; docker compose up --build; docker compose exec web alembic upgrade head



