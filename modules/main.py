"""
Script for crawling outlines via exposed API Route
"""

import argparse
import os
import csv
import requests
from tqdm import tqdm
from dotenv import load_dotenv

from modules import constants as const
from modules import parse_course

def main (verbose: bool) -> bool:
    """
    Check all .env secrets
    Make API call
    Request each page, pass response to parse_course
    Write extracted data to a CSV
    """

    #Load and check env secrets
    env_loaded = load_dotenv()

    if not env_loaded:
        tqdm.write(const.err("Could not load .env"))
        return False

    endpoint = os.getenv("EXPOSED_ENDPOINT")

    if not endpoint:
        tqdm.write(const.err("Could not find EXPOSED_ENDPOINT in .env"))
        return False

    endpoint += 'ece'

    cookie = os.getenv("COOKIE")

    if not cookie:
        tqdm.write(const.err("Could not find COOKIE in .env"))
        return False

    session = os.getenv("SESSION_COOKIE")

    if not session:
        tqdm.write(const.err("Could not find SESSION_COOKIE in .env"))
        return False

    term = os.getenv("TERM")

    if not term:
        tqdm.write(const.err("Could not find TERM in .env"))
        return False

    base_url = os.getenv("OUTLINE_BASE")

    if not base_url:
        tqdm.write(const.err("Could not find TERM in .env"))
        return False

    #Create output folder if not there
    if not os.path.exists(const.SCRAPE_OUTPUT_PATH):
        os.makedirs(const.SCRAPE_OUTPUT_PATH)
        if verbose:
            tqdm.write(f"Succesfully created path for CSVs: {const.SCRAPE_OUTPUT_PATH}")

    #Request
    if verbose:
        tqdm.write("Requesting API data...")

    courses = requests.get(endpoint, timeout=60, cookies={"csrftoken": cookie}).json()

    if not courses:
        tqdm.write(const.err("No response returned from API"))
        return False

    filtered_data = [course for course in courses if course["term"]==term]

    try:
        with open(const.SCRAPE_OUTPUT_PATH+'outlines.csv', "w", encoding="utf-8") as outlines_csv, open(const.SCRAPE_OUTPUT_PATH+'sections.csv', "w", encoding="utf-8") as sections_csv, open(const.SCRAPE_OUTPUT_PATH+'types.csv', "w", encoding="utf-8") as types_csv:
            outlines_writer = csv.writer(outlines_csv, lineterminator="\n")
            sections_writer = csv.writer(sections_csv, lineterminator="\n")
            types_writer = csv.writer(types_csv, lineterminator="\n")

            outlines_writer.writerow(const.outlines_columns)
            sections_writer.writerow(const.sections_columns)
            types_writer.writerow(const.types_columns)

            for course in filtered_data:
                code = course["courses"]
                name = course["title"]
                url = course["url"]
                types = course["types"]
                sections = course["sections"].split(",")

                if not url:
                    tqdm.write(const.warning(f"No outline url provided for {code}"))
                else:
                    course_page = requests.get(base_url+url, timeout=60, cookies={"csrftoken": cookie, "sessionid": session})

                    if course_page.status_code==404:
                        tqdm.write(const.warning(f"Page not found. 404 Error. {url}"))
                        return False

                    res, data = parse_course.main(course_page.text)

                    if not res:
                        return False

                    outlines_writer.writerow([code, name, data["description"], term])

                    for section in sections:
                        if "-" in section: #101-106
                            start_range = int(section.split("-")[0])
                            end_range = int((section.split("-")[1]))

                            for i in range(start_range, end_range+1):
                                sections_writer.writerow([i, code])
                        else:
                            sections_writer.writerow([section.strip(), code])

                    for type_ in types:
                        types_writer.writerow([type_, code])

                    tqdm.write(f"{code}: {data}")

    except IOError as e:
        tqdm.write(const.err(str(e)))
        return False

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cron job script for updating DB"
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
