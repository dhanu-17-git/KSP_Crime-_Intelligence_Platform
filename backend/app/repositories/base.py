from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from sqlalchemy import Select, and_, func, inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement

ModelT = TypeVar("ModelT")


@dataclass(frozen=True)
class PaginationResult(Generic[ModelT]):
    items: list[ModelT]
    total: int
    page: int
    page_size: int


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]
    primary_key: ClassVar[str | tuple[str, ...]]
    unique_fields: ClassVar[tuple[tuple[str, ...], ...]] = ()
    search_fields: ClassVar[tuple[str, ...]] = ()
    default_sort: ClassVar[str | tuple[str, bool]] | None = None
    list_options: ClassVar[tuple[Any, ...]] = ()
    detail_options: ClassVar[tuple[Any, ...]] = ()

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: Mapping[str, Any]) -> ModelT:
        self._validate_fields(data)
        instance = self.model(**dict(data))
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_primary_key(self, primary_key: Any) -> ModelT | None:
        return await self.session.get(
            self.model,
            primary_key,
            options=self.detail_options,
        )

    async def get(self, primary_key: Any) -> ModelT | None:
        return await self.get_by_primary_key(primary_key)

    async def get_by_unique_fields(self, **fields: Any) -> ModelT | None:
        if not fields:
            raise ValueError("At least one unique field is required")
        self._validate_fields(fields)
        if self.unique_fields and tuple(fields) not in self.unique_fields:
            field_set = frozenset(fields)
            valid = any(field_set == frozenset(unique) for unique in self.unique_fields)
            if not valid:
                raise ValueError(
                    f"Fields {tuple(fields)} are not configured as a unique lookup"
                )
        statement = self._base_select(detail=True)
        statement = statement.where(
            and_(*(getattr(self.model, field) == value for field, value in fields.items()))
        )
        result = await self.session.execute(statement)
        return result.scalars().unique().first()

    async def update(self, primary_key: Any, data: Mapping[str, Any]) -> ModelT | None:
        self._validate_fields(data)
        instance = await self.get_by_primary_key(primary_key)
        if instance is None:
            return None
        for field, value in data.items():
            setattr(instance, field, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, primary_key: Any) -> bool:
        instance = await self.get_by_primary_key(primary_key)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
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
        statement = self._build_query(
            filters=filters,
            search=search,
            sort_by=sort_by,
            sort_desc=sort_desc,
            include_options=True,
        )
        statement = statement.offset(self._offset(page, page_size)).limit(page_size)
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

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
        items = await self.list(
            filters=filters,
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )
        total = await self.count(filters=filters, search=search)
        return PaginationResult(items=items, total=total, page=page, page_size=page_size)

    async def count(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        search: str | None = None,
    ) -> int:
        key_columns = self._primary_key_columns()
        statement = select(*key_columns).select_from(self.model).distinct()
        statement = self._apply_filters(statement, filters or {})
        statement = self._apply_search(statement, search)
        count_statement = select(func.count()).select_from(statement.subquery())
        result = await self.session.execute(count_statement)
        return int(result.scalar_one())

    async def bulk_insert(self, rows: Sequence[Mapping[str, Any]]) -> list[ModelT]:
        for row in rows:
            self._validate_fields(row)
        instances = [self.model(**dict(row)) for row in rows]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def bulk_update(
        self,
        rows: Sequence[Mapping[str, Any]],
        *,
        key_fields: Sequence[str] | None = None,
    ) -> list[ModelT]:
        updated: list[ModelT] = []
        keys = tuple(key_fields or self._primary_key_field_names())
        for row in rows:
            self._validate_fields(row)
            missing = [field for field in keys if field not in row]
            if missing:
                raise ValueError(f"Missing bulk update key fields: {tuple(missing)}")
            lookup = {field: row[field] for field in keys}
            values = {field: value for field, value in row.items() if field not in keys}
            instance = await self.get_by_unique_fields(**lookup)
            if instance is None:
                continue
            for field, value in values.items():
                setattr(instance, field, value)
            updated.append(instance)
        await self.session.flush()
        for instance in updated:
            await self.session.refresh(instance)
        return updated

    def _build_query(
        self,
        *,
        filters: Mapping[str, Any] | None,
        search: str | None,
        sort_by: str | None,
        sort_desc: bool,
        include_options: bool,
    ) -> Select[tuple[ModelT]]:
        statement = self._base_select(detail=False if include_options else None)
        statement = self._apply_filters(statement, filters or {})
        statement = self._apply_search(statement, search)
        statement = self._apply_sorting(statement, sort_by, sort_desc)
        return statement

    def _base_select(self, *, detail: bool | None) -> Select[tuple[ModelT]]:
        statement = select(self.model)
        if detail is True and self.detail_options:
            statement = statement.options(*self.detail_options)
        elif detail is False and self.list_options:
            statement = statement.options(*self.list_options)
        return statement

    def _apply_filters(
        self,
        statement: Select[Any],
        filters: Mapping[str, Any],
    ) -> Select[Any]:
        for raw_field, value in filters.items():
            if value is None:
                continue
            field, operator = self._split_filter_operator(raw_field)
            column = self._column(field)
            statement = statement.where(self._predicate(column, operator, value))
        return statement

    def _apply_search(
        self,
        statement: Select[Any],
        search: str | None,
    ) -> Select[Any]:
        if not search or not self.search_fields:
            return statement
        pattern = f"%{search.strip()}%"
        predicates = [
            self._column(field).ilike(pattern)
            for field in self.search_fields
        ]
        return statement.where(or_(*predicates))

    def _apply_sorting(
        self,
        statement: Select[Any],
        sort_by: str | None,
        sort_desc: bool,
    ) -> Select[Any]:
        selected_sort = sort_by
        selected_desc = sort_desc
        if selected_sort is None and self.default_sort is not None:
            if isinstance(self.default_sort, tuple):
                selected_sort, selected_desc = self.default_sort
            else:
                selected_sort = self.default_sort
        if selected_sort is None:
            selected_sort = self._primary_key_field_names()[0]
        column = self._column(selected_sort)
        return statement.order_by(column.desc() if selected_desc else column.asc())

    def _column(self, field: str) -> InstrumentedAttribute[Any]:
        self._validate_field(field)
        return getattr(self.model, field)

    def _predicate(
        self,
        column: InstrumentedAttribute[Any],
        operator: str,
        value: Any,
    ) -> ColumnElement[bool]:
        if operator == "eq":
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
                return column.in_(list(value))
            return column == value
        if operator == "ne":
            return column != value
        if operator == "gt":
            return column > value
        if operator == "gte":
            return column >= value
        if operator == "lt":
            return column < value
        if operator == "lte":
            return column <= value
        if operator == "in":
            return column.in_(list(value))
        if operator == "like":
            return column.like(f"%{value}%")
        if operator == "ilike":
            return column.ilike(f"%{value}%")
        if operator == "isnull":
            return column.is_(None) if value else column.is_not(None)
        raise ValueError(f"Unsupported filter operator: {operator}")

    def _split_filter_operator(self, field: str) -> tuple[str, str]:
        if "__" not in field:
            return field, "eq"
        name, operator = field.rsplit("__", 1)
        return name, operator

    def _validate_fields(self, fields: Mapping[str, Any]) -> None:
        for field in fields:
            self._validate_field(self._split_filter_operator(field)[0])

    def _validate_field(self, field: str) -> None:
        if field not in self._field_names():
            raise ValueError(f"{field} is not a valid field for {self.model.__name__}")

    def _field_names(self) -> set[str]:
        mapper = inspect(self.model)
        return {attribute.key for attribute in mapper.column_attrs}

    def _primary_key_field_names(self) -> tuple[str, ...]:
        if isinstance(self.primary_key, tuple):
            return self.primary_key
        return (self.primary_key,)

    def _primary_key_columns(self) -> tuple[InstrumentedAttribute[Any], ...]:
        return tuple(self._column(field) for field in self._primary_key_field_names())

    def _offset(self, page: int, page_size: int) -> int:
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")
        if page_size < 1:
            raise ValueError("page_size must be greater than or equal to 1")
        return (page - 1) * page_size
