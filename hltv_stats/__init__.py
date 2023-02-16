from .parser import *
from .team import *
from .match import *
from .upcoming_matches import *
from loguru import logger
import sys
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO", backtrace=True, diagnose=True)



