from datetime import datetime

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    member_since: datetime
    account_age_days: int
    profile_completion_percentage: int
    profile_completion_missing_fields: list[str]