"""
Script for parsing outlines table into multiple tables
"""

import argparse
import csv
import json
import os
import uuid
import re

from tqdm import tqdm
from modules import constants

def main (verbose: bool) -> bool:
    """
    Process outline table CSV
    Main objective is to split the "outlines" array columns like personnel and schemes, into their own tables
    """

    if not os.path.exists(constants.OUTPUT_PATH):
        os.makedirs(constants.OUTPUT_PATH)
        if verbose:
            tqdm.write(f"Succesfully created path for CSVs: {constants.OUTPUT_PATH}")

    result, num_rows = constants.count_rows('outlines_rows.csv')

    if not result:
        return False

    try:
        with open(constants.INPUT_PATH+'outlines_rows.csv', "r", encoding="utf-8") as outlines_csv, open(constants.PERSONNEL_PATH, "w", encoding="utf-8") as personnel_csv, open(constants.CONDITIONS_PATH, "w", encoding="utf-8") as conditions_csv, open(constants.ASSESSMENTS_PATH, "w", encoding="utf-8") as assessments_csv, open(constants.ASSESSMENT_GROUPS_PATH, "w", encoding="utf-8") as assessment_group_csv:
            outlines_reader = csv.reader(outlines_csv, lineterminator="\n")
            personnel_writer = csv.writer(personnel_csv, lineterminator="\n")
            conditions_writer = csv.writer(conditions_csv, lineterminator="\n")
            assessments_writer = csv.writer(assessments_csv, lineterminator="\n")
            assessment_groups_writer = csv.writer(assessment_group_csv, lineterminator="\n")

            for i, outline in tqdm(enumerate(outlines_reader), total=num_rows):
                if i == 0:
                    personnel_writer.writerow(constants.personnel_columns)
                    conditions_writer.writerow(constants.conditions_columns)
                    assessments_writer.writerow(constants.assessments_columns)
                    assessment_groups_writer.writerow(constants.assessment_groups_columns)
                    continue

                course_id = outline[constants.OutlinesCols.ID.value]
                personnel = json.loads(outline[constants.OutlinesCols.PERSONNEL.value])
                schemes = json.loads(outline[constants.OutlinesCols.SCHEMES.value])

                #personnels table
                for person in personnel:
                    role = person.get("role").capitalize()
                    email = person.get("email")
                    if role=="Ta":
                        role = role.upper()

                    if email in constants.invalid_emails:
                        email = ""

                    personnel_writer.writerow([course_id, person.get("name"), role, email])

                #assessments & conditions table
                for scheme in schemes:
                    condition = scheme.get("condition")
                    condition_assessment = condition.get("symbol")
                    condition_assessment_id = None
                    scheme_num: int = scheme.get("schemeNum")
                    assessments = scheme.get("assessments")

                    for assessment_group in assessments:
                        assessment_group_id = uuid.uuid4()

                        weight = assessment_group.get("weight").lower()

                        if weight=="ungraded":
                            weight = 0
                        else:
                            cleaned_weight = re.sub(r'[^0-9\.\-\%]', '', weight)
                            if cleaned_weight.endswith("%"):
                                numbers = [float(n) for n in re.findall(r'(\d+(?:\.\d+)?)%', weight)]
                                if not numbers:
                                    weight = 0
                                else:
                                    max_percent = max(numbers)

                                    if str(weight).startswith("a*"):
                                        weight = float(weight[2:-1])/50
                                    else:
                                        weight = max_percent/100
                            else:
                                try:
                                    weight = float(cleaned_weight)
                                except ValueError:
                                    weight = 0

                        count = assessment_group.get("count")

                        if not count:
                            count = 1
                        else:
                            count = int(count)

                        drop = assessment_group.get("drop")

                        if not drop:
                            drop = 0
                        else:
                            drop = int(drop)

                        name = str(assessment_group.get("name"))
                        a_type = str(assessment_group.get("assessmentType"))

                        optional = False

                        if "optional" in name.lower() or "optional" in a_type.lower():
                            optional = True

                        assessment_groups_writer.writerow([assessment_group_id, course_id, weight, count, drop, name, a_type, optional])

                        individual_weight = weight/count

                        if assessment_group.get("symbol")==condition_assessment:
                            condition_assessment_id = assessment_group_id

                        for i in range(count):
                            assessments_writer.writerow([assessment_group_id, individual_weight, i if count > 0 else ""])

                    conditions_writer.writerow([course_id, condition_assessment_id, scheme_num, condition.get("lowerBound"), condition.get("upperBound")])

                    tqdm.write(str(assessments))

    except IOError as e:
        tqdm.write(constants.err(str(e)))
        return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Standalone script for parsing outlines table"
    )

    _ = parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Make output more verbose with logging"
    )

    args: argparse.Namespace = parser.parse_args()

    if main(args.verbose):
        tqdm.write("Process completed successfully.")
    else:
        tqdm.write("Process failed. Check logs for more info.")
