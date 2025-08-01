import requests
import pandas as pd

class FinancialAgent:
    def __init__(self, cik: str):
        self.cik = cik.zfill(10)
        self.headers = {
            "User-Agent": "your_email@example.com"  # 请改成你自己的邮箱
        }

    def get_10k_xbrl_links(self):
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        resp = requests.get(url, headers=self.headers)
        data = resp.json()

        filings = data["filings"]["recent"]
        results = []

        for i in range(len(filings["form"])):
            if filings["form"][i] == "10-K":
                accession = filings["accessionNumber"][i].replace("-", "")
                filing_date = filings["filingDate"][i]
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
