import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- CONFIGURATION ---
TARGET_URL = "http://127.0.0.1:9000/products-page"
OUTPUT_DIR = os.path.join("data", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- MOCK SERVER CONTEXT ---
# This simulates a live, uncleaned web page locally so your code runs flawlessly out-of-the-box
class MockWebPageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/products-page":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Raw HTML string with typical real-world data issues: empty fields, duplicates, and literal "None" text strings.
            mock_html = """
            <html>
                <body>
                    <h1>Target Data Source</h1>
                    <table id="products-table">
                        <tr><th>Product ID</th><th>Item Name</th><th>Price</th><th>Availability</th></tr>
                        <tr><td>101</td><td>Premium Mechanical Keyboard</td><td>$120.00</td><td>In Stock</td></tr>
                        <tr><td>102</td><td>Ergonomic Wireless Mouse</td><td>$45.50</td><td>In Stock</td></tr>
                        <tr><td>103</td><td>UltraWide 4K Monitor</td><td>   </td><td>Low Stock</td></tr>
                        <tr><td>101</td><td>Premium Mechanical Keyboard</td><td>$120.00</td><td>In Stock</td></tr>
                        <tr><td>104</td><td>USB-C Hub Adapter</td><td>$25.00</td><td>None</td></tr>
                        <tr><td>105</td><td>Noise Cancelling Headphones</td><td>$199.99</td><td>In Stock</td></tr>
                    </table>
                </body>
            </html>
            """
            self.wfile.write(bytes(mock_html, "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_mock_server():
    server = HTTPServer(("127.0.0.1", 9000), MockWebPageHandler)
    server.serve_forever()


# --- CORE PIPELINE MODULES ---

def extract_raw_web_data(url: str) -> str:
    """EXTRACT Step: Programmatically fetches raw data while spoofing headers to look like a real browser."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    print(f"[1/3] Extracting raw HTML from target page: {url}...")
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        raise RuntimeError(f"Extraction failed with HTTP status: {response.status_code}")
        
    return response.text


def parse_and_clean_data(html_content: str) -> pd.DataFrame:
    """TRANSFORM Step: Parses HTML with BeautifulSoup and runs clean-up operations using Pandas."""
    print("[2/3] Parsing unstructured table data and running automated cleaning protocols...")
    
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", {"id": "products-table"})
    
    if not table:
        raise ValueError("Target unstructured data table could not be isolated.")
        
    # Isolate column names
    headers = [th.text.strip() for th in table.find_all("th")]
    
    # Process unstructured table rows
    rows = []
    for tr in table.find_all("tr")[1:]:  # Skip headers
        cells = [td.text.strip() for td in tr.find_all("td")]
        if cells:
            rows.append(cells)
            
    # Load into a Pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # --- PIPELINE OPERATIONS ---
    # 1. Standardize hidden missing spaces or literal "None" strings into standard Pandas NA values
    df.replace(r'^\s*$', pd.NA, regex=True, inplace=True)
    df.replace('None', pd.NA, inplace=True)
    
    # 2. Isolate Null entries (Drop rows missing critical information like Price or Availability)
    null_mask = df.isna().any(axis=1)
    if null_mask.any():
        print(f"    ↳ Found broken data entries. Dropping {null_mask.sum()} invalid record(s).")
        df.dropna(subset=["Price", "Availability"], inplace=True)
        
    # 3. Deduplicate text entries
    initial_count = len(df)
    df.drop_duplicates(inplace=True)
    deduped_count = initial_count - len(df)
    if deduped_count > 0:
        print(f"    ↳ Deduplication complete. Removed {deduped_count} repetitive log row(s).")
        
    # 4. Standardize and Cast Data Formats (Strip '$' character, map columns to numeric floats/ints)
    df["Price"] = df["Price"].astype(str).str.replace("$", "", regex=False).astype(float)
    df["Product ID"] = df["Product ID"].astype(int)
    
    return df.reset_index(drop=True)


def load_cleaned_output(df: pd.DataFrame, output_directory: str):
    """LOAD Step: Automated storage manager script that dumps verified data into clean local layer."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"cleaned_analytics_export_{timestamp}.csv"
    destination_path = os.path.join(output_directory, filename)
    
    print(f"[3/3] Executing storage layer loader. Saving cleanly to: {destination_path}")
    df.to_csv(destination_path, index=False)
    print("Pipeline Process Executed and Finalized Successfully.")


# --- AUTOMATION RUNNER ---
if __name__ == "__main__":
    # Boot up the simulation web page thread
    server_thread = threading.Thread(target=run_mock_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # Brief delay to allow backend spin up
    
    try:
        # Run the full ETL pipeline workflow
        raw_html = extract_raw_web_data(TARGET_URL)
        cleaned_df = parse_and_clean_data(raw_html)
        
        print("\n--- Cleaned Dataframe Output Result ---")
        print(cleaned_df.to_string())
        print("----------------------------------------\n")
        
        load_cleaned_output(cleaned_df, OUTPUT_DIR)
        
    except Exception as e:
        print(f"Pipeline Process Terminated: {e}")