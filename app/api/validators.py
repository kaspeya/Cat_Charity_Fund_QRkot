from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
) -> None:
    """Проверка на уникальность имени благотворительного проекта."""
    project_id = await charity_project_crud.get_id_by_name(project_name, session)
    if project_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_charity_project_exists(
    charity_project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Проверка на существование благотворительного проекта по id."""
    charity_project = await charity_project_crud.get_project_by_id(
        charity_project_id,
        session
    )
    if not charity_project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден.'
        )
    return charity_project


async def check_charity_project_active(
    charity_project: CharityProject,
    session: AsyncSession,
) -> CharityProject:
    """Проверяет, не закрыт ли проект."""
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
    return charity_project


async def check_charity_project_has_investment(
    charity_project: CharityProject,
    session: AsyncSession,
) -> None:
    """Проверяет внесены ли уже средства в проект."""
    if charity_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )


async def check_charity_project_updated_amount(
    obj_in_full_amount: int,
    charity_project_inv_amount: int,
    session: AsyncSession
) -> None:
    """Проверят возможность для редактирования проекта."""
    if obj_in_full_amount < charity_project_inv_amount:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Нельзя установить требуемую сумму меньше уже вложенной.'
        )
