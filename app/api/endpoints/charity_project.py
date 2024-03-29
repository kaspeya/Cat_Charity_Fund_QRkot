from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_active,
                                check_charity_project_exists,
                                check_charity_project_has_investment,
                                check_charity_project_updated_amount,
                                check_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import Donation
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investing import donation_process

router = APIRouter()


@router.get(
    '/',
    response_model_exclude_none=True,
    response_model=List[CharityProjectDB]
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает список всех проектов:
    - Доступно для всех посетителей.
    """
    charity_projects = await charity_project_crud.get_multi(session)
    return charity_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Создаёт благотворительный проект:
    - Только для суперпользователей.
    """
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(charity_project,
                                                    session)
    new_project = await donation_process(new_project, Donation, session)
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Редактирует проект:
    - Только для суперпользователей.
    - Закрытый проект нельзя редактировать.
    - Нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await check_charity_project_exists(project_id, session)
    charity_project = await check_charity_project_active(charity_project,
                                                         session)
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    if not obj_in.full_amount:
        charity_project = await charity_project_crud.update(
            charity_project, obj_in, session
        )
        return charity_project
    await check_charity_project_updated_amount(obj_in.full_amount,
                                               charity_project.invested_amount,
                                               session)
    charity_project = await charity_project_crud.update(charity_project,
                                                        obj_in,
                                                        session)
    charity_project = await donation_process(charity_project, Donation, session)
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет проект:
    - Только для суперпользователей.
    - Нельзя удалить проект, в который уже были инвестированы средства,
      его можно только закрыть.
    """
    charity_project = await check_charity_project_exists(project_id, session)
    await check_charity_project_has_investment(charity_project, session)
    return await charity_project_crud.delete(charity_project,
                                             session)
