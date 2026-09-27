from sqlmodel import SQLModel,Field,Relationship
from datetime import datetime,date,timezone
from pydantic import EmailStr
from sqlalchemy import Column,DateTime

from uuid import UUID,uuid4
from typing import Optional,List


class User(SQLModel,table=True):
    __tablename__ = "users"

    uid : UUID = Field(default_factory=uuid4,primary_key=True)
    username : str 
    email : EmailStr
    profile_pic_url : str
    email_verified : bool
    created_at : datetime =  Field(sa_column=Column(DateTime,default=datetime.now(timezone.utc)))
    updated_at : datetime =  Field(sa_column=Column(DateTime,default=datetime.now(timezone.utc)))

    def __repr__(self):
        return f"<User {self.username}>"

class OauthConnections(SQLModel,table=True):
    __tablename__ = "oauthconnections"

    uid : UUID = Field(default_factory=uuid4,primary_key=True)
    user_id : Optional[UUID] = Field(default=None,foreign_key="users.uid")
    provider : str 
    provider_user_id : str = Field(unique=True) 
    provider_email : str = Field(default=None,nullable=True)
    created_at : datetime =  Field(sa_column=Column(DateTime,default=datetime.now(timezone.utc)))
    updated_at : datetime =  Field(sa_column=Column(DateTime,default=datetime.now(timezone.utc)))


    def __repr__(self):
        return f"<Provider_email : {self.provider_email}"