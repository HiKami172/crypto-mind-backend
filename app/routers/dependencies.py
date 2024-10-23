from fastapi import Depends
from typing import Annotated

from app.services.auth import AuthService
from app.services.users import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

UnitOfWorkDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]

get_user_service = Annotated[UserService, Depends(UserService)]
get_auth_service = Annotated[AuthService, Depends(AuthService)]
verify = get_auth_service().verify
get_current_user_id = Annotated[int, Depends(verify)]

verify_from_query = get_auth_service().verify_from_query
get_current_user_id_from_query = Annotated[int, Depends(verify_from_query)]
