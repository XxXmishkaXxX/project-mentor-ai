import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.base.accessor import BaseAccessor
from app.users.db import UserModel
from app.users.exceptions import UserAlreadyExistsError


class UserAccessor(BaseAccessor):
    async def create_user(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
    ) -> UserModel:
        user = UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
        )
        try:
            return await self.store.pg.add_one(user)
        except IntegrityError:
            raise UserAlreadyExistsError() from None

    async def get_by_email(self, email: str) -> UserModel | None:
        return await self.store.pg.scalar_one_or_none(
            select(UserModel).where(UserModel.email == email),
        )

    async def get_by_id(self, user_id: uuid.UUID | str) -> UserModel | None:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        return await self.store.pg.scalar_one_or_none(
            select(UserModel).where(UserModel.id == user_id),
        )
