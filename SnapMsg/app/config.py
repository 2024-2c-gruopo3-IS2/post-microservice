import os
import logging



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
    