from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from bot_service.service import BotService
from dal.osm_broker.broker import OpenMapsBroker
from dal.storage.storage import Storage

DB = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': 5432,
    'username': 'postgres',
    'password': 'example',
    'database': 'mapper',
}

engine = create_engine("postgresql+psycopg2://postgres:example@localhost:5432/mapper")

Session = sessionmaker(bind=engine)

session = Session()

storage = Storage(session)

osm_broker = OpenMapsBroker()

bot_service = BotService(storage, osm_broker, "7169891388:AAHEliCyDkIrdPovFxWuRFy6yVHyJ1YSrn8")

if __name__ == "__main__":
    app = bot_service.initialize_bot()

    app.run_polling()
