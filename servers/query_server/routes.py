from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import User, UserResponse, Product, ProductQuery
from datetime import datetime
from shared.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Mock data with realistic content
USERS = [
    User(id=1, name="Alice Johnson", email="alice.johnson@techcorp.com", created_at=datetime.now()),
    User(id=2, name="Bob Smith", email="bob.smith@innovate.io", created_at=datetime.now()),
    User(id=3, name="Carol Williams", email="carol.w@startup.dev", created_at=datetime.now()),
    User(id=4, name="David Brown", email="d.brown@enterprise.com", created_at=datetime.now()),
]

PRODUCTS = [
    Product(id=1, name="MacBook Pro 16\"", category="electronics", price=2499.99, in_stock=True),
    Product(id=2, name="Python Crash Course", category="books", price=39.99, in_stock=True),
    Product(id=3, name="iPhone 15 Pro", category="electronics", price=999.99, in_stock=False),
    Product(id=4, name="Clean Code", category="books", price=44.99, in_stock=True),
    Product(id=5, name="iPad Air", category="electronics", price=599.99, in_stock=True),
    Product(id=6, name="Designing Data-Intensive Applications", category="books", price=54.99, in_stock=True),
]

# Static text responses - DUMMY APIS
KNOWLEDGE_BASE = {
    "company_info": """
    TechCorp Solutions is a leading technology company specializing in AI-powered 
    enterprise solutions. Founded in 2015, we serve over 500 Fortune 500 companies 
    with our cutting-edge products and services. Our mission is to democratize 
    AI technology and make it accessible to businesses of all sizes.
    
    Key Achievements:
    - 500+ Enterprise Clients
    - 99.99% Uptime SLA
    - ISO 27001 Certified
    - $500M+ Annual Revenue
    """,
    
    "product_catalog": """
    Our comprehensive product catalog includes:
    
    1. Enterprise AI Platform: Cloud-based machine learning infrastructure with 
       auto-scaling capabilities, supporting TensorFlow, PyTorch, and custom models.
       
    2. Data Analytics Suite: Real-time business intelligence tools featuring 
       interactive dashboards, predictive analytics, and custom reporting.
       
    3. Automation Hub: Workflow automation and process optimization platform 
       with drag-and-drop interface and 200+ pre-built connectors.
       
    4. Security Shield: AI-powered cybersecurity solutions including threat 
       detection, vulnerability scanning, and automated incident response.
    """,
    
    "support_info": """
    Customer Support is available 24/7 through multiple channels:
    
    - Email: support@techcorp.com (Response within 2 hours)
    - Phone: 1-800-TECH-CORP (24/7 availability)
    - Live Chat: Available on our website (Instant response)
    - Dedicated Account Manager: For enterprise clients
    - Knowledge Base: 1000+ articles and tutorials
    - Community Forum: Active developer community
    
    Priority Levels:
    - P1 (Critical): 15-minute response time
    - P2 (High): 2-hour response time
    - P3 (Medium): 8-hour response time
    - P4 (Low): 24-hour response time
    """
}

@router.get("/users", response_model=UserResponse)
async def get_users(limit: int = Query(default=10, ge=1, le=100), 
                   offset: int = Query(default=0, ge=0)):
    """Get paginated list of users"""
    logger.info("Fetching users", limit=limit, offset=offset)
    users = USERS[offset:offset + limit]
    return UserResponse(users=users, total=len(USERS))

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user by ID"""
    logger.info("Fetching user by ID", user_id=user_id)
    user = next((u for u in USERS if u.id == user_id), None)
    if not user:
        logger.warning("User not found", user_id=user_id)
        raise HTTPException(404, "User not found")
    return user

@router.post("/products/search", response_model=List[Product])
async def search_products(query: ProductQuery):
    """Search products with filters"""
    logger.info("Searching products", filters=query.dict())
    filtered = PRODUCTS[:]
    
    if query.category:
        filtered = [p for p in filtered if p.category == query.category]
    if query.min_price:
        filtered = [p for p in filtered if p.price >= query.min_price]
    if query.max_price:
        filtered = [p for p in filtered if p.price <= query.max_price]
    
    logger.info("Product search completed", results_count=len(filtered))
    return filtered

@router.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    logger.info("Fetching analytics summary")
    return {
        "total_users": len(USERS),
        "total_products": len(PRODUCTS),
        "products_in_stock": len([p for p in PRODUCTS if p.in_stock]),
        "average_product_price": round(sum(p.price for p in PRODUCTS) / len(PRODUCTS), 2),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/knowledge/{topic}")
async def get_knowledge(topic: str):
    """Get static knowledge base content - DUMMY API"""
    logger.info("Fetching knowledge", topic=topic)
    
    if topic not in KNOWLEDGE_BASE:
        available_topics = list(KNOWLEDGE_BASE.keys())
        logger.warning("Topic not found", topic=topic, available=available_topics)
        raise HTTPException(404, f"Topic not found. Available topics: {available_topics}")
    
    return {
        "topic": topic,
        "content": KNOWLEDGE_BASE[topic].strip(),
        "last_updated": datetime.now().isoformat()
    }

@router.get("/dummy/greeting")
async def get_greeting():
    """Returns a static greeting message - DUMMY API"""
    return {
        "message": "Hello! Welcome to TechCorp's Query Server. We provide read-only access to user data, product catalogs, analytics, and our comprehensive knowledge base.",
        "server": "Query Server",
        "version": "1.0.0",
        "capabilities": [
            "User Management",
            "Product Catalog",
            "Analytics",
            "Knowledge Base"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/dummy/status")
async def get_system_status():
    """Returns static system status information - DUMMY API"""
    return {
        "status": "All systems operational",
        "uptime": "99.99%",
        "active_connections": 142,
        "last_backup": "2024-01-15T03:00:00Z",
        "database_status": "healthy",
        "cache_status": "healthy",
        "api_response_time_ms": 45,
        "total_requests_today": 125430,
        "timestamp": datetime.now().isoformat()
    }