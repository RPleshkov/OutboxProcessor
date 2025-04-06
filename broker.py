import logging
from uuid import UUID

import nats
from nats.aio.client import Client

from config import settings

logger = logging.getLogger(__name__)


async def connect_to_nats(server: str = settings.nats.url) -> Client:
    nc: Client = await nats.connect(server)
    return nc


async def publish_to_nats(
    rows: list[tuple[UUID, dict[str, str]]],
) -> tuple[set[UUID], set[UUID]]:
    published: set[UUID] = set()
    failed: set[UUID] = set()
    nc = None

    try:
        nc = await connect_to_nats()
        for key, message in rows:
            try:
                await nc.publish(
                    subject="email.send",
                    payload=message["to_email"].encode("utf-8"),
                    headers={"Nats-Msg-Id": message["message_id"]},
                )
                published.add(key)
                logger.info(f"Published message to {message['to_email']}")
            except Exception as e:
                failed.add(key)
                logger.warning(
                    f"Failed to publish message {key} to {message['to_email']}: {e}"
                )
    except Exception as e:
        logger.error(f"Could not connect to NATS: {e}")
        failed.update([key for key, _ in rows])
    finally:
        if nc and not nc.is_closed:
            await nc.drain()

    return published, failed
