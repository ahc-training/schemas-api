import json
from fastapi import APIRouter, Request
from data.core import db_dependency, DbSchema
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import and_, desc, func


class Schema(BaseModel):
    id: int
    name: str
    type: str
    data: str
    modifiedon: datetime 


class SchemaRouter:

    def __init__(self, prefix: str, schema_type: str):
        self.type = schema_type
        self.router = APIRouter(prefix=prefix)
        self.router.add_api_route("/{id}", self.get_schema, methods=["GET"])
        self.router.add_api_route("/{id}", self.create_schema, methods=["POST"])
        self.router.add_api_route("/{id}", self.remove_schema, methods=["DELETE"])

    @property
    def get_router(self) -> APIRouter:
        return self.router


    async def get_schema(self, id: str, db: db_dependency, version: int = None):
        schema = db.query(DbSchema).filter(and_(DbSchema.name == id, DbSchema.schema_type == self.type, DbSchema.version == (version if version is not None else DbSchema.version))).order_by(desc(DbSchema.version)).first()
        return (schema.data if schema is not None else schema)
        
        
    async def create_schema(self, id: str, request: Request, db: db_dependency):
        try:
            data = json.dumps(await request.json())
            version = db.query(func.max(DbSchema.version)).filter(and_(DbSchema.name == id, DbSchema.schema_type == self.type)).scalar()
            version = 1 if version is None else version + 1
            schema = DbSchema(name=id, schema_type=self.type, data=data, version=version, modifiedon=datetime.now())
            db.add(schema)
            db.commit()
        except Exception as ex:
            db.rollback()
            raise ex


    async def remove_schema(self, id: str, db: db_dependency, version: int = None):
        try:
            db.query(DbSchema).filter(and_(DbSchema.name == id, DbSchema.schema_type == self.type, DbSchema.version == (version if version is not None else DbSchema.version))).delete()
            db.commit()
        except Exception as ex:
            db.rollback()
            raise ex