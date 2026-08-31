from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegate.database.base import Base, TimestampMixin


class Role(str, Enum):
    ADMIN = "ADMIN"
    MAINTAINER = "MAINTAINER"
    REVIEWER = "REVIEWER"
    DEVELOPER = "DEVELOPER"

class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    members: Mapped[List["TeamMember"]] = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[Role] = mapped_column(String(50), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    # user relationship can be added here if we need to query user from member

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uix_team_id_user_id"),
    )
