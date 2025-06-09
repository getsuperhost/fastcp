import math
from uuid import UUID
from typing import Type, TypeVar, Optional, Generic, List, Dict, Any

from sqlalchemy import select, or_, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

T = TypeVar('T', bound=SQLModel)


class BaseRepository(Generic[T]):
    """
    A generic base repository for CRUD operations on a SQLModel model.
    Provides common methods like create, get, paginate, etc.
    """

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, db: AsyncSession, data: dict) -> T:
        """
        Insert a new record into the database.
        Commits the session and refreshes the created object.
        """
        obj_data = self.model(**data)
        db.add(obj_data)
        await db.commit()
        await db.refresh(obj_data)
        return obj_data

    async def create_many(self, db: AsyncSession, data_list: List[dict]) -> List[T]:
        """
        Insert multiple records in one go, committing once at the end.
        Returns the list of created objects with their IDs populated.
        Useful for bulk insert scenarios.
        """
        objects = [self.model(**data) for data in data_list]
        db.add_all(objects)
        await db.commit()

        # If you need the fully refreshed objects (with relationships), loop to refresh each
        for obj in objects:
            await db.refresh(obj)
        return objects

    async def get_one(
        self,
        db: AsyncSession,
        eager_relations: Optional[List[str]] = None,
        or_filters: Optional[Dict[str, Any]] = None,
        **filters,
    ) -> Optional[T]:
        """
        Retrieve a single record based on provided filters.
        Returns None if no match is found.
        """
        stmt = select(self.model)

        if eager_relations:
            for relation in eager_relations:
                # Convert the relationship name into a selectinload
                stmt = stmt.options(selectinload(getattr(self.model, relation)))

        # OR filters
        if or_filters:
            or_clauses = [
                getattr(self.model, field_name) == value
                for field_name, value in or_filters.items()
            ]
            stmt = stmt.where(or_(*or_clauses))

        for field_name, value in filters.items():
            stmt = stmt.where(getattr(self.model, field_name) == value)  # type: ignore
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        **filters,
    ) -> List[T]:
        """
        Retrieve multiple records, optionally applying an OR-based search across specified fields.
        Exact-match filters are applied as additional WHERE clauses.
        """
        stmt = select(self.model)

        # Apply OR-based case-insensitive search if requested
        if search and search_fields:
            or_conditions = []
            for field in search_fields:
                column = getattr(self.model, field, None)
                if column is not None:
                    or_conditions.append(column.ilike(f'%{search}%'))
            if or_conditions:
                stmt = stmt.where(or_(*or_conditions))

        # Apply exact-match filters
        for field_name, value in filters.items():
            stmt = stmt.where(getattr(self.model, field_name) == value)  # type: ignore

        result = await db.execute(stmt)
        return result.scalars().all()  # type: ignore

    async def update(self, db: AsyncSession, obj_id: UUID, data: dict) -> T | None:
        """
        Update an existing record by ID.
        Commits and refreshes the updated object.
        Returns None if the object does not exist.
        """
        db_obj = await db.get(self.model, obj_id)
        if not db_obj:
            return None
        for field, value in data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, **kwargs) -> None:
        """
        Delete records that match the given filters.
        """
        if len(kwargs) == 0:
            raise ValueError('At least one filter must be provided for deletion.')

        stmt = delete(self.model)
        for field_name, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, field_name) == value)  # type: ignore
        await db.execute(stmt)
        await db.commit()

    async def list_all(self, db: AsyncSession) -> List[T]:
        """
        Retrieve all records without filters.
        """
        result = await db.execute(select(self.model))
        return result.scalars().all()  # type: ignore

    async def paginate(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        order_by: str = 'id',
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        **filters,
    ) -> Dict[str, Any]:
        """
        Retrieve a paginated list of records, with optional search and filtering.
        Also returns total count and total pages for easy frontend consumption.
        """
        # Base select for items
        stmt = select(self.model)
        # Separate count query for total items
        count_stmt = select(func.count())

        # Apply OR-based case-insensitive search if requested
        if search and search_fields:
            or_conditions = []
            for field in search_fields:
                column = getattr(self.model, field, None)
                if column is not None:
                    or_conditions.append(column.ilike(f'%{search}%'))

            if or_conditions:
                stmt = stmt.where(or_(*or_conditions))
                count_stmt = count_stmt.where(or_(*or_conditions))

        # Apply exact-match filters to both queries
        if filters:
            for field_name, value in filters.items():
                stmt = stmt.where(getattr(self.model, field_name) == value)  # type: ignore
                count_stmt = count_stmt.where(getattr(self.model, field_name) == value)  # type: ignore

        # Order results (descending if prefixed with -)
        is_desc = order_by.startswith('-')
        order_by_field = order_by.lstrip('-')
        if hasattr(self.model, order_by_field):
            column = getattr(self.model, order_by_field)
            stmt = stmt.order_by(column.desc()) if is_desc else stmt.order_by(column)

        # Execute count query to get total number of items
        total_count = (await db.execute(count_stmt)).scalar() or 0

        # Apply pagination offsets/limits
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        # Execute the query to fetch items
        result = await db.execute(stmt)
        items = result.scalars().all()

        # Return a standardized response structure
        return {
            'items': items,
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': math.ceil(total_count / limit) if limit else 1,
        }
