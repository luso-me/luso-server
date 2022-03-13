from typing import IO

import structlog

from app.core.media.media_service import MediaService
from app.core.skill.model.base import SkillCreate, SkillUpdate
from app.database import get_db_client
from app.repositories.base import BaseRepository
from app.repositories.skill import SkillRepository, SkillAlreadyExistException

log = structlog.get_logger()


class SkillService:

    def __init__(self):
        self.skill_repo = SkillRepository(
            db_client_factory=get_db_client, db_name="luso", collection_name="skills"
        )
        self.media_service = MediaService()

    async def list_skills(self, limit: int = 100):
        return await self.skill_repo.list(limit)

    async def find_skill(self, skill_name, limit=100):
        return await self.skill_repo.find({"name": skill_name}, limit=limit)

    async def get_skill(self, skill_id: str):
        return await self.skill_repo.get(skill_id)

    async def delete_skill(self, skill_id: str):
        await self.skill_repo.delete(skill_id)

    async def create_skill(self, skill: SkillCreate):
        if await self.check_if_skill_exist(skill.name):
            log.error(
                f"Unable to create skill with name: [{skill.name}] because "
                f"it already exists"
            )
            raise SkillAlreadyExistException(f"Skill [{skill.name}] already exist")

        self._set_missing_resource_ids(skill)

        await self.skill_repo.create(skill)

    async def update_skill(self, skill_id: str, skill: SkillUpdate):
        self._set_missing_resource_ids(skill)

        await self.skill_repo.update(skill_id, skill)

    async def check_if_skill_exist(self, skill_name: str):
        skill = await self.skill_repo.find({"name": skill_name})
        log.info(f"Skill is {skill}")

        if skill:
            return True

        return False

    @classmethod
    def _set_missing_resource_ids(cls, skill):
        if skill.resources is not None:
            for resource in skill.resources:
                if not resource.id:
                    log.info(f"resource id missing for skill: [{skill.name}]")
                    resource.id = BaseRepository.generate_uuid()
                for item in resource.items:
                    if not item.id:
                        log.info(f"item id missing for resource: [{resource.name}]")
                        item.id = BaseRepository.generate_uuid()

    async def update(self, skill_id: str, skill: SkillUpdate):
        return await self.skill_repo.update(skill_id, skill)

    async def update_skill_icon(self, skill_id: str, icon_name: str, icon_file: IO):
        skill = SkillUpdate()
        skill.icon_link = await self.media_service.upload_image(icon_name, icon_file)

        return await self.skill_repo.update(skill_id, skill)
