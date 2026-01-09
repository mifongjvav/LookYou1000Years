import logging
import coloredlogs
from MenuLite.Main import ml_main_menu, ml_input

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO", fmt="%(asctime)s - %(funcName)s: %(message)s")

ml_main_menu()
ml_input()
