import asyncio
import logging

from broker import publish_to_nats
from db_helper import get_pending_or_failed_outbox_rows, update_outbox_statuses
from config import settings

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.WARNING,
    format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
    "%(lineno)d - %(name)s - %(message)s",
)


async def main():
    logger.info("Start worker")
    while True:
        try:
            rows = get_pending_or_failed_outbox_rows()

            if not rows:
                logger.info("No outbox messages to process")

            else:
                published, failed = await publish_to_nats(rows)
                update_outbox_statuses(
                    published=published,
                    failed=failed,
                )
                logger.info(
                    f"Processed outbox: sent={len(published)}, failed={len(failed)}"
                )

        except Exception as e:
            logger.exception(f"Unexpected error in worker loop: {e}")

        await asyncio.sleep(settings.outbox_poll_interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stop worker")
