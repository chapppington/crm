from functools import lru_cache

from infrastructure.database.repositories.dummy.organizations.members import DummyInMemoryOrganizationMemberRepository
from infrastructure.database.repositories.dummy.organizations.organizations import DummyInMemoryOrganizationRepository
from infrastructure.database.repositories.dummy.sales.activities import DummyInMemoryActivityRepository
from infrastructure.database.repositories.dummy.sales.contacts import DummyInMemoryContactRepository
from infrastructure.database.repositories.dummy.sales.deals import DummyInMemoryDealRepository
from infrastructure.database.repositories.dummy.sales.tasks import DummyInMemoryTaskRepository
from infrastructure.database.repositories.dummy.users.users import DummyInMemoryUserRepository
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
    container.register(Config, instance=Config(), scope=Scope.singleton)

    # Регистрируем репозитории (dummy для начала)
    container.register(
        BaseOrganizationRepository,
        DummyInMemoryOrganizationRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseOrganizationMemberRepository,
        DummyInMemoryOrganizationMemberRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseUserRepository,
        DummyInMemoryUserRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseContactRepository,
        DummyInMemoryContactRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseDealRepository,
        DummyInMemoryDealRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseTaskRepository,
        DummyInMemoryTaskRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseActivityRepository,
        DummyInMemoryActivityRepository,
        scope=Scope.singleton,
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
