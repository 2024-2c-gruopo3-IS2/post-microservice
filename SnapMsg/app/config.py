import os
import logging
from dotenv import load_dotenv



log_file_path = "logs/snapmsg.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)


logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", 
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    load_dotenv()
else:
    load_dotenv(dotenv_path=".env.testing")
    