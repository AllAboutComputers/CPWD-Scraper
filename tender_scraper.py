import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException

project_path = os.path.dirname(os.path.abspath(__file__))

def clean_text(text):
    """Clean extracted text by replacing currency symbol and stripping whitespace."""
    return text.replace("₹", "Rs.").strip()

# CSV column renaming dictionary
csv_cols = {
    "NIT/RFP NO": "ref_no",
    "Name of Work / Subwork / Packages": "title",
    "Estimated Cost": "tender_value",
    "Bid Submission Closing Date & Time": "bid_submission_end_date",
    "EMD Amount": "emd",
    "Bid Opening Date & Time": "bid_open_date"
}

def setup_driver():
    """Initialize and return a Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--headless")  # Comment to run browser and see live progress
    # options.add_argument("--disable-gpu")  # Usually not needed on Windows
    # options.add_argument("--no-sandbox")   # Needed mainly on Linux Docker containers
    chromedriver_path = os.path.join(project_path, "chromedriver.exe")
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def handle_alert(driver):
    """Handle and accept alert if present on page load."""
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print("Alert detected:", alert.text)
        alert.accept()
        print("Alert accepted.")
    except TimeoutException:
        print("No alert present (timeout). Continuing.")
    except NoAlertPresentException:
        print("No alert present.")

def navigate_to_tenders_page(driver):
    """Navigate to 'New Tenders > All' and set tenders per page to 20."""
    all_link = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "a_TenderswithinOneday3"))
    )
    all_link.click()
    print("Clicked on 'New Tenders > All'")

    # Wait for table to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "awardedDataTable"))
    )
    print("Tender table loaded.")

    # Change dropdown to show 20 tenders per page
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "awardedDataTable_length"))
    )
    time.sleep(5)  # <-- Important sleep, do not remove
    Select(select_element).select_by_visible_text("20")
    print("Dropdown updated to show 20 tenders per page.")

def wait_for_rows(driver, expected_count=20, timeout=20):
    """Wait until expected number of tender rows are loaded or timeout."""
    start_time = time.time()
    rows = []
    while True:
        rows = driver.find_elements(By.CSS_SELECTOR, "#awardedDataTable tbody tr")
        row_count = len(rows)
        print(f"Current row count: {row_count}")
        if row_count >= expected_count:
            print(f"{expected_count} or more rows loaded.")
            break
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {expected_count} rows. Found only {row_count} rows.")
            break
        time.sleep(1)
    return rows

def extract_tenders(rows):
    """Extract tender details from the table rows."""
    tenders = []
    for row in rows[:20]:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 8:
            tender_data = {
                "NIT/RFP NO": clean_text(cols[1].text),
                "Name of Work / Subwork / Packages": clean_text(cols[2].text),
                "Estimated Cost": clean_text(cols[4].text),
                "Bid Submission Closing Date & Time": clean_text(cols[6].text),
                "EMD Amount": clean_text(cols[5].text),
                "Bid Opening Date & Time": clean_text(cols[7].text),
            }
            tenders.append(tender_data)
    return tenders

def save_to_csv(tenders, csv_path):
    """Save extracted tenders to CSV file with renamed columns."""
    renamed_tenders = []
    for tender in tenders:
        renamed_tender = {csv_cols[key]: value for key, value in tender.items() if key in csv_cols}
        renamed_tenders.append(renamed_tender)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_cols.values())
        writer.writeheader()
        writer.writerows(renamed_tenders)
    print(f"Scraping successful. Saved {len(tenders)} tenders to {csv_path}.")

def main():
    driver = setup_driver()
    try:
        url = "https://etender.cpwd.gov.in/"
        driver.get(url)
        handle_alert(driver)
        navigate_to_tenders_page(driver)
        rows = wait_for_rows(driver)
        tenders = extract_tenders(rows)
        if tenders:
            csv_path = os.path.join(project_path, "tenders.csv")
            save_to_csv(tenders, csv_path)
        else:
            print("No tenders found to save.")
    finally:
        driver.quit()
if __name__ == "__main__":
    main()
