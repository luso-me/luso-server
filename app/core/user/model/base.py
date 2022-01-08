from typing import List, Optional

import pydantic
from pydantic import BaseModel, Field

from app.core.user.model.user_skill import UserSkill


class UserFields:
    user_id = Field(
        description='ID of user',
        example='some id',
        min_length=22,
        max_length=22
    )
    name = Field(
        description='Name',
        example='John Doe',
        min_length=1
    )
    skills = Field(
        description='List of skills',
        default_factory=list
    )
    email = Field(
        description='Users emails address'
    )
    active = Field(True)


class UserUpdate(BaseModel):
    name: Optional[str] = UserFields.name
    email: Optional[str] = UserFields.email
    skills: Optional[List[UserSkill]] = UserFields.skills


class UserCreate(UserUpdate):
    name: str = UserFields.name
    email: str = UserFields.email
    github_user_id: Optional[str]


class UserRead(UserCreate):
    id: str = UserFields.user_id

    @pydantic.root_validator(pre=True)
    def _set_user_id(cls, data):
        """Swap the field _id to user_id (this could be done with field alias, by setting the field as "_id"
        and the alias as "user_id", but can be quite confusing)"""
        document_id = data.get("_id")
        if document_id:
            data['id'] = document_id
        return data


class UserAdmin(UserRead):
    active: bool = UserFields.active