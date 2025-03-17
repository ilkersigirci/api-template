from fastapi import APIRouter, FastAPI, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/docs", include_in_schema=False)
async def swagger_ui_html(request: Request) -> HTMLResponse:
    """Swagger UI.

    Args:
        request: Current Request.

    Returns:
        Rendered Swagger UI.

    NOTE:
        swagger-ui-bundle.js: https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js
        swagger-ui.css: https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css
    """
    app: FastAPI = request.app

    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=str(request.url_for("swagger_ui_redirect")),
        swagger_js_url="/static/docs/swagger-ui-bundle.js",
        swagger_css_url="/static/docs/swagger-ui.css",
    )


@router.get("/swagger-redirect", include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    """Redirect to swagger.

    Returns:
        Redirect.
    """
    return get_swagger_ui_oauth2_redirect_html()


@router.get("/redoc", include_in_schema=False)
async def redoc_html(request: Request) -> HTMLResponse:
    """Redoc UI.

    Args:
        request: Current Request.

    Returns:
        Rendered Redoc UI.

    NOTE:
        redoc.standalone.js: https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js
    """
    app: FastAPI = request.app

    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/docs/redoc.standalone.js",
    )
