from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time



def scrape_important_announcements(output_path="./dataset/Important Announcements.txt"):   
    """
    Scrape important announcements from Bahria University's website pop-up.
    
    Args:
        output_path (str): Path to save the extracted announcements.
    """
# Set up the Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# Initialize the driver
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

try:
    # Navigate to the website
    base_url = "https://www.bahria.edu.pk"
    url = f"{base_url}/home/index"
    print(f"Navigating to {url}...")
    driver.get(url)
    
    # Wait for the pop-up to appear and become visible
    print("Waiting for pop-up to appear...")
    wait = WebDriverWait(driver, 10)
    popup_content = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "popup-content"))
    )
    
    # Wait for the content to be visible
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "popup-content")))
    
    # Give it a moment to fully render
    time.sleep(2)
    
    # Extract title
    print("Extracting pop-up content...")
    popup_title = popup_content.find_element(By.CLASS_NAME, "popup-title").text
    
    # Extract all links and their text
    links = popup_content.find_elements(By.CLASS_NAME, "popup-link")
    
    # Prepare content with links
    content_lines = [popup_title]
    content_lines.append("")  # Empty line for readability
    
    for link in links:
        link_text = link.text
        link_url = link.get_attribute("href")
        
        # Convert relative URLs to full URLs
        if link_url.startswith("/"):
            link_url = base_url + link_url
        elif not link_url.startswith("http"):
            link_url = base_url + "/" + link_url
        
        content_lines.append(f"{link_text}")
        content_lines.append(f"Link: {link_url}")
        content_lines.append("")  # Empty line for readability
    
    # Join all content
    full_content = "\n".join(content_lines)
    
    # Print the extracted content
    print("\n" + "="*60)
    print("="*60)
    print(full_content)
    
    # Save to file
    with open("./dataset/Important Announcements.txt", "w", encoding="utf-8") as f:
        f.write(full_content)
    
    print("\n✓ Content saved to 'Important Announcement.txt'")
    
except Exception as e:
    print(f"Error occurred: {e}")

finally:
    driver.quit()
    print("Browser closed.")