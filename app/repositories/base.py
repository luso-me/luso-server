import abc
import logging
from typing import Generic, TypeVar, Type, List

from pydantic import BaseModel
import shortuuid  # type: ignore

from app.repositories.exceptions import DocumentNotFoundException, DocumentCouldNotBeCreatedException

CREATE_SCHEMA = TypeVar('CREATE_SCHEMA', bound=BaseModel)
READ_SCHEMA = TypeVar('READ_SCHEMA', bound=BaseModel)
UPDATE_SCHEMA = TypeVar('UPDATE_SCHEMA', bound=BaseModel)

log = logging.getLogger(__name__)


class BaseRepository(Generic[CREATE_SCHEMA, READ_SCHEMA, UPDATE_SCHEMA]):
    def __init__(self, db_session, db_name: str, collection: str):
        self._collection = db_session[db_name][collection]

    @property
    @abc.abstractmethod
    def _read_schema(self) -> Type[READ_SCHEMA]:
        ...

    @staticmethod
    def _generate_uuid():
        return shortuuid.uuid()

    async def get(self, _id: str) -> READ_SCHEMA:
        document = await self._collection.find_one({"_id": _id})
        if not document:
            raise DocumentNotFoundException()
        return self._read_schema(**document)

    async def list(self, limit=None) -> List[READ_SCHEMA]:
        return [self._read_schema(**document) for document in await self._collection.find().to_list(limit)]

    async def create(self, create: CREATE_SCHEMA) -> READ_SCHEMA:
        document = create.dict()
        document["_id"] = self._generate_uuid()

        result = await self._collection.insert_one(document)

        if not result.acknowledged:
            log.error(f'failed to create document {document}')
            raise DocumentCouldNotBeCreatedException()

        return await self.get(result.inserted_id)

    async def update(self, _id: str, update: UPDATE_SCHEMA) -> READ_SCHEMA:
        document = update.dict(exclude_none=True)

        result = await self._collection.update_one({"_id": _id}, {"$set": document})
        if not result.modified_count:
            log.debug('document not modified')

        return await self.get(_id)

    async def delete(self, _id: str):
        result = await self._collection.delete_one({"_id": _id})
        if not result.deleted_count:
            raise DocumentNotFoundException()

    async def find(self, search_dict) -> List[READ_SCHEMA]:
        return [self._read_schema(**document) for document in await self._collection.find(search_dict).to_list(100)]
