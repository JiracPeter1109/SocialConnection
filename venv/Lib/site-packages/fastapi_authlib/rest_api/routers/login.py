"""login"""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fastapi_authlib.config import settings
from fastapi_authlib.services import AuthService
from fastapi_authlib.utils import encode_token

router = APIRouter()


@router.get('/login')
async def login(
    request: Request,
    service: AuthService = Depends()
):
    """
    Login
    """
    redirect_uri = request.url_for('auth')
    url = f"{str(redirect_uri)}{'?' + urlencode(request.query_params) if request.query_params else ''}"
    return await service.login(request, url)


@router.get('/auth')
async def auth(
    callback_url: str,
    request: Request,
    service: AuthService = Depends(),
):
    """
    Auth
    """
    user = await service.auth(request)
    # clear session, three-party authentication uses cookies
    request.session.clear()
    token = encode_token(user, secret_key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return RedirectResponse(url=callback_url, headers={"authorization": f"Bearer {token}"})
