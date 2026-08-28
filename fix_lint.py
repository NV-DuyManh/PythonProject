import re

with open('codegate/database/models/analysis.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix unused JSONB import
content = content.replace(
    'from sqlalchemy.dialects.postgresql import JSONB\n',
    ''
)
content = content.replace(
    'from typing import Any, List, Optional\n',
    'from typing import Any, List, Optional, TYPE_CHECKING\n\nif TYPE_CHECKING:\n    from codegate.database.models.pull_request import PullRequest\n'
)

# 2. Wrap long lines
content = content.replace(
    'pull_request_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False, index=True)',
    'pull_request_id: Mapped[int] = mapped_column(\n        ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False, index=True\n    )'
)
content = content.replace(
    'analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)',
    'analysis_run_id: Mapped[int] = mapped_column(\n        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True\n    )'
)

with open('codegate/database/models/analysis.py', 'w', encoding='utf-8') as f:
    f.write(content)
