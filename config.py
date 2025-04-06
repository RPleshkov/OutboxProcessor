from dataclasses import dataclass, field

from environs import Env


@dataclass
class DatabaseConfig:
    url: str
    naming_convention: dict = field(
        default_factory=lambda: {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    )


@dataclass
class NatsConfig:
    url: str


@dataclass
class Config:
    db: DatabaseConfig
    nats: NatsConfig
    process_delay: int


def load_config(path: str | None = None):
    env = Env()
    env.read_env(path)
    return Config(
        db=DatabaseConfig(url=env("ENV_DB__URL")),
        nats=NatsConfig(url=env("ENV_NATS__URL")),
        process_delay=int(env("PROCESS_DELAY")),
    )


settings = load_config()
