from pydantic import BaseModel, Field
from typing import Optional

class LoanApplication(BaseModel):
    """
    Standard schema for a loan request input.
    Based on the Aegis-Finance Phase 1 Data Audit.
    """
    income: float = Field(..., description="Annual income of the applicant")
    credit_score: int = Field(..., description="FICO or equivalent credit score (300-850)")
    D_39: Optional[float] = Field(None, description="Delinquency marker 39")
    D_42: Optional[float] = Field(None, description="Delinquency marker 42 (High Sparsity)")
    D_43: Optional[float] = Field(None, description="Delinquency marker 43 (High Sparsity)")
    D_114: Optional[float] = Field(None, description="Delinquency marker 114 (Categorical)")

    class Config:
        json_schema_extra = {
            "example": {
                "income": 85000.0,
                "credit_score": 720,
                "D_39": 1.0,
                "D_42": None,
                "D_43": None,
                "D_114": 1.0
            }
        }

class RiskResponse(BaseModel):
    """
    Standardized response from the Aegis Risk Gateway.
    """
    status: str
    probability: float
    action: str
