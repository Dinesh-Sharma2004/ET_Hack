from pydantic import BaseModel


class BriefingSection(BaseModel):
    title: str
    bullets: list[str]


class BriefingResponse(BaseModel):
    headline: str
    summary: str
    insights: list[BriefingSection]
    risks: list[str]
    opportunities: list[str]
    faqs: list[str]
    memory_hint: str


class BriefingChatRequest(BaseModel):
    question: str
    mode: str = "expert"
    history: list[str] = []


class BriefingChatResponse(BaseModel):
    answer: str
    supporting_articles: list[str]
    follow_ups: list[str]
