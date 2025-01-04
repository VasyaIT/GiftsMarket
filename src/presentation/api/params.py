from fastapi import Query


class FilterParams:
    def __init__(
        self,
        offset: int | None = Query(default=None, ge=0),
        limit: int | None = Query(default=50, ge=0, le=1000)
    ) -> None:
        self.offset = offset
        self.limit = limit
