from pydantic import BaseModel

from app.core.security import Permission, Role


class CurrentUser(BaseModel):
    id: str
    role: Role
    permissions: list[Permission] = []
