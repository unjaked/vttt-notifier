# Try to import required modules
try: 
    import requests, time, random
    import parsing
    from datetime import datetime, timedelta
except ImportError as e:
    print(f"Error: Missing required module: {e.name}")
    print(f"Please install the missing module using pip:")
    print(f"    pip install {e.name}")
    exit(1)

######################## CONFIG #########################

# URL for timetable of classes (default: https://selfservice.banner.vt.edu/ssb/HZSKVTSC.P_ProcRequest)
URL = "https://selfservice.banner.vt.edu/ssb/HZSKVTSC.P_ProcRequest"

# .CSV file containing course subscriptions (default: course_subscriptions.csv)
CSV_FILE = "course_subscriptions.csv"       

# Debug mode. Prints messages to console for monitoring and writes to logging file (default: True)
DEBUG = True   

# Upper/lower limits of seconds to wait before checking for availability again.
# Value is randomly chosen between these two values each loop to prevent rate limiting. (default: 30, 90)
FREQUENCY_SECONDS_LOWER = 30
FREQUENCY_SECONDS_UPPER = 90

#########################################################


def main():

    bad_requests = 0
    notified_users = set() # For storing already-notified users
    last_reset_time = datetime.now()

    while True:
        debug_print(f"\n\n[{get_current_time()}] Checking for course availibility...", end=" ")

        # Reset notified_users set every 10 minutes
        if datetime.now() - last_reset_time >= timedelta(minutes=10):
            notified_users.clear()
            last_reset_time = datetime.now()
            debug_print(f"\n[{get_current_time()}] Resetting `notified_users` set...", end=" ")

        try: 
            # Check course availibility for each line in subscription csv
            course_subscriptions = parsing.read_subscriptions_csv(CSV_FILE)
            for course in course_subscriptions:

                desc = course["desc"]
                campus = course["campus"]
                term_year = course["term_year"]
                crn = course["crn"]
                ntfy_url = course["ntfy_url"]

                header = {'User-Agent': 'Mozilla/5.0 (compatible; VTTT-SCPR/v0.1)'}

                payload = {
                    "CAMPUS": campus,
                    "TERMYEAR": term_year,
                    "CORE_CODE": "AR%",
                    "subj_code": "%",
                    "SCHDTYPE": "%",
                    "CRSE_NUMBER": "",
                    "crn": crn,
                    "open_only": "on", # "on" for display only open sectons. "" for all sections.
                    "disp_comments_in": "Y",
                    "sess_code": "%",
                    "BTN_PRESSED": "FIND class sections",
                    "inst_name": ""   ,
                }

                # Send POST, retry if not successful
                response = requests.post(URL, data=payload,headers=header)
                if response.status_code != 200: 
                    bad_requests += 1
                    status_code = response.status_code
                    debug_print(f"\n[{get_current_time()}] Error: Response returned status code of {status_code}.",end=" ",)
                    time.sleep(30 * bad_requests)
                    if bad_requests > 30:  # max 15 minute sleep
                        bad_requests = 1
                    continue

                bad_requests = 0
                availability = parsing.parse_course_availability(response, crn)

                # If availability found, send notification unless already recently sent
                if availability == "open found":
                    debug_print(f"\n[{get_current_time()}] {desc:<20} {crn:<8} {"Availibility found ***"}", end=" ")

                    if (crn, desc) in notified_users:
                        debug_print("(User already notified)", end=" ")
                        continue

                    else:
                        try:
                            notifier(ntfy_url, crn)
                            notified_users.add((crn, desc)) # add to already-notified list
                            debug_print("(Notification sent)", end=" ")

                        except Exception as e:
                            debug_print(f"(Error sending notification: {e})", end=" ")

                # If no availability found or error encountered
                if availability == "no open":
                    debug_print(f"\n[{get_current_time()}] {desc:<20} {crn:<8} {"No availibility found."}", end=" "); 
                if availability == "timetable error":
                    debug_print(f"\n[{get_current_time()}] {desc:<20} {crn:<8} {"Error from timetable. Likely bad payload."}", end=" ")
                if availability == "invalid crn":
                    debug_print(f"\n[{get_current_time()}] {desc:<20} {crn:<8} {"CRN not found in timetable."}", end=" ")
                if availability == "unknown":
                    debug_print(f"\n[{get_current_time()}] {desc:<20} {crn:<8} {"Unknown error occurred"}", end=" ")

        except Exception as e:
            debug_print(f"\n[{get_current_time()}] Unknown error occurred: {e}", end=" ")

        # Sleep before looping
        sleep_time = random.uniform(FREQUENCY_SECONDS_LOWER, FREQUENCY_SECONDS_UPPER)
        debug_print(f"\n[{get_current_time()}] Sleeping for {sleep_time:.2f} seconds...", end=" ")
        time.sleep(sleep_time)


def notifier(ntfy_url, crn):
    """
    Sends notifications to the user via ntfy
    """
    requests.post(ntfy_url, data=f"COURSE OPENING FOR CRN: {crn}".encode(encoding='utf-8'))


def get_current_time():
    """
    Returns the current time in HH:MM:SS format
    """
    return datetime.now().strftime("%H:%M:%S")


def debug_print(message, end):
    """
    Prints debug messages to the console only if the `DEBUG` variable in config is set to True.
    """
    if DEBUG:
        # Print message
        print(f"{message}", end=end)

        # Write (append) messages to log file
        with open("debug_output.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"{message}{end}")


if __name__ == "__main__":
    main()
