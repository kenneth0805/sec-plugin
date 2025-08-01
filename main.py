from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from financial_agent import FinancialAgent
from app import fetch_company_cik_map
import difflib

app = FastAPI()
CIK_MAP = fetch_company_cik_map()

class CompanyRequest(BaseModel):
    company_name: str

@app.post("/query")
def query_financials(req: CompanyRequest):
    company_name = req.company_name.strip()
    lookup = {k.lower(): v for k, v in CIK_MAP.items()}
    cik = lookup.get(company_name.lower())

    if not cik:
        matches = difflib.get_close_matches(company_name, CIK_MAP.keys(), n=3, cutoff=0.4)
        msg = f"❌ 未找到 “{company_name}” 的精确 CIK。\n候选：{', '.join(matches)}"
        return PlainTextResponse(msg)

    agent = FinancialAgent(cik)
    df = agent.get_10k_xbrl_links()

    lines = [f"✅ 查询到 {company_name.upper()}（CIK: {cik}）的 10-K 财报："]
    for row in df.itertuples(index=False):
        lines.append(f"- {row.year} ({row.filing_date}) → {row.url}")
    return PlainTextResponse("\n".join(lines))
