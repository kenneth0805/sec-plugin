from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from financial_agent import FinancialAgent
from app import fetch_company_cik_map
import difflib
import re

app = FastAPI()

# 插件元数据托管
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")
CIK_MAP = fetch_company_cik_map()

class CompanyRequest(BaseModel):
    company_name: str

@app.post("/query")
def query_financials(req: CompanyRequest):
    raw_text = req.company_name.strip()
    lookup = {k.lower(): v for k, v in CIK_MAP.items()}

    # 👉 提取年份/区间，例如 "2018 到 2023" 或 "查 FND 的 2020 年报"
    start_year, end_year = None, None
    year_range = re.findall(r"(\d{4})\D+(\d{4})", raw_text)
    if year_range:
        start_year, end_year = year_range[0]
    else:
        single_year = re.findall(r"(\d{4})", raw_text)
        if len(single_year) == 1:
            start_year = end_year = single_year[0]

    # 👉 抽取公司名部分（去掉年份）
    cleaned_text = re.sub(r"\d{4}.*", "", raw_text).strip().lower()
    cik = lookup.get(cleaned_text)

    if not cik:
        matches = difflib.get_close_matches(cleaned_text, CIK_MAP.keys(), n=3, cutoff=0.4)
        msg = f"❌ 未找到 “{cleaned_text}” 的精确 CIK。\n候选：{', '.join(matches)}"
        return PlainTextResponse(msg)

    agent = FinancialAgent(cik)
    df = agent.get_10k_xbrl_links(start_year=start_year, end_year=end_year)

    if df.empty:
        return PlainTextResponse(f"⚠️ 未找到符合条件的 10-K 报告。")

    lines = []
    title = f"✅ 查询到 {cleaned_text.title()}（CIK: {cik}）"
    if start_year and end_year:
        title += f" 从 {start_year} 到 {end_year} 的"
    elif start_year:
        title += f" 的 {start_year} 年"
    title += " 10-K 财报链接（Excel 格式）："

    lines.append(title)
    for row in df.itertuples(index=False):
        lines.append(f"{row.year:<4} ({row.filing_date})  → {row.url}")

    return PlainTextResponse("\n".join(lines))
