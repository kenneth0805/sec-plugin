from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from financial_agent import FinancialAgent
from app import fetch_company_cik_map
import difflib

app = FastAPI()

# 插件文件托管
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")
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

    if df.empty:
        return PlainTextResponse(f"⚠️ 未找到 {company_name} 的任何 10-K 财报。")

    lines = [f"✅ 查询到 {company_name}（CIK: {cik}）的财报链接："]
    for row in df.itertuples(index=False):
        # 对齐输出，年份为4位，→ 前保留两个空格
        lines.append(f"{row.year:<4} ({row.filing_date})  → {row.url}")

    return PlainTextResponse("\n".join(lines))
