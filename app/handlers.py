from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import NotFoundError, DuplicateError, DateValidationError, LoginError, RegisterError, \
    PasswordResetError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(PasswordResetError)
    async def password_reset_exception_handler(request: Request, exc: PasswordResetError):
        return JSONResponse(
            status_code=401,
            content={
                "error": 'Reset password failed',
                "message": f'{exc.message}',
            }
        )

    # Обработчик ошибки: Неправильная почта или пароль
    @app.exception_handler(RegisterError)
    async def login_exception_handler(request: Request, exc: RegisterError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": 'Register failed',
                "message": f'{exc.message}',
            }
        )

    # Обработчик ошибки: Неправильная почта или пароль
    @app.exception_handler(LoginError)
    async def login_exception_handler(request: Request, exc: LoginError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "error": 'login failed',
                "message": f'{exc.message}',
            }
        )

    # Обработчик ошибки: Объект не найден
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "detail": f"{exc.entity} с {exc.entity_data} не найден",
            },
        )

    # Обработчик ошибки: Дублирование уникальных данных
    @app.exception_handler(DuplicateError)
    async def duplicate_handler(request: Request, exc: DuplicateError):
        return JSONResponse(
            status_code=409,
            content={
                "error": "duplicate",
                "detail": f"Значение '{exc.value}' для поля '{exc.field}' уже существует",
            },
        )

    # Обработчик ошибки: Некорректные даты
    @app.exception_handler(DateValidationError)
    async def date_validation_handler(request: Request, exc: DateValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "date_validation",
                "detail": exc.detail,
            },
        )

    # Переопределение дефолтной ошибки валидации Pydantic (Убираем loc и делаем понятный JSON)
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            locs = [str(loc) for loc in error["loc"] if loc != "body"]
            field = " -> ".join(locs) if locs else "body"
            errors.append({"field": field, "message": error["msg"]})

        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "detail": errors},
        )
