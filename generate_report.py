from fpdf import FPDF
from datetime import datetime

def export_pdf(df, org):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"{org.upper()} Cyber Audit – {datetime.now():%b %Y}", ln=1, align="C")
    pdf.set_font("Helvetica", size=10)
    pdf.ln(5)
    for _, row in df.iterrows():
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, f"ID: {row['event_id']}", ln=1)
        pdf.set_font("Helvetica", size=9)
        pdf.multi_cell(0, 5, f"""
Risk Score: {row['risk_score']:.1%}
Gap: {row['gap_sec']:.0f}s
Wallet: {row['wallet_balance_change']:+,.0f}
→ {'BLOCKCHAIN TAMPER' if row['gap_sec']>300 else 'PRIVILEGE ESCALATION'}
        """.strip())
        pdf.ln(3)
    pdf.output(f"reports/{org}_Audit_{datetime.now():%b%Y}.pdf")
