from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from sqlalchemy.exc import NoResultFound
from typing import Optional
from models import Message, UserMessage
from datetime import timedelta
import asyncio
import os

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine and session maker for the async database connections
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)




class DatabaseOperations:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = AsyncSessionLocal
    
    async def add_message(self, message_hash, status):
        async with self.SessionLocal() as session:
            async with session.begin():
                message = Message(message_hash=message_hash, status=status)
                session.add(message)
    
    async def update_message_status(self, message_hash, new_status):
        async with self.SessionLocal() as session:
            async with session.begin():
                stmt = update(Message).where(Message.message_hash == message_hash).values(
                    status=new_status)
                await session.execute(stmt)
    
    async def delete_old_safe_messages(self, minutes):
        async with self.SessionLocal() as session:
            async with session.begin():
                stmt = delete(Message).where(
                    Message.status == 'safe',
                    Message.last_updated_at < func.now() - timedelta(minutes=minutes)
                )
                await session.execute(stmt)

    async def increment_safe_message_amount(self, message_hash):
        async with self.SessionLocal() as session:
            async with session.begin():
                stmt = update(Message).where(Message.message_hash == message_hash, Message.status == 'safe').values(
                    amount=Message.amount + 1)
                await session.execute(stmt)

    async def get_message(self, message_hash):
        async with self.SessionLocal() as session:
            result = await session.execute(select(Message).where(Message.message_hash == message_hash))
            return result.scalars().first()
    
    async def add_user_message(self, user_id, local_id, message_hash):
        async with self.SessionLocal() as session:
            async with session.begin():
                message = await self.get_message(message_hash)
                if not message:
                    raise NoResultFound(f"Message with hash {message_hash} not found")
                
                user_message = UserMessage(user_id=user_id, local_id=local_id, message_id=message.id)
                session.add(user_message)
    
    async def check_and_update_message_status(self, threshold):
        async with self.SessionLocal() as session:
            async with session.begin():
                result = await session.execute(
                    select(Message).where(Message.status == 'safe', Message.amount > threshold)
                )
                messages = result.scalars().all()
                
                for message in messages:
                    stmt = update(Message).where(Message.id == message.id).values(status='dangerous')
                    await session.execute(stmt)


async def background_task(database_operations, threshold, interval):
    while True:
        await database_operations.check_and_update_message_status(threshold)
        await asyncio.sleep(interval)