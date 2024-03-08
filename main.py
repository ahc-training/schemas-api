from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from routers.schemas import SchemaRouter
from data.core import db_dependency, DbUser
from sqlalchemy import and_

security = HTTPBasic()


def verification(db: db_dependency, creds: HTTPBasicCredentials = Depends(security)):
    user = db.query(DbUser).filter(and_(DbUser.username == creds.username, DbUser.password == creds.password)).first()
    if user is None :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user name or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user is not None


router = APIRouter(dependencies=[Depends(security), Depends(verification)])
app = FastAPI(dependencies=[Depends(security), Depends(verification)])


types = [
    { "prefix": "/avro", "type": "avsc"},
    { "prefix": "/json", "type": "json"}
]

[app.include_router(SchemaRouter(prefix=t["prefix"], schema_type=t["type"]).get_router) for t in types]


