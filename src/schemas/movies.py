from pydantic import BaseModel
from pydantic.config import ConfigDict
from datetime import date
from typing import List, Optional
from fastapi import Query


class MovieDetailResponseSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str

    class Config:
        orm_mode = True


class MovieCreate(BaseModel):
    name: str
    date: date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    orig_lang: str
    budget: float
    country: str


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1)
    per_page: int = Query(10, ge=1, le=20)


class MovieListResponseSchema(BaseModel):
    movies: List[MovieDetailResponseSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int

    class Config:
        orm_mode = True
