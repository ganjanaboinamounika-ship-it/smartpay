from pydantic import BaseModel


class FraudRuleResult(BaseModel):
    rule: str
    triggered: bool
    score: int
    reason: str


class FraudEvaluationResponse(BaseModel):
    total_score: int
    risk_level: str
    triggered_rules: list[FraudRuleResult]