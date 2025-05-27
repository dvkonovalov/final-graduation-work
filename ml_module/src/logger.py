import logging

logging.basicConfig(filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('pymongo').setLevel(logging.INFO)
logging.info("Running Urban Planning")
logger = logging.getLogger('urbanGUI')