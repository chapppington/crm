from functools import lru_cache

from infrastructure.database.gateways.postgres import Database
from infrastructure.database.repositories.organizations.members import SQLAlchemyOrganizationMemberRepository
from infrastructure.database.repositories.organizations.organizations import SQLAlchemyOrganizationRepository
from infrastructure.database.repositories.sales.activities import SQLAlchemyActivityRepository
from infrastructure.database.repositories.sales.contacts import SQLAlchemyContactRepository
from infrastructure.database.repositories.sales.deals import SQLAlchemyDealRepository
from infrastructure.database.repositories.sales.tasks import SQLAlchemyTaskRepository
from infrastructure.database.repositories.users.users import SQLAlchemyUserRepository
from punq import (
    Container,
    Scope,
)

from application.mediator import Mediator
from application.organizations.commands import (
    AddMemberCommand,
    AddMemberCommandHandler,
    CreateOrganizationCommand,
    CreateOrganizationCommandHandler,
)
from application.organizations.queries import (
    GetMemberByOrganizationAndUserQuery,
    GetMemberByOrganizationAndUserQueryHandler,
    GetOrganizationByIdQuery,
    GetOrganizationByIdQueryHandler,
    GetUserOrganizationsQuery,
    GetUserOrganizationsQueryHandler,
)
from application.sales.commands import (
    CreateActivityCommand,
    CreateActivityCommandHandler,
    CreateCommentActivityCommand,
    CreateCommentActivityCommandHandler,
    CreateContactCommand,
    CreateContactCommandHandler,
    CreateDealCommand,
    CreateDealCommandHandler,
    CreateTaskCommand,
    CreateTaskCommandHandler,
    DeleteContactCommand,
    DeleteContactCommandHandler,
    UpdateDealStageCommand,
    UpdateDealStageCommandHandler,
    UpdateDealStatusCommand,
    UpdateDealStatusCommandHandler,
    UpdateTaskCommand,
    UpdateTaskCommandHandler,
)
from application.sales.queries import (
    GetActivitiesByDealIdQuery,
    GetActivitiesByDealIdQueryHandler,
    GetContactByIdQuery,
    GetContactByIdQueryHandler,
    GetContactsQuery,
    GetContactsQueryHandler,
    GetDealByIdQuery,
    GetDealByIdQueryHandler,
    GetDealsQuery,
    GetDealsQueryHandler,
    GetTaskByIdQuery,
    GetTaskByIdQueryHandler,
    GetTasksQuery,
    GetTasksQueryHandler,
)
from application.users.commands import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from application.users.queries import (
    AuthenticateUserQuery,
    AuthenticateUserQueryHandler,
    GetUserByIdQuery,
    GetUserByIdQueryHandler,
)
from domain.organizations.interfaces.repositories.members import BaseOrganizationMemberRepository
from domain.organizations.interfaces.repositories.organizations import BaseOrganizationRepository
from domain.organizations.services import (
    MemberService,
    OrganizationService,
)
from domain.sales.interfaces.repositories import (
    BaseActivityRepository,
    BaseContactRepository,
    BaseDealRepository,
    BaseTaskRepository,
)
from domain.sales.services import (
    ActivityService,
    ContactService,
    DealService,
    TaskService,
)
from domain.users.interfaces.repositories.users import BaseUserRepository
from domain.users.services import UserService
from settings.config import Config


@lru_cache(1)
def init_container():
    return _init_container()


