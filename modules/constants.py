"""
Constants for other modules
"""

import os
import csv
from typing import final
from enum import Enum
from tqdm import tqdm
from uuid import uuid4
from copy import deepcopy

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

personnels_columns = ["course_id", "name", "role", "email"]
assessment_groups_columns = ["id", "course_id", "weight", "count", "drop", "name", "type", "optional"]
assessments_columns = ["id", "group_id", "weight", "index", "due_date", "name"]
conditions_columns = ["course_id", "group_id", "scheme", "lower", "upper"]
outlines_columns = ["id", "code", "name", "description", "term", "url"]
sections_columns = ["section", "course_id"]
types_columns = ["type", "course_id"]

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

def prompt(section_html: str):
    return f"""
    You are a strict parser.

    Rules:
    - Output only JSON, no prose.
    - Use absolute weights as decimals (e.g., 0.5 for 50%).
    - Create assessment GROUPS (e.g., "Quizzes") and ITEMS inside each group.
    - If a group has a total like "Quiz [50%]" and items like "[25%]":
      - Treat item percents as RELATIVE to the group total unless the page clearly states they are course-level.
      - So four items each "[25%]" under "Quiz [50%]" → each item weight is 0.5 * 0.25 = 0.125.
    - Numbering may be wrong or skipped (e.g., "Quiz5"). Do NOT assume missing numbers imply missing items.
      - Set item indexes sequentially by appearance starting at 0 (0,1,2,3...), ignoring the label’s number.
    - Set group.count to the number of items you produced for that group.
    - group.drop: parse if present (e.g., "lowest two dropped"); otherwise 0.
    - If both undergraduate and graduate variants exist, prefer undergraduate unless the item is marked graduate-only (then optional=true).
    - Ensure the sum of item weights equals the group weight (±0.5%). If item weights aren’t provided, split group weight evenly.
    - If dates are not directly parseable into a YYYY-MM-DD HH:mm:ss datetime format then use null, also year is always 2025

    Example (edge case):
    HTML snippet:
      Quiz [50%]
      Quiz1: [25%] Topic A
      Quiz2: [25%] Topic B
      Quiz3: [25%] Topic C
      Quiz5: [25%] Topic D

    Expectation:
    - 1 group "Quizzes" with weight 0.5 and count 4.
    - 4 items with indexes 0..3 and weights 0.125 each, in the order they appear.

    HTML to parse:
    {section_html}
    """

def personnels_prompt(section_html: str):
    return f"""
    You are a strict parser.

    Rules:
    - Output only JSON, no prose.
    - Role's should only be Professor or TA. No variance, if it doesn't fit then skip it.
    - Courses can have no personnel, just return nothing

    HTML to parse:
    {section_html}
    """


def assign_ids(parsed_output):
    parsed = deepcopy(parsed_output)

    # map placeholder group_id -> real UUID
    group_id_map = {}

    for group in parsed.assessment_groups:
        real_id = str(uuid4())
        group_id_map[group.id] = real_id
        group.id = real_id

    # assign UUIDs to assessments and remap group_id
    for idx, assessment in enumerate(parsed.assessments):
        assessment.id = str(uuid4())
        assessment.group_id = group_id_map.get(assessment.group_id, assessment.group_id)

    return parsed

def open_csv_with_header(path: str, columns: list[str]):
    file_exists = os.path.isfile(path)
    csv_file = open(path, "a", encoding="utf-8", newline="")
    writer = csv.writer(csv_file, lineterminator="\n")
    if not file_exists or os.stat(path).st_size == 0:
        writer.writerow(columns)
    return csv_file, writer
