from orm.database.repo.abc_repo import AbstractRepository
from orm.models.models import User


class UserRepository(AbstractRepository):
    model = User