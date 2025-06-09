CPWD Tender Scraper

This script opens the CPWD eTendering website, navigates to the "New Tenders > All" page, extracts the first 20 tenders, and saves them into a file named 'tenders.csv'.

✅ How to Run

1. Install Dependencies

Ensure Python 3 is installed. Then, run:

pip install -r requirements.txt


2. ChromeDriver Note

The script includes `chromedriver.exe` in the folder. It is configured to run in headless mode by default (i.e., without opening a visible browser window).

- If you face issues related to driver compatibility, please:
  - Update your Chrome browser to the latest version.
  - OR Download the correct ChromeDriver version matching your browser from: https://chromedriver.chromium.org/downloads
  - Replace the existing `chromedriver.exe` with the correct one in the same folder.

3. Run the Script

From the terminal or command prompt or any IDE:

python tender_scraper.py


This will extract the first 20 tenders and generate a `tenders.csv` file in the same directory.

---

🖥️ Want to See the Browser in Action?

By default, the script runs in headless mode. To enable visible Chrome window:

1. Open tender_scraper.py

2. Find this line:
options.add_argument("--headless")

3.Comment it out:

# options.add_argument("--headless")


Then rerun the script to observe browser actions.

---

📁 Output

The output file 'tenders.csv' will include the following columns:
- ref_no
- title
- tender_value
- bid_submission_end_date
- emd
- bid_open_date