"""
Standalone script for parsing outline
"""

from bs4 import BeautifulSoup, Tag
import re

def extract_assessment_section_html(course_content):
    # find h2/h3 that mentions "assessment"
    header = course_content.find(
        lambda t: t.name in ("h2","h3")
        and re.search(r"assessment|évaluation", t.get_text(" ", strip=True), re.I)
    )
    if not header:
        return ""

    # collect siblings until next h1/h2/h3
    parts = []
    for sib in header.next_siblings:
        if isinstance(sib, Tag):
            if sib.name in ("h1","h2","h3"):
                break
            parts.append(str(sib))  # keep raw HTML for Gemini
    return "".join(parts)

def extract_personnel_section_html(course_content):
    # find h2/h3 that mentions Instructional, Instructor, TA, or Team
    header = course_content.find(
        lambda t: t.name in ("h2", "h3")
        and re.search(r"(instructional|instructor|ta|team)", t.get_text(" ", strip=True), re.I)
    )
    if not header:
        return ""

    # collect siblings until next h1/h2/h3
    parts = []
    for sib in header.next_siblings:
        if isinstance(sib, Tag):
            if sib.name in ("h1", "h2", "h3"):
                break
            parts.append(str(sib))  # raw HTML for Gemini
    return "".join(parts)

def main (content: str) -> tuple[bool, dict[str, str]]:
    """
    Parse / extract data from HTML
    """

    soup = BeautifulSoup(content, features="lxml")

    course_data = {}

    if soup.body is not None:
        course_info = soup.body.find(class_="outline-body")

        if course_info:
            course_content = course_info.find(class_="outline-content")

            if course_content:
                desc = (
                    course_content
                    .find(id=re.compile("course_description|apercu_du_cours"))
                    .find_next_sibling()
                    .find(class_="course-descriptions")
                    .find(class_="description")
                    .find(class_="cd-content")
                    .text
                )

                course_data["description"] = desc

                course_data["personnels"] = extract_personnel_section_html(course_content)

                course_data["assessments_table"] = extract_assessment_section_html(course_content)#assessments

    return True, course_data
