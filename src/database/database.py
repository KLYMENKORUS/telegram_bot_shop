from sqlalchemy.ext.asyncio import create_async_engine, \
    async_sessionmaker, AsyncSession
from src.config import DATABASE_URL


# create async engine
engine = create_async_engine(DATABASE_URL, future=True, echo=True)

# create session
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)
