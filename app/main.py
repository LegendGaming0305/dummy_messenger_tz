from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from asyncpg.exceptions import SerializationError
import asyncio

from .database import get_async_session
from .models import Message, UserCounter
from .schemas import MessageCreate, MessageResponse

app = FastAPI()

MAX_RETRIES = 7
BASE_DELAY = 0.1

@app.post("/message", response_model=list[MessageResponse])
async def create_message(
    message: MessageCreate,
    db: AsyncSession = Depends(get_async_session)
):
    retry_delay = BASE_DELAY
    for attempt in range(MAX_RETRIES):
        try:
            async with db.begin():
                user_counter = await db.execute(
                    select(UserCounter).where(UserCounter.sender_name == message.sender).with_for_update(skip_locked=True)
                )
                user_counter = user_counter.scalar_one_or_none()
                
                if user_counter:
                    user_counter.counter += 1
                else:
                    user_counter = UserCounter(sender_name=message.sender, counter=1)
                    db.add(user_counter)
                
                await db.flush()

                new_message = Message(
                    sender_name=message.sender,
                    text=message.text,
                    user_counter=user_counter.counter
                )
                db.add(new_message)
                await db.flush()

                result = await db.execute(
                    select(Message)
                    .order_by(Message.created_at.desc(), Message.id.desc())
                    .limit(10)
                )
                messages = result.scalars().all()

                return [
                    MessageResponse(
                        sender=msg.sender_name,
                        text=msg.text,
                        created_at=msg.created_at.isoformat(),
                        sequence_number=msg.id,
                        user_counter=msg.user_counter
                    ) for msg in messages
                ]
                
        except Exception as e:
            await db.rollback()
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise HTTPException(
                status_code=503,
                detail=f"Database conflict, please retry later: {str(e)}"
            )


    raise HTTPException(
        status_code=503,
        detail="Too many retries, try again later"
    )