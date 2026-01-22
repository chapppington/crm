from presentation.admin.auth_provider import JWTAuthProvider
from presentation.admin.views.activities import ActivityView
from presentation.admin.views.contacts import ContactView
from presentation.admin.views.deals import DealView
from presentation.admin.views.members import OrganizationMemberView
from presentation.admin.views.organizations import OrganizationView
from presentation.admin.views.tasks import TaskView
from presentation.admin.views.users import UserView
from sqlalchemy import create_engine
from starlette_admin.contrib.sqla import Admin
from starlette_admin.i18n import I18nConfig

from application.container import init_container
from application.mediator import Mediator
from settings.config import Config


def setup_admin(app) -> None:
    container = init_container()
    config = container.resolve(Config)
    mediator = container.resolve(Mediator)

    sync_url = config.postgres_connection_uri.replace("+asyncpg", "+psycopg2")

    engine = create_engine(sync_url)

    admin = Admin(
        engine,
        title="CRM Admin",
        i18n_config=I18nConfig(default_locale="ru"),
        auth_provider=JWTAuthProvider(mediator=mediator),
    )

    admin.add_view(UserView())
    admin.add_view(OrganizationView())
    admin.add_view(OrganizationMemberView())
    admin.add_view(ContactView())
    admin.add_view(DealView())
    admin.add_view(TaskView())
    admin.add_view(ActivityView())

    admin.mount_to(app)
