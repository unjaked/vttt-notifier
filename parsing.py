try: 
    from bs4 import BeautifulSoup
    import csv
except ImportError as e:
    print(f"Error: Missing required module: {e.name}")
    print("Please install the missing module using pip:")
    print(f"    pip install {e.name}")
    exit(1)

def parse_course_availability(response, crn):
    """
    Parses the response HTML to check for course availability based on CRN.
    """
    html_parser = BeautifulSoup(response.text, 'html.parser')

    # No table means CRN wasn't found in timetable. (Full CRNs will have at least a header row)
    if html_parser.find("table", class_="dataentrytable") is None:
        return "invalid crn"

    # Check for error message from invalid POST request
    error_messages = html_parser.find_all("b", class_="red_msg")
    for message in error_messages:
        if message.text.strip() == "Information for this CAMPUS is not currently available for the TERM selected.":
            return "timetable error"

    # Check for no open sections
    no_sec_found = html_parser.find_all("li", class_="red_msg")
    for message in no_sec_found:
        if message.text.strip() == "NO SECTIONS FOUND FOR THIS INQUIRY.":
            return "no open"

    ## Code could end here theoretically as the only outcome is an availability was found,
    ## but still looks for an exact CRN match in the response

    # Store the (HTML) table that contains course info
    course_table = html_parser.find("table", class_="dataentrytable") 

    # Parse through the course table and look for matching CRN
    rows = course_table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        for cell in cells:
            if cell.text.strip() == crn:
                return "open found"

    return "unknown"


def read_subscriptions_csv(filename):
    """
    Reads the .CSV file containing all course "subscriptions" into a list.
    """
    course_subscriptions = []

    try:
        with open(filename, mode="r") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:

                # Validate required fields
                required_fields = ["desc", "campus", "term_year", "crn", "ntfy_url"]
                if not all(field in row and row[field].strip() for field in required_fields):
                    print(f"[Warning]: Invalid row, skipping: {row}")
                    continue

                course_subscriptions.append(
                    {
                        "desc": row["desc"].strip(),
                        "campus": row["campus"].strip(),
                        "term_year": row["term_year"].strip(),
                        "crn": row["crn"].strip(),
                        "ntfy_url": row["ntfy_url"].strip(),
                    }
                )
    except FileNotFoundError:
        print(f"Error: CSV file '{filename}' not found.")
        return []
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
        return []

    return course_subscriptions
