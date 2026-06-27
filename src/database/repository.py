from typing import TypeVar, Generic, Sequence, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID as ID

from src.database.base import Base

_MT = TypeVar('_MT', bound=Base)
"""An abbreviation for `ORM Model Type` referring to any table in the database."""


class BaseRepository(Generic[_MT]):
    """
    Generic repository class for performing standard `CRUD` operations.
    
    Provides an abstraction layer over `SQLAlchemy's` `AsyncSession` to handle
    database interactions strictly without implementing business logic.
    """

    def __init__(self, model: type[_MT], session: AsyncSession):
        """
        Initializes the repository with the specific `SQLAlchemy` model and session.

        Args:
            model (type[_MT]): The `SQLAlchemy` declarative model class.
            session (AsyncSession): The `asynchronous` database session instance.
        """
        self.model = model

        self.session = session

    
    async def get_by_id(self, id: ID) -> _MT | None:
        """
        Retrieves a single database record by its primary key `UUID`.

        Args:
            id (ID): The universally unique identifier `UUID` of the record.

        Returns:
            _MT | None: The model instance if found, otherwise `None`.
        """
        return await self.session.get(self.model, id)


    async def get_multi(self, skip: int= 0, limit: int= 20) -> Sequence[_MT]:
        """
        Retrieves a list of database records with pagination support.

        Args:
            skip (int, optional): The number of records to skip. Defaults to 0.
            limit (int, optional): The maximum number of records to return. Defaults to 20.

        Returns:
            Sequence[_MT]: A sequence containing the retrieved model instances.
        """

        stmt = select(self.model).offset(skip).limit(limit)

        result = await self.session.execute(stmt)

        return result.scalars().all()
        


    async def get_one_by_attribute(self, **kw) -> _MT | None:
        """
        Retrieves a single database record based on dynamic keyword arguments.

        Args:
            **kw (Any): Dynamic keyword arguments representing model attributes and their expected values.

        Returns:
            _MT | None: The first matching model instance if found, otherwise None.
        """

        stmt = select(self.model).filter_by(**kw)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    


    async def create(self, orm_model: _MT) -> _MT:
        """
        Adds a new record to the database.

        Args:
            orm_model (_MT): The model instance to be persisted.

        Raises:
            IntegrityError: If the insertion violates database constraints (e.g., unique constraints).

        Returns:
            _MT: The persisted model instance refreshed with database-generated fields.
        """
        self.session.add(orm_model)
        return orm_model

    async def update(self, orm_model: _MT, update_data: dict[str, Any]) -> _MT:
        """
        Updates an existing database record with the provided dictionary data.

        Args:
            orm_model (_MT): The existing model instance tracked by the current session.
            update_data (dict[str, Any]): A dictionary containing the fields to update and their new values.

        Raises:
            IntegrityError: If the update violates database constraints.

        Returns:
            _MT: The updated and refreshed model instance.
        """

        for key, value in update_data.items():
            setattr(orm_model, key, value)

        self.session.add(orm_model)
        return orm_model
        

    async def delete(self, orm_model: _MT) -> _MT:
        """
        Deletes an existing record from the database.

        Args:
            orm_model (_MT): The model instance to be removed.

        Returns:
            _MT: The deleted model instance.
        """
        await self.session.delete(orm_model)
        return orm_model