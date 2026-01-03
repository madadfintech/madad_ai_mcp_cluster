from fastapi import APIRouter
import random
from .models import *
from datetime import datetime
from shared.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Static responses for dummy APIs
DUMMY_NEWS = """
Breaking: Major advancements in AI technology announced today. Leading tech 
companies showcase new language models with unprecedented capabilities. Industry 
experts predict significant impact on enterprise automation and productivity tools.
"""

DUMMY_WEATHER_ADVICE = """
Weather Advisory: Based on current conditions, we recommend:
- Morning: Light jacket recommended, temperatures rising
- Afternoon: Peak sunshine hours, stay hydrated
- Evening: Cooling down, perfect for outdoor activities
- Air quality: Good, suitable for all activities
"""

@router.post("/search/serp", response_model=SerpSearchResponse)
async def run_serp_search(request: SerpSearchRequest):
    """Perform a SERP search - DUMMY API with static results"""
    logger.info("SERP search request", query=request.query, num_results=request.num_results)
    
    # Mock SERP results
    mock_results = [
        SerpResult(
            title=f"Result {i}: {request.query} - Comprehensive Guide",
            url=f"https://example{i}.com/{request.query.replace(' ', '-')}",
            snippet=f"Discover everything about {request.query}. Expert insights, tutorials, and best practices for {request.query}.",
            rank=i
        )
        for i in range(1, min(request.num_results + 1, 11))
    ]
    
    logger.info("SERP search completed", results_count=len(mock_results))
    
    return SerpSearchResponse(
        query=request.query,
        results=mock_results,
        total_results=len(mock_results)
    )

@router.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest):
    """Get weather information - DUMMY API with random data"""
    logger.info("Weather request", location=request.location, units=request.units)
    
    conditions = ["sunny", "partly cloudy", "cloudy", "light rain", "clear"]
    
    response = WeatherResponse(
        location=request.location,
        temperature=round(random.uniform(15, 30), 1),
        condition=random.choice(conditions),
        humidity=random.randint(40, 80),
        timestamp=datetime.now().isoformat()
    )
    
    logger.info("Weather response generated", location=request.location, condition=response.condition)
    return response

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text - DUMMY API with predefined translations"""
    logger.info("Translation request", 
               source=request.source_lang, 
               target=request.target_lang,
               text_length=len(request.text))
    
    translations = {
        ("en", "es"): "Texto traducido al español",
        ("en", "fr"): "Texte traduit en français",
        ("en", "de"): "Ins Deutsche übersetzter Text",
        ("es", "en"): "Text translated to English",
        ("fr", "en"): "Text translated to English",
        ("de", "en"): "Text translated to English",
    }
    
    key = (request.source_lang, request.target_lang)
    translated = translations.get(key, f"[TRANSLATED from {request.source_lang} to {request.target_lang}]: {request.text}")
    
    logger.info("Translation completed")
    
    return TranslationResponse(
        original_text=request.text,
        translated_text=translated,
        source_language=request.source_lang,
        target_language=request.target_lang,
        confidence=random.uniform(0.85, 0.99)
    )

@router.get("/external/status")
async def get_external_api_status():
    """Get status of external API connections - DUMMY API"""
    return {
        "serp_api": "operational",
        "weather_api": "operational", 
        "translation_api": "operational",
        "last_check": datetime.now().isoformat(),
        "response_times_ms": {
            "serp": 125,
            "weather": 85,
            "translation": 95
        }
    }

@router.get("/dummy/news")
async def get_latest_news():
    """Get latest news - DUMMY API with static content"""
    return {
        "headline": "AI Technology Breakthrough",
        "content": DUMMY_NEWS.strip(),
        "category": "Technology",
        "published": datetime.now().isoformat(),
        "source": "TechNews Global"
    }

@router.get("/dummy/advice")
async def get_weather_advice():
    """Get weather advice - DUMMY API with static content"""
    return {
        "title": "Daily Weather Advisory",
        "advice": DUMMY_WEATHER_ADVICE.strip(),
        "generated": datetime.now().isoformat(),
        "valid_until": "End of day"
    }