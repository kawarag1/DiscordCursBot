from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import User


class UserRepository(AbstractRepository):
    model = User