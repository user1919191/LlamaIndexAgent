from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"code": 40001, "message": "请求参数不合法", "details": {"errors": exc.errors()}},
        headers={"X-Trace-Id": request.state.trace_id},
    )
