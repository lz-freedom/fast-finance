from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Any, Dict
from app.services.investing_service import InvestingService

router = APIRouter()

@router.get("/search", response_model=Dict[str, Any])
async def search_investing(
    keyword: str = Query(..., description="Search keyword"),
    country_code: Optional[str] = Query(None, description="Country code / domain ID for the request header")
):
    """
    Search for financial instruments on Investing.com.
    
    - **keyword**: The search term (e.g., 'aapl')
    - **country_code**: Optional domain ID to filter results (header: domain-id)
    """
    try:
        results = InvestingService.search(keyword=keyword, country_code=country_code)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/translations", response_model=Dict[str, List[Dict[str, Any]]])
async def get_translations(
    symbol: str = Query(..., description="Stock Symbol"),
    country_codes: List[str] = Query(..., description="List of country codes to fetch translations for")
):
    """
    Get translations for a stock symbol.
    """
    try:
        return InvestingService.get_translations(symbol, country_codes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
