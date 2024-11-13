from fastapi import Depends, HTTPException, status
from typing import Annotated

from app.services import AuthService, UserService, ThreadService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

UnitOfWorkDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]

get_user_service = Annotated[UserService, Depends(UserService)]
get_threads_service = Annotated[ThreadService, Depends(ThreadService)]

get_auth_service = Annotated[AuthService, Depends(AuthService)]
verify = get_auth_service().verify

get_current_user = Annotated[int, Depends(verify)]

verify_from_query = get_auth_service().verify_from_query
get_current_user_id_from_query = Annotated[int, Depends(verify_from_query)]