def _init_container() -> Container:
    container = Container()

    # Регистрируем конфиг
    config = Config()
    container.register(Config, instance=config, scope=Scope.singleton)

    # Регистрируем Database
    def init_database() -> Database:
        return Database(
            url=config.postgres_connection_uri,
            ro_url=config.postgres_connection_uri,
        )

    container.register(Database, factory=init_database, scope=Scope.singleton)

    # Регистрируем репозитории
    container.register(
        BaseOrganizationRepository,
        SQLAlchemyOrganizationRepository,
    )
    container.register(
        BaseOrganizationMemberRepository,
        SQLAlchemyOrganizationMemberRepository,
    )
    container.register(
        BaseUserRepository,
        SQLAlchemyUserRepository,
    )
    container.register(
        BaseContactRepository,
        SQLAlchemyContactRepository,
    )
    container.register(
        BaseDealRepository,
        SQLAlchemyDealRepository,
    )
    container.register(
        BaseTaskRepository,
        SQLAlchemyTaskRepository,
    )
    container.register(
        BaseActivityRepository,
        SQLAlchemyActivityRepository,
    )

    # Регистрируем доменные сервисы
    container.register(OrganizationService)
    container.register(MemberService)
    container.register(UserService)
    container.register(ContactService)
    container.register(DealService)
    container.register(TaskService)
    container.register(ActivityService)

    # Регистрируем command handlers
    # Organizations
    container.register(CreateOrganizationCommandHandler)
    container.register(AddMemberCommandHandler)

    # Users
    container.register(CreateUserCommandHandler)

    # Sales - Contacts
    container.register(CreateContactCommandHandler)
    container.register(DeleteContactCommandHandler)

    # Sales - Deals
    container.register(CreateDealCommandHandler)
    container.register(UpdateDealStatusCommandHandler)
    container.register(UpdateDealStageCommandHandler)

    # Sales - Tasks
    container.register(CreateTaskCommandHandler)
    container.register(UpdateTaskCommandHandler)

    # Sales - Activities
    container.register(CreateActivityCommandHandler)
    container.register(CreateCommentActivityCommandHandler)

    # Регистрируем query handlers
    # Organizations
    container.register(GetOrganizationByIdQueryHandler)
    container.register(GetMemberByOrganizationAndUserQueryHandler)
    container.register(GetUserOrganizationsQueryHandler)

    # Users
    container.register(AuthenticateUserQueryHandler)
    container.register(GetUserByIdQueryHandler)

    # Sales - Contacts
    container.register(GetContactByIdQueryHandler)
    container.register(GetContactsQueryHandler)

    # Sales - Deals
    container.register(GetDealByIdQueryHandler)
    container.register(GetDealsQueryHandler)

    # Sales - Tasks
    container.register(GetTaskByIdQueryHandler)
    container.register(GetTasksQueryHandler)

    # Sales - Activities
    container.register(GetActivitiesByDealIdQueryHandler)

    # Инициализируем медиатор
    def init_mediator() -> Mediator:
        mediator = Mediator()

        # Регистрируем commands
        # Organizations
        mediator.register_command(
            CreateOrganizationCommand,
            [container.resolve(CreateOrganizationCommandHandler)],
        )
        mediator.register_command(
            AddMemberCommand,
            [container.resolve(AddMemberCommandHandler)],
        )

        # Users
        mediator.register_command(
            CreateUserCommand,
            [container.resolve(CreateUserCommandHandler)],
        )

        # Sales - Contacts
        mediator.register_command(
            CreateContactCommand,
            [container.resolve(CreateContactCommandHandler)],
        )
        mediator.register_command(
            DeleteContactCommand,
            [container.resolve(DeleteContactCommandHandler)],
        )

        # Sales - Deals
        mediator.register_command(
            CreateDealCommand,
            [container.resolve(CreateDealCommandHandler)],
        )
        mediator.register_command(
            UpdateDealStatusCommand,
            [container.resolve(UpdateDealStatusCommandHandler)],
        )
        mediator.register_command(
            UpdateDealStageCommand,
            [container.resolve(UpdateDealStageCommandHandler)],
        )

        # Sales - Tasks
        mediator.register_command(
            CreateTaskCommand,
            [container.resolve(CreateTaskCommandHandler)],
        )
        mediator.register_command(
            UpdateTaskCommand,
            [container.resolve(UpdateTaskCommandHandler)],
        )

        # Sales - Activities
        mediator.register_command(
            CreateActivityCommand,
            [container.resolve(CreateActivityCommandHandler)],
        )
        mediator.register_command(
            CreateCommentActivityCommand,
            [container.resolve(CreateCommentActivityCommandHandler)],
        )

        # Регистрируем queries
        # Organizations
        mediator.register_query(
            GetOrganizationByIdQuery,
            container.resolve(GetOrganizationByIdQueryHandler),
        )
        mediator.register_query(
            GetMemberByOrganizationAndUserQuery,
            container.resolve(GetMemberByOrganizationAndUserQueryHandler),
        )
        mediator.register_query(
            GetUserOrganizationsQuery,
            container.resolve(GetUserOrganizationsQueryHandler),
        )

        # Users
        mediator.register_query(
            AuthenticateUserQuery,
            container.resolve(AuthenticateUserQueryHandler),
        )
        mediator.register_query(
            GetUserByIdQuery,
            container.resolve(GetUserByIdQueryHandler),
        )

        # Sales - Contacts
        mediator.register_query(
            GetContactByIdQuery,
            container.resolve(GetContactByIdQueryHandler),
        )
        mediator.register_query(
            GetContactsQuery,
            container.resolve(GetContactsQueryHandler),
        )

        # Sales - Deals
        mediator.register_query(
            GetDealByIdQuery,
            container.resolve(GetDealByIdQueryHandler),
        )
        mediator.register_query(
            GetDealsQuery,
            container.resolve(GetDealsQueryHandler),
        )

        # Sales - Tasks
        mediator.register_query(
            GetTaskByIdQuery,
            container.resolve(GetTaskByIdQueryHandler),
        )
        mediator.register_query(
            GetTasksQuery,
            container.resolve(GetTasksQueryHandler),
        )

        # Sales - Activities
        mediator.register_query(
            GetActivitiesByDealIdQuery,
            container.resolve(GetActivitiesByDealIdQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator, scope=Scope.singleton)

    return container
