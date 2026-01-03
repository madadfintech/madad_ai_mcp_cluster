from pydantic import BaseModel
from typing import List, Optional

class SerpSearchRequest(BaseModel):
    query: str
    num_results: int = 10
    country: str = "US"

class SerpResult(BaseModel):
    title: str
    url: str
    snippet: str
    rank: int

class SerpSearchResponse(BaseModel):
    query: str
    results: List[SerpResult]
    total_results: int

class WeatherRequest(BaseModel):
    location: str
    units: str = "metric"

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    condition: str
    humidity: int
    timestamp: str

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float