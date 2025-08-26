from pydantic import BaseModel, Field

class AssessmentGroups(BaseModel):
    id: str = Field(..., description="Placeholder ID like G1, G2, etc.")
    course_id: str | None = Field()
    weight: float = Field(...)
    count: int = Field(...)
    drop: int = Field(...)
    name: str = Field(...)
    optional: bool = Field(...)

class Assessments(BaseModel):
    id: str | None = None
    group_id: str = Field(...)
    weight: float = Field(...)
    index: int = Field(...)
    due_date: str | None = Field() 
    name: str = Field(...)

class ParsedAssessmentOutput(BaseModel):
    assessment_groups: list[AssessmentGroups]
    assessments: list[Assessments]

class Personnels(BaseModel):
    course_id: str | None = None
    name: str = Field(...)
    role: str = Field(...)
    email: str | None = Field()

class ParsedPersonnelsOutput(BaseModel):
    personnels: list[Personnels]
