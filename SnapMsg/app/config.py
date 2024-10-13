import os
import logging
from datadog import initialize
from ddtrace import patch

options = {
    'api_key': os.getenv('DD_API_KEY'),
    'app_key': os.getenv('DD_APP_KEY'),
}
initialize(**options)

patch(logging=True)

log_file_path = "logs/snapmsg.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),  
        logging.StreamHandler(),            
    ]
)

logger = logging.getLogger(__name__)

logger.info("Application logging initialized and connected to Datadog.")
