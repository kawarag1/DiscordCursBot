from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Guild

class GuildsRepository(AbstractRepository):
    model = Guild