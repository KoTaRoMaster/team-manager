<h2 align="center">Blog FastAPI</h2>


### Описание проекта:
Блог написаный на FastAPI.
- JWT авторизация
- CRUD пользователей
- CRUD категорий
- CRUD статей
- Отправка Email

### Инструменты разработки

**Стек:**
- Python >= 3.14
- FastAPI == 0.52.0
- PostgreSQL


## Разработка


##### 1) Клонировать репозиторий:

    git clone https://github.com/KoTaRoMaster/team-manager.git
    
##### 2) Перейти в директорию проекта:

    cd team-manager

##### 3) Создать виртуальное окружение:

    python -m venv venv
    
##### 4) Скопировать образ .env файла для корректной работы:

       cp .env.example .env

##### 5) Собрать образы и поднять приложение и базу данных одной командой:

    docker-compose.yml up --build

##### 6) Выполнить команду для выполнения миграций:

    docker-compose exec web alembic upgrade head

##### 7) Перейти по адресу

    http://127.0.0.1:8000/docs
    
## License

[BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause)

Copyright (c) 2020-present, DJWOMS - Omelchenko Michael



