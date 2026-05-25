from typing import Any, Dict

from tools.api_wrappers.read.non_transactional import MadadOffersNonTransactionalReadAPI

from . import mcp


offers_read_api = MadadOffersNonTransactionalReadAPI()


@mcp.tool
async def madad_offers_get_my_offers(access_token: str) -> Dict[str, Any]:
    """Get active offers for the current merchant."""
    return await offers_read_api.get_my_offers(access_token=access_token)


@mcp.tool
async def madad_offers_get_offer(access_token: str, offer_id: str) -> Dict[str, Any]:
    """Get a single financing offer by ID."""
    return await offers_read_api.get_offer(access_token=access_token, offer_id=offer_id)


@mcp.tool
async def madad_offers_get_offers(access_token: str) -> Dict[str, Any]:
    """Get all active financing offers visible to the authenticated user."""
    return await offers_read_api.get_offers(access_token=access_token)


@mcp.tool
async def madad_offers_get_extension_request(access_token: str, offer_id: str) -> Dict[str, Any]:
    """Get the current merchant's extension request for an offer."""
    return await offers_read_api.get_extension_request(access_token=access_token, offer_id=offer_id)
