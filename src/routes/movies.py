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

    if per_page <= 0:
        raise HTTPException(
            status_code=400, detail="per_page must be >= 1"
        )

    total_items_result = await db.execute(
        select(func.count()).select_from(MovieModel)
    )
    total_items = total_items_result.scalar_one()
    total_pages = math.ceil(total_items / per_page)

    result = await db.execute(
        select(MovieModel)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    movies = result.scalars().all()

    base_url = str(request.url).split("?")[0]
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="No movies found."
        )


    def build_url(page_number: int) -> str:
        return f"{base_url}?page={page_number}&per_page={per_page}"

    return {

        "prev_page": build_url(page - 1) if page > 1 else None,
        "next_page": build_url(page + 1) if page < total_pages else None,
        "total_pages": total_pages,
        "total_items": total_items,
        "movies": movies
    }


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
