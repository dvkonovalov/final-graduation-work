import logging

logging.basicConfig(filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logging.getLogger('pymongo').setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("filelock").setLevel(logging.INFO)
logging.getLogger("numba.core").setLevel(logging.INFO)
logging.info("Running Urban Planning")
logger = logging.getLogger('urbanGUI')