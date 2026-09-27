from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User,OauthConnections
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from .schemas import UserCretaeModel


class UserService:
    async def get_user_by_sub(self,sub:str,session:AsyncSession) -> dict:
        try:
            statement = (
                select(User)
                .join(OauthConnections)
                .where(OauthConnections.provider_user_id == sub)
            )

            result = await session.exec(statement)

            user = result.first()

            return user

        except IntegrityError as e:
            return None
    
    async def user_exists(self,sub:str,session:AsyncSession) -> bool:
        user = await self.get_user_by_sub(sub,session)

        return True if user is not None else None 

    async def create_user(self,user_data:UserCretaeModel,sub:str,session:AsyncSession) -> dict:
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        session.add(new_user)
        await session.flush()

        new_oauth_user = OauthConnections(
                provider="Google",
                user_id=new_user.uid,
                provider_user_id = sub,
                provider_email = new_user.email
                )

        session.add(new_oauth_user)
        await session.commit()

        return new_user