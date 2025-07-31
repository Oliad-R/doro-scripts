"""
Constants for other modules
"""

import csv
from typing import final
from enum import Enum
from tqdm import tqdm

OUTPUT_PATH = "./output/"
INPUT_PATH = "./input/"

SCRAPE_OUTPUT_PATH = OUTPUT_PATH + 'scrape/'

PERSONNEL_PATH = OUTPUT_PATH + 'personnel_rows.csv'
CONDITIONS_PATH = OUTPUT_PATH + 'conditions_rows.csv'
ASSESSMENTS_PATH = OUTPUT_PATH + 'assessments_rows.csv'
ASSESSMENT_GROUPS_PATH = OUTPUT_PATH + 'assessment_groups_rows.csv'

class OutlinesCols(Enum):
    """
    outlines table columns
    """
    COURSE_CODE = 0
    PERSONNEL = 1
    SCHEMES = 2
    ID = 3
    COURSE_NAME = 4
    COURSE_DESCRIPTION = 5

personnel_columns = ["course_id", "name", "role", "email"]
assessment_groups_columns = ["id", "course_id", "weight", "count", "drop", "name", "type", "optional"]
assessments_columns = ["group_id", "weight", "index"]
conditions_columns = ["course_id", "group_id", "scheme", "lower", "upper"]
outlines_columns = ["code", "name", "description", "term"]
sections_columns = ["section", "code"]
types_columns = ["type", "code"]

invalid_emails = ["a6lian@uwaterloo.ca"]

DEPARTMENTS = [
    "AE", "BME", "CHE", "CIVE", "ECE", "ME", "MSCI", "MSE", "MTE", "NE", "SE", "SYDE",
    "AMATH", "ACTSC", "CO", "CS", "MATH", "STAT",
    "ASTRN", "BIOL", "CHEM", "EARTH", "OPTOM", "PHYS", "SCBUS", "SCI",
    "HEALTH", "HLTH", "KIN", "PHS", "REC",
    "ERS", "GEOG", "INTEG", "PLAN",
    "AFM", "APPLS", "ANTH", "BLKST", "CLAS", "COMMST", "EASIA", "ECON", "EMLS", "ENGL", "FINE", "FR", "GER", "GBDA", "GSJ", "GGOV", "HIST", "ISS", "ITAL", "ITALST", "JS", "LS", "MEDVL", "MUSIC", "PACS", "PHIL", "PSCI", "PSYCH", "RS", "SDS", "SMF", "SOC", "SOCWK", "SWK", "SWREN", "SPAN", "TS",
    "BET", "PD", "SAF", "ARCH", "DAC", "ENBUS", "SFM"
]

@final
class Colors:
    """
    ASCII characters for printing terminal colours
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def err(message: str) -> str:
    """
    Returns red error terminal text
    """
    return f"{Colors.FAIL}ERR: {message}{Colors.ENDC}"

def warning(message: str) -> str:
    """
    Returns yellow warning terminal text
    """
    return f"{Colors.WARNING}WARNING: {message} {Colors.ENDC}"

def success(message: str) -> str:
    """
    Returns green success terminal text
    """
    return f"{Colors.OKGREEN}SUCCESS: {message} {Colors.ENDC}"


def count_rows(filename: str) -> tuple[bool, int | None]:
    """
    Generic function to count the number of rows in a CSV
    """
    num_rows = 0

    try:
        with open(INPUT_PATH+filename, "r", encoding="utf-8") as generic_csv:
            counter_reader = csv.reader(generic_csv, lineterminator="\n")

            for _ in counter_reader:
                num_rows += 1

    except IOError as e:
        tqdm.write(err(str(e)))
        return False, None

    return True, num_rows
