from fastapi import APIRouter, HTTPException
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from app.services.investing_service import InvestingService

router = APIRouter()

class SearchRequest(BaseModel):
    keyword: str
    country_code: Optional[str] = None

class TranslationsRequest(BaseModel):
    symbol: str
    country_codes: List[str]

@router.post("/search", response_model=Dict[str, Any])
async def search_investing(request: SearchRequest):
    """
    Search for financial instruments on Investing.com.
    
    - **keyword**: The search term (e.g., 'aapl')
    - **country_code**: Optional domain ID to filter results (header: domain-id)
    """
    try:
        results = InvestingService.search(keyword=request.keyword, country_code=request.country_code)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translations", response_model=Dict[str, List[Dict[str, Any]]])
async def get_translations(request: TranslationsRequest):
    """
    Get translations for a stock symbol.
    """
    try:
        return InvestingService.get_translations(request.symbol, request.country_codes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
