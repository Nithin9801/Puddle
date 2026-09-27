from pydantic import BaseModel,EmailStr
from uuid import UUID
from datetime import datetime

class UserCretaeModel(BaseModel):
    username : str 
    email : EmailStr
    profile_pic_url : str
    email_verified : bool

class UserResponseModel(BaseModel):
    uid : UUID 
    username : str 
    email : EmailStr
    profile_pic_url : str
    email_verified : bool
    created_at : datetime 
    updated_at : datetime 

class OauthUserModel(BaseModel):
    provider : str 
    provider_user_id : str
    provider_email : str
    user_id : UUID