import requests

def fetch_company_cik_map():
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        "User-Agent": "your_email@example.com"  # 修改为你自己的邮箱
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    cik_map = {}
    for _, info in data.items():
        name = info["title"].strip()
        cik = str(info["cik_str"]).zfill(10)
        cik_map[name] = cik
    return cik_map
