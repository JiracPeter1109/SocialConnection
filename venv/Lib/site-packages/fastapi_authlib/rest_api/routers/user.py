"""User"""

from fastapi import APIRouter, Depends
from starlette.requests import Request

from fastapi_authlib.messages.user import UserMessage
from fastapi_authlib.services import AuthService

router = APIRouter()


@router.get('/users', response_model=UserMessage)
async def user(
    *,
    request: Request,
    service: AuthService = Depends()
):
    """
    User
    """
    user_info = request.state.user
    return {'data': await service.get_user_by_id(user_info.get('user_id'))}
