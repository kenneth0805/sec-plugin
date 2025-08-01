import requests
import pandas as pd

class FinancialAgent:
    def __init__(self, cik: str):
        self.cik = cik.zfill(10)
        self.headers = {
            "User-Agent": "252983421@qq.com"  # 替换为你自己的邮箱地址
        }

    def get_10k_xbrl_links(self):
        base_url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        resp = requests.get(base_url, headers=self.headers)
        data = resp.json()

        index_files = data.get("filings", {}).get("files", [])
        results = []

        for file in index_files:
            year_url = f"https://data.sec.gov{file['name']}"
            year_resp = requests.get(year_url, headers=self.headers)
            if year_resp.status_code != 200:
                continue

            year_data = year_resp.json()
            for filing in year_data.get("filings", []):
                if filing.get("form") == "10-K":
                    accession = filing["accessionNumber"].replace("-", "")
                    filing_date = filing["filingDate"]
                    year = filing_date[:4]
                    xbrl_url = (
                        f"https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/"
                        f"{accession}/Financial_Report.xlsx"
                    )
                    results.append({
                        "year": year,
                        "filing_date": filing_date,
                        "url": xbrl_url
                    })

        df = pd.DataFrame(results).sort_values("year", ascending=False).reset_index(drop=True)
        return df
