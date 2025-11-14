from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import ServerProfile


class UserServerRepository(AbstractRepository):
    model = ServerProfile