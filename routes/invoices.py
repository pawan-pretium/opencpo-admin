"""CPO invoices in the admin portal."""
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from shared import api, templates, CORE_API, CORE_API_KEY

router = APIRouter()


@router.get("/invoices", response_class=HTMLResponse)
async def invoices_page(request: Request):
    """Every CPO invoice."""
    try:
        data = await api("/public-sessions/invoices?limit=100")
        invoices = data.get("invoices", [])
        total = data.get("total", 0)
    except Exception:
        invoices = []
        total = 0
    return templates.TemplateResponse(request, "session_invoices.html", {
        "invoices": invoices,
        "total": total,
        "active": "invoices",
    })


@router.get("/invoices/{session_id}/pdf")
async def invoice_download(session_id: str):
    """The CPO invoice PDF."""
    headers = {"X-API-Key": CORE_API_KEY} if CORE_API_KEY else {}
    async with httpx.AsyncClient(base_url=CORE_API, timeout=30, headers=headers) as client:
        resp = await client.get(f"/api/v1/public-sessions/invoices/{session_id}/pdf")
    if resp.status_code != 200:
        return HTMLResponse("Invoice not found", status_code=resp.status_code)
    return Response(
        content=resp.content,
        media_type="application/pdf",
        headers={"Content-Disposition": resp.headers.get(
            "content-disposition", f'attachment; filename="invoice-{session_id[:8]}.pdf"'
        )},
    )
