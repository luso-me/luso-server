from http import HTTPStatus
from typing import List, Optional

import structlog
from fastapi import HTTPException, status, APIRouter, Depends, UploadFile

from app.adapters.dependencies.auth import get_current_user
from app.adapters.dependencies.db import skill_repository
from app.core.media import media_service
from app.core.media.media_service import MediaService
from app.core.skill import skill_service
from app.core.skill.model.base import SkillCreate, SkillRead, SkillUpdate
from app.core.user.model.base import UserRead
from app.repositories.skill import SkillRepository

log = structlog.get_logger()

router = APIRouter(prefix="/skills")


@router.post(
    "",
    response_description="Add new skill",
    response_model=SkillRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    skill: SkillCreate, current_user: UserRead = Depends(get_current_user)
):
    log.debug(f"attempting to create skill with body {skill}")
    return await skill_service.create_skill(skill)


@router.get("", response_description="List all skills", response_model=List[SkillRead])
async def list_skills(
    limit: int = 100,
    skill_repo: SkillRepository = Depends(skill_repository),
    current_user: UserRead = Depends(get_current_user),
):
    skills = await skill_repo.list(limit)
    log.debug("skills found", skills=skills)
    return skills


@router.get(
    "/find", response_description="Find skill by...", response_model=List[SkillRead]
)
async def find_query(
    skill_name: Optional[str] = None,
    limit: int = 10,
    skill_repo: SkillRepository = Depends(skill_repository),
    current_user: UserRead = Depends(get_current_user),
):
    if skill_name:
        log.info("searching for skills with name", skill_name=skill_name)
        return await skill_repo.find({"name": skill_name}, limit=limit)

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="No known search parameter passed"
    )


@router.get(
    "/{skill_id}", response_description="Get a single skill", response_model=SkillRead
)
async def show_skill(
    skill_id: str,
    skill_repo: SkillRepository = Depends(skill_repository),
    current_user: UserRead = Depends(get_current_user),
):
    if (skill := await skill_repo.get(skill_id)) is not None:
        return skill

    raise HTTPException(status_code=404, detail=f"skill {skill_id} not found")


@router.put(
    "/{skill_id}", response_description="Update a skill", response_model=SkillRead
)
async def update_skill(
    skill_id: str,
    skill: SkillUpdate,
    current_user: UserRead = Depends(get_current_user),
):
    return await skill_service.update_skill(skill_id, skill)


@router.delete("/{skill_id}", response_description="Delete a skill")
async def delete_skill(
    skill_id,
    skill_repo: SkillRepository = Depends(skill_repository),
    current_user: UserRead = Depends(get_current_user),
):
    await skill_repo.delete(skill_id)


@router.post("/{skill_id}/icon")
async def skill_icon_upload(skill_id: str, file: UploadFile, skill_repo: SkillRepository = Depends(skill_repository), media_service: MediaService = Depends(MediaService)):
    log.info("file upload", filename=file.filename)
    skill = SkillUpdate()
    skill.icon_link = await media_service.upload_image(file.filename, file.file)
    return await skill_repo.update(skill_id, skill)
