from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)

def paginate(items: list, total: int, params: PaginationParams) -> dict:
    pages = (total + params.page_size - 1) // params.page_size
    return {
        "items": items,
        "page": params.page,
        "page_size": params.page_size,
        "total": total,
        "pages": pages
    }
