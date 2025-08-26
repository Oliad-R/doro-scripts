"""
"""
import argparse
from tqdm import tqdm
from modules import constants as const
import csv
import os

def main (verbose: bool) -> bool:
    """
    """

    if not os.path.exists(f"{const.OUTPUT_PATH}/final/"):
        os.makedirs(f"{const.OUTPUT_PATH}/final/")
        if verbose:
            tqdm.write(f"Succesfully created path for CSVs: {const.OUTPUT_PATH}/final")

    try:
        with (
            open(f"{const.OUTPUT_PATH}/final/outlines.csv", "w", encoding="utf-8") as outlines_csv,
            open(f"{const.OUTPUT_PATH}/final/assessment_groups.csv", "w", encoding="utf-8") as assessment_groups_csv,
            open(f"{const.OUTPUT_PATH}/final/assessments.csv", "w", encoding="utf-8") as assessments_csv,
            open(f"{const.OUTPUT_PATH}/final/personnels.csv", "w", encoding="utf-8") as personnels_csv,
            open(f"{const.OUTPUT_PATH}/final/sections.csv", "w", encoding="utf-8") as sections_csv,
            open(f"{const.OUTPUT_PATH}/final/types.csv", "w", encoding="utf-8") as types_csv,
        ):
            #CSV Writers
            outlines_writer = csv.writer(outlines_csv, lineterminator="\n")
            assessment_groups_writer = csv.writer(assessment_groups_csv, lineterminator="\n")
            assessments_writer = csv.writer(assessments_csv, lineterminator="\n")
            personnels_writer = csv.writer(personnels_csv, lineterminator="\n")
            sections_writer = csv.writer(sections_csv, lineterminator="\n")
            types_writer = csv.writer(types_csv, lineterminator="\n")

            #Write CSV headers
            outlines_writer.writerow(const.outlines_columns)
            assessment_groups_writer.writerow(const.assessment_groups_columns)
            assessments_writer.writerow(const.assessments_columns)
            personnels_writer.writerow(const.personnels_columns)
            sections_writer.writerow(const.sections_columns)
            types_writer.writerow(const.types_columns)

            for dept in const.DEPARTMENTS:
                if os.path.isfile(f"{const.SCRAPE_OUTPUT_PATH}{dept}/outlines.csv"):
                    try:
                        with (
                            open(f"{const.SCRAPE_OUTPUT_PATH}{dept}/outlines.csv", "r", encoding="utf-8") as dept_outlines_csv,
                            open(f"{const.SCRAPE_OUTPUT_PATH}{dept}/assessment_groups.csv", "r", encoding="utf-8") as dept_assessment_groups_csv,
                            open(f"{const.SCRAPE_OUTPUT_PATH}{dept}/assessments.csv", "r", encoding="utf-8") as dept_assessments_csv,
                            open(f"{const.SCRAPE_OUTPUT_PATH}{dept}/personnels.csv", "r", encoding="utf-8") as dept_personnels_csv,
                            open(f"{const.SCRAPE_OUTPUT_PATH}{dept}/sections.csv", "r", encoding="utf-8") as dept_sections_csv,
                            open(f"{const.SCRAPE_OUTPUT_PATH}{dept}/types.csv", "r", encoding="utf-8") as dept_types_csv,
                        ):
                    
                            dept_outlines_reader = csv.reader(dept_outlines_csv)
                            dept_assessment_groups_reader = csv.reader(dept_assessment_groups_csv)
                            dept_assessments_reader = csv.reader(dept_assessments_csv)
                            dept_personnels_reader = csv.reader(dept_personnels_csv)
                            dept_sections_reader = csv.reader(dept_sections_csv)
                            dept_types_reader = csv.reader(dept_types_csv)

                            for i, row in enumerate(dept_outlines_reader):
                                if i != 0:
                                    outlines_writer.writerow(row)
                           
                            for i, row in enumerate(dept_assessment_groups_reader):
                                if i != 0:
                                    assessment_groups_writer.writerow(row)

                            for i, row in enumerate(dept_assessments_reader):
                                if i != 0:
                                    assessments_writer.writerow(row)

                            for i, row in enumerate(dept_personnels_reader):
                                if i != 0:
                                    personnels_writer.writerow(row)

                            for i, row in enumerate(dept_sections_reader):
                                if i != 0:
                                    sections_writer.writerow(row)

                            for i, row in enumerate(dept_types_reader):
                                if i != 0:
                                    types_writer.writerow(row)

                    except IOError as e:
                        tqdm.write(const.err(str(e)))
                        return False

    except IOError as e:
        tqdm.write(const.err(str(e)))
        return False
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script for updating DB"
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
        tqdm.write("Process failed.")
