"""
Script for crawling outlines via exposed API Route
"""

import argparse
import os
import csv
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from uuid import uuid4
from google import genai 
import json

from modules import constants as const
from modules import parse_course
from modules import models

def main (verbose: bool, query: str) -> bool:
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

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        tqdm.write(const.err("Could not find GEMINI_API_KEY in .env"))
        return False

    #Create output folder if not there
    if not os.path.exists(f"{const.SCRAPE_OUTPUT_PATH}/{query}/"):
        os.makedirs(f"{const.SCRAPE_OUTPUT_PATH}/{query}/")
        if verbose:
            tqdm.write(f"Succesfully created path for CSVs: {const.SCRAPE_OUTPUT_PATH}/{query}")

    #Request
    if verbose:
        tqdm.write("Requesting API data...")

    courses = requests.get(endpoint+query, timeout=60, cookies={"csrftoken": cookie}).json()

    if not courses:
        tqdm.write(const.err("No response returned from API"))
        return False
    
    covered_courses = []

    if os.path.isfile(f'{const.SCRAPE_OUTPUT_PATH}/{query}/outlines.csv'):
        try:
            with open(f'{const.SCRAPE_OUTPUT_PATH}/{query}/outlines.csv', "r", encoding="utf-8") as outlines_csv:
                outlines_reader = csv.reader(outlines_csv)
                for i, row in enumerate(outlines_reader):
                    if i != 0:
                        tqdm.write(str(row[1]))
                        covered_courses.append(row[1])

        except IOError as e:
            tqdm.write(const.err(str(e)))
            return False

    filtered_data = [course for course in courses if course["term"]==term and course["courses"].startswith(f"{query} ") and course["courses"] not in covered_courses]

    try:
        with (
            const.open_csv_with_header(f'{const.SCRAPE_OUTPUT_PATH}/{query}/outlines.csv', const.outlines_columns)[0] as outlines_csv,
            const.open_csv_with_header(f'{const.SCRAPE_OUTPUT_PATH}/{query}/sections.csv', const.sections_columns)[0] as sections_csv,
            const.open_csv_with_header(f'{const.SCRAPE_OUTPUT_PATH}/{query}/types.csv', const.types_columns)[0] as types_csv,
            const.open_csv_with_header(f'{const.SCRAPE_OUTPUT_PATH}/{query}/assessment_groups.csv', const.assessment_groups_columns)[0] as assessment_groups_csv,
            const.open_csv_with_header(f'{const.SCRAPE_OUTPUT_PATH}/{query}/assessments.csv', const.assessments_columns)[0] as assessments_csv,
            const.open_csv_with_header(f'{const.SCRAPE_OUTPUT_PATH}/{query}/personnels.csv', const.personnels_columns)[0] as personnels_csv,
        ):
            outlines_writer = csv.writer(outlines_csv, lineterminator="\n")
            sections_writer = csv.writer(sections_csv, lineterminator="\n")
            types_writer = csv.writer(types_csv, lineterminator="\n")
            assessment_groups_writer = csv.writer(assessment_groups_csv, lineterminator="\n")
            assessments_writer = csv.writer(assessments_csv, lineterminator="\n")
            personnels_writer = csv.writer(personnels_csv, lineterminator="\n")

            for i, course in tqdm(enumerate(filtered_data), total=len(filtered_data)):
                course_id = uuid4()
                code = course["courses"]
                name = course["title"]
                url = course["url"]
                types = course["types"]
                sections = course["sections"].split(",")

                tqdm.write(f"Parsing {code}...")

                if not url:
                    tqdm.write(const.warning(f"No outline url provided for {code}"))
                else:
                    course_page = requests.get(base_url+url, timeout=60, cookies={"csrftoken": cookie, "sessionid": session})

                    tqdm.write(f"Page Status: {course_page.status_code}")

                    if course_page.status_code==404:
                        tqdm.write(const.warning(f"Page not found. 404 Error. {url}"))
                        return False

                    res, data = parse_course.main(course_page.text)

                    if not res:
                        return False

                    personnels_html = str(data["personnels"])

                    if personnels_html:
                        client = genai.Client(api_key=api_key)

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=const.personnels_prompt(personnels_html),
                            config={
                                "response_mime_type": "application/json",
                                "response_schema": models.ParsedPersonnelsOutput,
                            }
                        )
                        
                        for person in response.parsed.personnels:
                            p = person.model_dump()
                            personnels_writer.writerow([
                                course_id,
                                p["name"],
                                p["role"],
                                p["email"]
                            ])
                    
                    table_html = str(data["assessments_table"])
                    
                    if table_html:
                        client = genai.Client(api_key=api_key)

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=const.prompt(table_html),
                            config={
                                "response_mime_type": "application/json",
                                "response_schema": models.ParsedAssessmentOutput,
                            }
                        )

                        # Now assign real UUIDs
                        parsed = const.assign_ids(response.parsed)

                        tqdm.write(f"RES {str(parsed.model_dump_json(indent=2))}")

                        # Write assessment groups
                        for group in parsed.assessment_groups:
                            g = group.model_dump()
                            assessment_groups_writer.writerow([
                                g["id"],
                                course_id,
                                g["weight"],
                                g["count"],
                                g["drop"],
                                g["name"],
                                g.get("type"),     # might be None if not present
                                g.get("optional", False),
                            ])

                        # Write assessments
                        for assessment in parsed.assessments:
                            a = assessment.model_dump()
                            assessments_writer.writerow([
                                a["id"],
                                a["group_id"],
                                a["weight"],
                                a["index"],
                                a["due_date"],
                                a["name"],
                            ])

                    outlines_writer.writerow([course_id, code, name, data["description"], term, url])

                    for section in sections:
                        if "-" in section: #101-106
                            start_range = int(section.split("-")[0])
                            end_range = int((section.split("-")[1]))

                            for i in range(start_range, end_range+1):
                                sections_writer.writerow([i, course_id])
                        else:
                            sections_writer.writerow([section.strip(), course_id])

                    for type_ in types:
                        types_writer.writerow([type_, course_id])


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
    
    for dept in const.DEPARTMENTS:
        if main(args.verbose, dept):
            tqdm.write(f"Process completed successfully for {dept}.")
        else:
            tqdm.write(f"Process failed for {dept}.")
