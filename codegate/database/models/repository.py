from enum import Enum
from typing import Optional, List
from sqlalchemy import String, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from codegate.database.base import Base, TimestampMixin

class Provider(str, Enum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET = "BITBUCKET"
    AZURE_DEVOPS = "AZURE_DEVOPS"
    GITEA = "GITEA"
    OTHER = "OTHER"

class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider: Mapped[Provider] = mapped_column(String(50), nullable=False)
    provider_repository_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False, default="main")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    pull_requests: Mapped[List["PullRequest"]] = relationship(
        "PullRequest", 
        back_populates="repository", 
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("provider", "full_name", name="uix_provider_full_name"),
    )
