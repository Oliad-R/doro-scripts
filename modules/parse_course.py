"""
Standalone script for parsing outline
"""

from bs4 import BeautifulSoup

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
                    .find(id="course_description")
                    .find_next_sibling()
                    .find(class_="course-descriptions")
                    .find(class_="description")
                    .find(class_="cd-content")
                    .text
                )

                course_data["description"] = desc

    return True, course_data
