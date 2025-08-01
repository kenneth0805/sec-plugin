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

    # 转成 DataFrame 并按年份倒序排序
    df = pd.DataFrame(results).sort_values("year", ascending=False).reset_index(drop=True)

    # 构造 {year: "year 年财报：url"} 格式
    result_dict = {}
    for _, row in df.iterrows():
        result_dict[row["year"]] = f"{row['year']} 年财报：{row['url']}"

    return result_dict

