from fastapi import APIRouter, Depends, Response

from ..use_cases.user_use_case import AddUserUseCase
from ..viewmodels.user_model import CreateUserModel

router = APIRouter(prefix='/users')


@router.post('/add')
def add_user(new_user: CreateUserModel, add_use_case: AddUserUseCase = Depends()):
    add_use_case.add(new_user)
    return Response("Added", 200)
