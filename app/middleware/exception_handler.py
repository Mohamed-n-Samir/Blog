import logging

from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException

from app.utils.exceptions import APPException
from app.utils.helpers import is_api_request

from app.constants.constant import ROOT_DIR
from app.config.templates import templates

logger = logging.getLogger(__name__)

template_dir = ROOT_DIR / "templates"


def get_error_template(status_code: int) -> str:
    """
    Returns the matching error template if it exists,
    otherwise falls back to errors/error.html.
    """
    template = template_dir / "errors" / f"{status_code}.html"

    if template.exists():
        return f"errors/{status_code}.html"

    return "errors/error.html"


def error_response(
    request: Request,
    *,
    status_code: int,
    message: str,
    details: dict[str, Any] | None = None,
):
    """
    Returns either JSON or HTML depending on the request.
    """

    print(False)

    if is_api_request(request):
        print(True)
        body = {
            "status": "error",
            "message": message,
        }

        if details:
            body["details"] = details

        return JSONResponse(
            status_code=status_code,
            content=body,
        )

    return templates.TemplateResponse(
        request=request,
        name=get_error_template(status_code),
        context={
            "status_code": status_code,
            "message": message,
            "details": details,
        },
        status_code=status_code,
    )


async def app_exception_handler(
    request: Request,
    exc: APPException,
):
    return error_response(
        request=request,
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return error_response(
        request=request,
        status_code=exc.status_code,
        message=str(exc.detail),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation failed",
        details={
            "errors": exc.errors(),
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception",
        exc_info=exc,
    )

    return error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal server error",
    )