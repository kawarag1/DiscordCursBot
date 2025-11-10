from orm.database.repo.abc_repo import AbstractRepository
from orm.models.models import ServerProfile


class UserServerRepository(AbstractRepository):
    model = ServerProfile