from pydantic import BaseModel, Field

class ProjectInput(BaseModel):
    goal: float = Field(..., description="The funding goal in USD")
    category: str = Field(..., description="The parent category")
    subcategory: str = Field(..., description="The specific subcategory")
    launch_month: int = Field(..., ge=1, le=12, description="Month of launch (1-12)")
    launch_day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    campaign_duration: int = Field(..., ge=1, le=90, description="Duration of campaign in days")
