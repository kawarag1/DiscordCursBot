from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Log_entries

class LogRepository(AbstractRepository):
    model = Log_entries