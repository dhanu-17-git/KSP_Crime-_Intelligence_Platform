"""Generic base service with transaction management and validation hooks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository, PaginationResult

ModelT = TypeVar("ModelT")
RepoT = TypeVar("RepoT", bound=BaseRepository)  # type: ignore[type-arg]


class BaseService(Generic[ModelT, RepoT]):
    """Thin service layer that owns the session commit boundary.

    Subclasses override ``_validate_create`` / ``_validate_update`` to inject
    business rules.  The base implementation delegates straight to the
    repository.
    """

    repository_class: type[RepoT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo: RepoT = self.repository_class(session)  # type: ignore[call-arg]

    # -- Public API ----------------------------------------------------------

    async def create(self, data: Mapping[str, Any]) -> ModelT:
        await self._validate_create(data)
        instance = await self.repo.create(data)
        await self.session.commit()
        return instance

    async def get(self, pk: Any) -> ModelT | None:
        return await self.repo.get(pk)

    async def get_or_404(self, pk: Any) -> ModelT:
        from app.utils.exceptions import NotFoundError

        instance = await self.repo.get(pk)
        if instance is None:
            model_name = self.repo.model.__name__
            raise NotFoundError(f"{model_name} with id {pk} not found")
        return instance

    async def update(self, pk: Any, data: Mapping[str, Any]) -> ModelT:
        from app.utils.exceptions import NotFoundError

        await self._validate_update(pk, data)
        instance = await self.repo.update(pk, data)
        if instance is None:
            model_name = self.repo.model.__name__
            raise NotFoundError(f"{model_name} with id {pk} not found")
        await self.session.commit()
        return instance

    async def delete(self, pk: Any) -> bool:
        from app.utils.exceptions import NotFoundError

        deleted = await self.repo.delete(pk)
        if not deleted:
            model_name = self.repo.model.__name__
            raise NotFoundError(f"{model_name} with id {pk} not found")
        await self.session.commit()
        return True

    async def list(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> list[ModelT]:
        return await self.repo.list(
            filters=filters,
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )

    async def paginate(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> PaginationResult[ModelT]:
        return await self.repo.paginate(
            filters=filters,
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )

    async def count(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        search: str | None = None,
    ) -> int:
        return await self.repo.count(filters=filters, search=search)

    async def bulk_insert(self, rows: list[Mapping[str, Any]]) -> list[ModelT]:
        instances = await self.repo.bulk_insert(rows)
        await self.session.commit()
        return instances

    # -- Hooks for subclasses ------------------------------------------------

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        """Override to add business-rule validation before create."""

    async def _validate_update(self, pk: Any, data: Mapping[str, Any]) -> None:
        """Override to add business-rule validation before update."""

    async def _assert_exists(self, repo: BaseRepository, pk: Any, label: str) -> None:  # type: ignore[type-arg]
        """Raise NotFoundError if a referenced FK target does not exist."""
        from app.utils.exceptions import NotFoundError

        if pk is not None and await repo.get(pk) is None:
            raise NotFoundError(f"Referenced {label} ({pk}) does not exist")
