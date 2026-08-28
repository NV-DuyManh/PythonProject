from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class CodeGateException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class NotFoundException(CodeGateException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class ConflictException(CodeGateException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)

class ValidationException(CodeGateException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(CodeGateException)
    async def codegate_exception_handler(request: Request, exc: CodeGateException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message},
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Do not expose raw database exceptions or stack traces
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
        )
