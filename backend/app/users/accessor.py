import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.base.accessor import BaseAccessor
from app.users.db import UserModel
from app.users.domain.models import User


class UserAccessor(BaseAccessor):
    async def create_user(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
    ) -> User | None:
        stmt = (
            pg_insert(UserModel)
            .values(
                username=username,
                email=email,
                password_hash=password_hash,
            )
            .on_conflict_do_nothing()
            .returning(UserModel)
        )
        row = await self.store.pg.scalar_one_or_none(stmt)
        return User.from_db(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        row = await self.store.pg.scalar_one_or_none(
            select(UserModel).where(UserModel.email == email),
        )
        return User.from_db(row) if row else None

    async def get_by_id(self, user_id: uuid.UUID | str) -> User | None:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        row = await self.store.pg.scalar_one_or_none(
            select(UserModel).where(UserModel.id == user_id),
        )
        return User.from_db(row) if row else None
