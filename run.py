from app import app
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('log.log')
formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("Started logging")

app.run(host='0.0.0.0', port=5000, debug=True)
