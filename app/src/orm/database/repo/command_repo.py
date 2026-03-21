from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import DisabledCommands

class CommandRepository(AbstractRepository):
    model = DisabledCommands