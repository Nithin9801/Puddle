from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse,JSONResponse,Response
from sqlmodel.ext.asyncio.session import AsyncSession

from urllib.parse import urlencode
import httpx
from datetime import timedelta

from .schemas import UserCretaeModel
from .service import UserService
from .utils import create_access_token,decode_token

from src.config import Config
from src.db.main import get_session



auth_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = 1

REDIRECT_URI="http://localhost:8000/api/v1/auth/callback"
GOOGLE_AUTH_ENDPOINT="https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT="https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT="https://openidconnect.googleapis.com/v1/userinfo"




@auth_router.get('/signup')
async def signup():
    params = {"client_id" : Config.CLIENT_ID,
            "response_type" :"code",
            "scope" : "openid email profile",
            "redirect_uri" : REDIRECT_URI,
            "access_type" : "offline",
            "prompt" : "select_account"
            }

    url =  f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(query=params)}"

    return RedirectResponse(url)




@auth_router.get('/callback')
async def callback(request:Request,session:AsyncSession = Depends(get_session)):
    code = request.query_params.get("code")
    if not code :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Authorization code not found")

    data = {
        "code" : code,
        "client_id" : Config.CLIENT_ID,
        "client_secret" : Config.CLIENT_SECRET,
        "redirect_uri" : REDIRECT_URI,
        "grant_type" : "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_ENDPOINT,data=data)
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Failed to retrieve access token")

        headers = {"Authorization" : f"Bearer {access_token}"}
        user_info_response = await client.get(GOOGLE_USERINFO_ENDPOINT,headers=headers)
        user_info = user_info_response.json()

        user_exists = await user_service.user_exists(user_info['sub'],session)

        if not user_exists:

            user_data = UserCretaeModel(
                    username = user_info['name'],
                    email = user_info['email'],
                    profile_pic_url= user_info['picture'],
                    email_verified= user_info['email_verified']
                    )

            await user_service.create_user(user_data,user_info['sub'],session)

        access_token = create_access_token(
            user_data={
                "name":user_info['name'],
                "email":user_info['email'],
                "profile_pic":user_info['picture']
            }
        )

        refresh_token = create_access_token(
            user_data={
                "name":user_info['name'],
                "email":user_info['email'],
                "profile_pic":user_info['picture']
            },
            expiry=timedelta(REFRESH_TOKEN_EXPIRY),
            refresh=True
        )

        response = RedirectResponse("http://localhost:5173/profile")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=900
        )
    
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400
        )

        return response


@auth_router.get('/profile')
async def profile(request: Request):

    access_token = request.cookies.get("access_token")

    if not access_token:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail={"message":"user not logged in"})

        refresh_token_data = decode_token(refresh_token)
        access_token = create_access_token(
                    user_data={
                        "name":refresh_token_data['user']['name'],
                        "email":refresh_token_data['user']['email'],
                        "profile_pic":refresh_token_data['user']['profile_pic']
                    }
                )

        response = Response()

        response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=900
            )
        
    token_data = decode_token(access_token)

    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail={"message":"Token invaild or expired"})

    content = {
        "name":token_data['user']['name'],
        "email":token_data['user']['email'],
        "picture":token_data['user']['profile_pic']
    }

    return JSONResponse(content=content,status_code=status.HTTP_200_OK)
