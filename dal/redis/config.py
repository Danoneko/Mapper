import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class RedisConfiguration:
    host: str
    port: int
    database: int
    password_env_name: str

    password: str = ""

    def __post_init__(self):
        load_dotenv()

        self.password = os.environ.get(self.password_env_name)
