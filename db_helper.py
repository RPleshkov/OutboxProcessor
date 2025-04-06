from contextlib import contextmanager
from typing import Generator, Sequence
from uuid import UUID

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session, sessionmaker

from config import settings
from models.outbox import Outbox, Status

engine = create_engine(settings.db.url)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def get_pending_or_failed_outbox_rows() -> list[tuple[UUID, dict[str, str]]]:
    stmt = select(Outbox.id, Outbox.payload).where(
        Outbox.status.in_([Status.pending, Status.failed])
    )
    with get_db_session() as session:
        result = session.execute(stmt)
        return list(result.tuples().all())


def update_outbox_statuses(published: set[UUID], failed: set[UUID]) -> None:
    if not published and not failed:
        return

    with get_db_session() as session:
        if published:
            stmt = (
                update(Outbox)
                .where(Outbox.id.in_(published))
                .values(status=Status.sent)
            )
            session.execute(stmt)

        if failed:
            stmt = (
                update(Outbox).where(Outbox.id.in_(failed)).values(status=Status.failed)
            )
            session.execute(stmt)

        session.commit()
