# VTTT Notifier

Scrapes the Virginia Tech "Time Table of Classes" for availability of specified CRNs and notifies user(s) via [ntfy.sh](https://ntfy.sh). Ran from the commandline. The "subscription list" is stored in a .CSV file.

**Note**: This is designed exclusively for Virginia Tech's system.

## Requirements
- Python 3.10 or higher
- Required Python libraries:
  - `requests`
  - `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```

## Usage
1. Add subscriptions to the .CSV

2. Run the script:
   ```bash
   python main.py
   ```

<br>

## Notification Setup (ntfy)
To receive notifications, you'll need to have the **[ntfy.sh](https://ntfy.sh)** app on your mobile device:

1. Visit [ntfy.sh](https://ntfy.sh) and download the app.
2. Add a subscription and choose a unique topic name (e.g., `vtttnotifier-yourName`).
3. Add the URL to your CSV

## CSV File Format
The `course_subscriptions.csv` file should contain the following columns:
- `desc`: Description of the subscription (for readability of the CSV)
- `campus`: Campus code (`0` for main campus)
- `term_year`: Term and year
- `crn`: Course Reference Number
- `ntfy_url`: URL for sending notifications via ntfy

**To find `campus` and `term_year`,** open up your browser's developer tools and search for the course you want. Under the network tab, find the POST request and check the payload's values. Reference image below:

![Image of POST request payload](https://i.imgur.com/q6Es8Ua.png)


#### Example CSV:
```csv
desc,campus,term_year,crn,ntfy_url
Intro to Python,0,202509,12345,https://ntfy.sh/vtttnotifier-johndoe
Data Structures,0,202509,67890,https://ntfy.sh/vtttnotifier-janedoe
```

---