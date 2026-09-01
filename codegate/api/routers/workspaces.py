import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from codegate.api.dependencies import get_current_user, get_current_workspace, get_db
from codegate.database.models import Role, Team, TeamMember, User

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class WorkspaceCreate(BaseModel):
    name: str
    slug: str = None


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    slug: str = None
    role: str


def generate_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    List all workspaces the current user is a member of.
    """
    memberships = db.scalars(
        select(TeamMember)
        .where(TeamMember.user_id == user.id)
    ).all()

    result = []
    for member in memberships:
        # Avoid N+1 in a real app, but fine for Phase 7
        team = db.scalar(select(Team).where(Team.id == member.team_id))
        if team:
            role_str = member.role.value if hasattr(member.role, "value") else str(member.role)
            result.append(WorkspaceResponse(
                id=team.id,
                name=team.name,
                slug=getattr(team, "slug", generate_slug(team.name)),  # Phase 7 fallback
                role=role_str
            ))
    return result


@router.post("", response_model=WorkspaceResponse)
async def create_workspace(data: WorkspaceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new workspace and make the current user an ADMIN.
    """
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Workspace name is required")

    # Team is the backing model for Workspace
    new_team = Team(
        name=name,
        description="Workspace created via onboarding"
    )
    db.add(new_team)
    db.flush()  # to get new_team.id

    member = TeamMember(
        team_id=new_team.id,
        user_id=user.id,
        role=Role.ADMIN
    )
    db.add(member)
    
    # Automatically activate this new workspace if user has none
    if not user.active_workspace_id:
        user.active_workspace_id = new_team.id

    db.commit()

    return WorkspaceResponse(
        id=new_team.id,
        name=new_team.name,
        slug=generate_slug(new_team.name),
        role=Role.ADMIN.value
    )


@router.post("/{workspace_id}/activate")
async def activate_workspace(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Sets the active workspace for the user.
    """
    member = db.scalar(
        select(TeamMember)
        .where(TeamMember.user_id == user.id)
        .where(TeamMember.team_id == workspace_id)
    )
    
    if not member:
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")
        
    user.active_workspace_id = workspace_id
    db.commit()
    
    return {"status": "success", "active_workspace_id": workspace_id}


@router.get("/current")
async def get_current(workspace: Team = Depends(get_current_workspace)):
    """
    Returns the currently active workspace.
    """
    return {
        "id": workspace.id,
        "name": workspace.name
    }
