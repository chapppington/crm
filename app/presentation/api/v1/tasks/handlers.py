from datetime import date
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from presentation.api.dependencies import (
    get_current_user_id,
    get_organization_id,
    get_organization_member,
)
from presentation.api.filters import PaginationOut
from presentation.api.schemas import ApiResponse
from presentation.api.v1.tasks.schemas import (
    CreateTaskRequestSchema,
    TaskListResponseSchema,
    TaskResponseSchema,
    UpdateTaskRequestSchema,
)

from application.container import init_container
from application.mediator import Mediator
from application.sales.commands import (
    CreateTaskCommand,
    UpdateTaskCommand,
)
from application.sales.queries import (
    GetTaskByIdQuery,
    GetTasksQuery,
)
from domain.organizations.entities import OrganizationMemberEntity
from domain.sales.filters import TaskFilters


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[TaskListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[TaskListResponseSchema]},
    },
)
async def get_tasks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    deal_id: UUID | None = Query(default=None),
    only_open: bool | None = Query(default=None),
    due_before: date | None = Query(default=None),
    due_after: date | None = Query(default=None),
    is_done: bool | None = Query(default=None),
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[TaskListResponseSchema]:
    """Получить список задач с фильтрацией и пагинацией."""
    mediator: Mediator = container.resolve(Mediator)

    filters = TaskFilters(
        organization_id=organization_id,
        page=page,
        page_size=page_size,
        deal_id=deal_id,
        only_open=only_open,
        due_before=due_before,
        due_after=due_after,
        is_done=is_done,
    )

    role = member.role.as_generic_type()
    query = GetTasksQuery(
        filters=filters,
        user_id=user_id,
        user_role=role.value,
    )
    tasks, total = await mediator.handle_query(query)

    items = [TaskResponseSchema.from_entity(task) for task in tasks]

    pagination = PaginationOut(
        limit=page_size,
        offset=(page - 1) * page_size,
        total=total,
    )

    return ApiResponse[TaskListResponseSchema](
        data=TaskListResponseSchema(
            items=items,
            pagination=pagination,
        ),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[TaskResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[TaskResponseSchema]},
    },
)
async def create_task(
    request: CreateTaskRequestSchema,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[TaskResponseSchema]:
    """Создать новую задачу."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    command = CreateTaskCommand(
        deal_id=request.deal_id,
        title=request.title,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
        description=request.description,
        due_date=request.due_date,
    )

    task, *_ = await mediator.handle_command(command)

    return ApiResponse[TaskResponseSchema](
        data=TaskResponseSchema.from_entity(task),
    )


@router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[TaskResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[TaskResponseSchema]},
    },
)
async def get_task(
    task_id: UUID,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[TaskResponseSchema]:
    """Получить задачу по ID."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    query = GetTaskByIdQuery(
        task_id=task_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
    )
    task = await mediator.handle_query(query)

    return ApiResponse[TaskResponseSchema](
        data=TaskResponseSchema.from_entity(task),
    )


@router.patch(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[TaskResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[TaskResponseSchema]},
    },
)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequestSchema,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[TaskResponseSchema]:
    """Обновить задачу."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    command = UpdateTaskCommand(
        task_id=task_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
        title=request.title,
        description=request.description,
        due_date=request.due_date,
        is_done=request.is_done,
    )
    task, *_ = await mediator.handle_command(command)

    return ApiResponse[TaskResponseSchema](
        data=TaskResponseSchema.from_entity(task),
    )
