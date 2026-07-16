"""
Module A: Web Scraper for Grant Announcements (Target: Bizinfo / 기업마당)
"""
import requests
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrantScraper:
    def __init__(self):
        # Base URL for Bizinfo (기업마당) search
        self.base_url = "https://www.bizinfo.go.kr"
        # The specific list endpoint
        self.search_url = f"{self.base_url}/web/lay1/bbs/S1T122C128/AS/74/list.do"
        
    def fetch_grants(self, max_items=5):
        """
        Fetches the latest real-time grant announcements from Bizinfo (기업마당).
        Returns a list of dictionaries with grant_id, title, link, content_summary, and due_date.
        """
        logger.info(f"Fetching live grants from {self.search_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            res = requests.get(self.search_url, headers=headers, timeout=10)
            res.raise_for_status()
            res.encoding = "utf-8"
            
            soup = BeautifulSoup(res.text, "html.parser")
            grants = []
            
            table = soup.find("table")
            if not table:
                logger.warning("Could not find list table on Bizinfo page.")
                return []
                
            rows = table.find_all("tr")
            # Skip the header row
            for row in rows[1:]:
                if len(grants) >= max_items:
                    break
                    
                cells = row.find_all("td")
                if len(cells) >= 7:
                    title_link = row.find("a")
                    if title_link:
                        title = title_link.get_text(strip=True)
                        href = title_link.get("href", "")
                        
                        # Extract pblancId
                        pblanc_id_match = re.search(r"pblancId=([^&]+)", href)
                        grant_id = pblanc_id_match.group(1) if pblanc_id_match else "BIZ_UNKNOWN"
                        
                        # Absolute URL
                        full_link = href
                        if href and not href.startswith("http"):
                            full_link = f"{self.base_url}{href}"
                            
                        # Extract application period and due date
                        period = cells[3].get_text(strip=True)
                        due_date = "2026-12-31"  # Default fallback
                        
                        if "~" in period:
                            parts = period.split("~")
                            if len(parts) > 1:
                                raw_due = parts[1].strip()
                                date_match = re.search(r"(\d{4})[-.](\d{2})[-.](\d{2})", raw_due)
                                if date_match:
                                    due_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                                    
                        governing = cells[4].get_text(strip=True)
                        agency = cells[5].get_text(strip=True)
                        category = cells[1].get_text(strip=True)
                        
                        content_summary = (
                            f"분야: {category} | 소관부처: {governing} | 수행기관: {agency} | 신청기간: {period}"
                        )
                        
                        grants.append({
                            "grant_id": grant_id,
                            "title": title,
                            "link": full_link,
                            "due_date": due_date,
                            "content_summary": content_summary
                        })
                        
            logger.info(f"Successfully scraped {len(grants)} live grants.")
            return grants

        except Exception as e:
            logger.error(f"Error fetching live grants: {e}")
            return []

if __name__ == "__main__":
    scraper = GrantScraper()
    grants = scraper.fetch_grants()
    for g in grants:
        print(g)
