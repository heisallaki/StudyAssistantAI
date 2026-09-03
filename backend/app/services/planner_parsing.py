import json

from pydantic import BaseModel, Field

MAX_RECOMMENDATIONS = 5


class GeneratedRecommendation(BaseModel):
    subject: str
    action: str
    reason: str


class GeneratedRecommendationSet(BaseModel):
    recommendations: list[GeneratedRecommendation] = Field(default_factory=list)


def _is_recommendation_valid(recommendation: GeneratedRecommendation) -> bool:
    return (
        bool(recommendation.subject.strip())
        and bool(recommendation.action.strip())
        and bool(recommendation.reason.strip())
    )


def parse_generated_recommendations(raw_text: str) -> list[GeneratedRecommendation]:
    data = json.loads(raw_text)
    parsed = GeneratedRecommendationSet.model_validate(data)
    valid = [recommendation for recommendation in parsed.recommendations if _is_recommendation_valid(recommendation)]
    return valid[:MAX_RECOMMENDATIONS]