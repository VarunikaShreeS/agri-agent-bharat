from pydantic import BaseModel


class Diagnosis(BaseModel):
    disease: str
    severity: float      # clamped to 0-1 in code
    confidence: float    # clamped to 0-1 in code
    visible_symptoms: str
