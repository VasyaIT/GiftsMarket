from src.application.interfaces.database import DBSession
from src.application.interfaces.history import HistoryReader
from src.application.interfaces.interactor import Interactor
from src.domain.entities.history import ActivityDM, HistoryDM
from src.domain.entities.user import UserDM


class HistoryInteractor(Interactor[None, list[HistoryDM]]):
    def __init__(
        self,
        history_gateway: HistoryReader,
        user: UserDM,
        db_session: DBSession,
    ) -> None:
        self._db_session = db_session
        self._user = user
        self._history_gateway = history_gateway

    async def __call__(self) -> list[HistoryDM]:
        return await self._history_gateway.get_many(user_id=self._user.id)


class ActivityInteractor(Interactor[None, list[ActivityDM]]):
    def __init__(
        self,
        history_gateway: HistoryReader,
        user: UserDM,
        db_session: DBSession,
    ) -> None:
        self._db_session = db_session
        self._user = user
        self._history_gateway = history_gateway

    async def __call__(self) -> list[ActivityDM]:
        return await self._history_gateway.get_activity()
