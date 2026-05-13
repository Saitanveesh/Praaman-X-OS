from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.command import CommandCreate, CommandRead
from app.services.command_service import CommandService

router = APIRouter(prefix="/api/commands", tags=["commands"])
service = CommandService()


@router.post("", response_model=CommandRead)
async def submit_command(payload: CommandCreate, db: Session = Depends(get_db)):
    return await service.submit(db, payload)


@router.get("/{command_id}", response_model=CommandRead)
def get_command(command_id: str, db: Session = Depends(get_db)):
    command = service.get(db, command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return command
