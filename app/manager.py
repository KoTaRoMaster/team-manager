import asyncio

import typer

from app.database import AsyncSessionLocal
from app.enums import UserRole
from sqlalchemy import select

from app.models import User
from app.security import hash_password

app = typer.Typer()


@app.command()
async def _create_user(username: str, password: str, role: UserRole) -> None:
    async with AsyncSessionLocal() as session:
        exists = await session.scalar(
            select(User).where(User.name == username)
        )
        if exists:
            typer.secho(f"Пользователь {username} уже существует", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        session.add(User(
            name=username,
            email=f'{username}@email.com',
            hashed_password=hash_password(password),  # не хранить пароль в открытом виде!
            role=role.value,
        ))
        await session.commit()

    typer.secho(f"Создан {username} с ролью {role.value}", fg=typer.colors.GREEN)

@app.command()
def create_user(
    username: str,
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
    role: UserRole = typer.Option(UserRole.MEMBER, "--role", "-r", case_sensitive=False),
):
    asyncio.run(_create_user(username, password, role))

if __name__ == "__main__":
    app()
