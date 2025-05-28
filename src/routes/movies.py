from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request
)

from database.models import MovieModel
from database import get_db
from typing import List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.movies import (
    MovieDetailResponseSchema,
    MovieCreate,
    MovieListResponseSchema,
    PaginationParams,
)
import math

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def read_movies(
    request: Request,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    page = pagination.page
    per_page = pagination.per_page

    if page <= 0:
        raise HTTPException(
            status_code=400,
            detail="page must be >= 1"
        )
    if per_page <= 0:
        raise HTTPException(
            status_code=400,
            detail="per_page must be >= 1"
        )

    total_items_result = await db.execute(
        select(func.count()).select_from(MovieModel)
    )
    total_items = total_items_result.scalar_one()
    total_pages = max(math.ceil(total_items / per_page), 1)

    result = await db.execute(
        select(MovieModel)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    movies = result.scalars().all()

    base_url = str(request.url).split("?")[0]
    query_params = request.query_params.multi_items()

    def build_page_url(target_page: int) -> str | None:
        if target_page < 1 or target_page > total_pages:
            return None
        params = [(k, v) for k, v in query_params if k not in {"page"}]
        params.append(("page", str(target_page)))
        return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params)}"

    return MovieListResponseSchema(
        movies=movies,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_items=total_items,
        next_page_url=build_page_url(page + 1),
        prev_page_url=build_page_url(page - 1)
    )


@router.get(
    "/movies/{movie_id}/",
    response_model=MovieDetailResponseSchema
)
async def get_movie(
        movie_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MovieModel).where(MovieModel.id == movie_id)
    )
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found."
        )
    return movie


@router.post(
    "/movies/",
    response_model=MovieDetailResponseSchema
)
async def create_movie(
        movie: MovieCreate, db: AsyncSession = Depends(get_db)
):
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    return new_movie
