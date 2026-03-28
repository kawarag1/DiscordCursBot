from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Owner

class OwnerRepository(AbstractRepository):
    model = Owner