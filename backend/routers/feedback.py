from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.client import get_pool

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    message_id: str
    rating: str          # "up" or "down"
    user_query: str = ""
    message_content: str = ""


class FeedbackSummary(BaseModel):
    total: int
    thumbs_up: int
    thumbs_down: int
    up_pct: float
    down_pct: float


@router.post("", status_code=201)
async def submit_feedback(req: FeedbackRequest):
    if req.rating not in ("up", "down"):
        raise HTTPException(status_code=400, detail="rating must be 'up' or 'down'")

    content_hash = hashlib.sha256(req.message_content.encode()).hexdigest()[:16]

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO message_feedback
                (message_id, rating, user_query, content_hash, created_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (message_id) DO UPDATE
                SET rating = EXCLUDED.rating,
                    created_at = EXCLUDED.created_at
            """,
            req.message_id,
            req.rating,
            req.user_query[:500],       # cap length
            content_hash,
            datetime.now(timezone.utc),
        )

    return {"status": "ok"}


@router.get("/summary", response_model=FeedbackSummary)
async def feedback_summary():
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                COUNT(*)                                        AS total,
                COUNT(*) FILTER (WHERE rating = 'up')          AS thumbs_up,
                COUNT(*) FILTER (WHERE rating = 'down')        AS thumbs_down
            FROM message_feedback
            """
        )

    total = row["total"] or 0
    up = row["thumbs_up"] or 0
    down = row["thumbs_down"] or 0

    return FeedbackSummary(
        total=total,
        thumbs_up=up,
        thumbs_down=down,
        up_pct=round((up / total * 100), 1) if total else 0.0,
        down_pct=round((down / total * 100), 1) if total else 0.0,
    )


@router.get("/recent")
async def recent_feedback(limit: int = 20):
    """Return the most recent feedback entries — useful for debugging low-rated responses."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT message_id, rating, user_query, content_hash, created_at
            FROM message_feedback
            ORDER BY created_at DESC
            LIMIT $1
            """,
            limit,
        )
    return [dict(r) for r in rows]
