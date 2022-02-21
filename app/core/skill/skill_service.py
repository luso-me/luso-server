import structlog

from app.core.skill.model.base import SkillCreate, SkillUpdate
from app.database import get_db_client
from app.repositories.base import BaseRepository
from app.repositories.skill import SkillRepository, SkillAlreadyExistException

log = structlog.get_logger()

skill_repo = SkillRepository(db_client_factory=get_db_client,
                             db_name='luso',
                             collection_name='skills')


async def create_skill(skill: SkillCreate):
    _set_ids(skill)
    # validate skill doesn't already exist
    find_ = await skill_repo.find()

    if (len(find_) is 0):
        await skill_repo.create(skill)
    else:
        raise SkillAlreadyExistException(
            'A skill with name: [{}] already exist')


async def update_skill(skill_id: str, skill: SkillUpdate):
    _set_ids(skill)

    await skill_repo.update(skill_id, skill)


def _set_ids(skill):
    for resource in skill.resources:
        if not resource.id:
            log.info(f"resource id missing for skill: [{skill.name}]")
            resource.id = BaseRepository.generate_uuid()
        for item in resource.items:
            if not item.id:
                log.info(f"item id missing for resource: [{resource.name}] ")
                item.id = BaseRepository.generate_uuid()
