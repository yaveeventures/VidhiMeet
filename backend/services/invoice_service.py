import html
import json
import smtplib
import ssl
import urllib.request
from datetime import datetime, timezone
import structlog
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Booking, User

log = structlog.get_logger("invoice_service")
settings = get_settings()


def get_invoice_number(booking: Booking) -> str:
    """Generate deterministic, collision-free invoice number."""
    dt = booking.created_at or datetime.now(timezone.utc)
    date_part = dt.strftime("%Y%m")
    clean_id = booking.id.replace("-", "")[:8].upper()
    return f"VM-INV-{date_part}-{clean_id}"


def calculate_tax_breakdown(platform_fee_minor: int) -> dict:
    """
    Calculate GST breakdown for platform fee (inclusive of 18% GST).
    SAC Code: 998315 (Hosting and IT Infrastructure Provisioning Services)
    """
    total_fee = platform_fee_minor / 100.0
    # Base taxable value (18% inclusive)
    base_taxable = round(total_fee / 1.18, 2)
    total_gst = round(total_fee - base_taxable, 2)
    cgst = round(total_gst / 2.0, 2)
    sgst = round(total_gst - cgst, 2)
    return {
        "total_fee": total_fee,
        "base_taxable": base_taxable,
        "total_gst": total_gst,
        "cgst": cgst,
        "sgst": sgst,
        "igst": total_gst,
        "rate_percent": 18,
    }


def generate_client_receipt_html(booking: Booking, client: User, lawyer: User | None = None) -> str:
    """
    Generate print-ready, legally compliant HTML Tax Invoice & Receipt for the client.
    Complies with IT Act 2000 Section 79 (Intermediary Marketplace) and GST rules.
    """
    inv_number = get_invoice_number(booking)
    created_dt = booking.created_at or datetime.now(timezone.utc)
    date_str = created_dt.strftime("%d %B %Y, %I:%M %p UTC")

    # Financial calculations
    total_paid = round(booking.amount_minor / 100.0, 2)
    base_price = round(booking.base_price_minor / 100.0, 2)
    platform_fee = round(booking.client_platform_fee_minor / 100.0, 2)
    tax_info = calculate_tax_breakdown(booking.client_platform_fee_minor)

    # Names and practice
    client_name = html.escape(client.full_name or "Client")
    client_email = html.escape(client.email or "N/A")
    client_phone = html.escape(getattr(client, "phone", "") or "N/A")

    lawyer_name = html.escape(lawyer.full_name if lawyer else (booking.lawyer_name or "Verified Advocate"))
    practice_title = html.escape(str(booking.practice.value if hasattr(booking.practice, "value") else booking.practice).replace("_", " ").title())
    cf_order_id = html.escape(booking.cashfree_order_id or "N/A")

    scheduled_str = booking.starts_at.strftime("%d %B %Y, %I:%M %p UTC") if booking.starts_at else "As scheduled"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tax Invoice &amp; Payment Receipt — {inv_number}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #1b4332;
      --primary-dark: #0f281e;
      --forest: #2d6a4f;
      --gold: #d4af37;
      --slate-900: #0f172a;
      --slate-700: #334155;
      --slate-600: #475569;
      --slate-500: #64748b;
      --slate-200: #e2e8f0;
      --slate-50: #f8fafc;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: var(--slate-900);
      background-color: #f1f5f9;
      line-height: 1.5;
      padding: 30px 16px;
    }}
    .action-bar {{
      max-width: 820px;
      margin: 0 auto 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s;
    }}
    .btn-primary {{
      background: var(--primary);
      color: #ffffff;
      border: 1px solid var(--primary-dark);
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .btn-primary:hover {{ background: var(--forest); }}
    .btn-outline {{
      background: #ffffff;
      color: var(--slate-700);
      border: 1px solid var(--slate-200);
    }}
    .btn-outline:hover {{ background: var(--slate-50); }}
    .invoice-card {{
      max-width: 820px;
      margin: 0 auto;
      background: #ffffff;
      border: 1px solid var(--slate-200);
      border-radius: 12px;
      padding: 44px 48px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
    }}
    .invoice-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid var(--slate-200);
      padding-bottom: 28px;
      margin-bottom: 28px;
    }}
    .brand-logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: var(--primary);
      text-decoration: none;
    }}
    .brand-logo span {{ color: var(--gold); }}
    .company-details {{
      font-size: 12.5px;
      color: var(--slate-600);
      margin-top: 8px;
      max-width: 380px;
      line-height: 1.45;
    }}
    .invoice-meta {{
      text-align: right;
    }}
    .invoice-meta h1 {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 22px;
      font-weight: 800;
      color: var(--slate-900);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .meta-tag {{
      display: inline-block;
      margin-top: 6px;
      background: #ecfdf5;
      color: #065f46;
      border: 1px solid #a7f3d0;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 9999px;
    }}
    .meta-row {{
      font-size: 13px;
      color: var(--slate-600);
      margin-top: 6px;
    }}
    .meta-row strong {{ color: var(--slate-900); }}

    .parties-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 28px;
      background: var(--slate-50);
      border: 1px solid var(--slate-200);
      border-radius: 8px;
      padding: 20px 24px;
      margin-bottom: 32px;
    }}
    .party-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--slate-500);
      margin-bottom: 6px;
    }}
    .party-name {{
      font-size: 15px;
      font-weight: 700;
      color: var(--slate-900);
      margin-bottom: 4px;
    }}
    .party-desc {{
      font-size: 13px;
      color: var(--slate-600);
      line-height: 1.4;
    }}

    table.invoice-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 24px;
    }}
    table.invoice-table th {{
      background: #f8fafc;
      text-align: left;
      padding: 12px 14px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--slate-600);
      border-bottom: 2px solid var(--slate-200);
    }}
    table.invoice-table td {{
      padding: 14px;
      font-size: 13.5px;
      color: var(--slate-700);
      border-bottom: 1px solid var(--slate-200);
      vertical-align: top;
    }}
    .text-right {{ text-align: right; }}
    .item-desc {{
      font-size: 12px;
      color: var(--slate-500);
      margin-top: 4px;
      line-height: 1.4;
    }}

    .summary-section {{
      display: flex;
      justify-content: flex-end;
      margin-bottom: 28px;
    }}
    .summary-box {{
      width: 320px;
    }}
    .summary-row {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      color: var(--slate-600);
      padding: 6px 0;
    }}
    .summary-row.total {{
      border-top: 2px solid var(--slate-900);
      margin-top: 8px;
      padding-top: 10px;
      font-size: 17px;
      font-weight: 800;
      color: var(--primary);
    }}

    .payment-badge {{
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }}

    .disclaimer-box {{
      border-top: 1px solid var(--slate-200);
      padding-top: 20px;
      font-size: 11.5px;
      color: var(--slate-500);
      line-height: 1.5;
    }}
    .disclaimer-box p {{ margin-bottom: 6px; }}

    @media print {{
      body {{
        background: #ffffff !important;
        padding: 0 !important;
      }}
      .action-bar {{ display: none !important; }}
      .invoice-card {{
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
      }}
    }}
  </style>
</head>
<body>

  <div class="action-bar">
    <a href="javascript:window.history.back()" class="btn btn-outline">← Back</a>
    <button onclick="window.print()" class="btn btn-primary">🖨️ Print / Save as PDF</button>
  </div>

  <div class="invoice-card">
    <div class="invoice-header">
      <div>
        <a href="/" class="brand-logo">⚖️ {settings.company_brand}<span>.in</span></a>
        <div class="company-details">
          <strong>{settings.company_name}</strong><br>
          {settings.company_address}<br>
          <strong>GSTIN:</strong> {settings.company_gstin} &middot; <strong>PAN:</strong> {settings.company_pan}<br>
          <strong>Support:</strong> {settings.company_support_email}
        </div>
      </div>
      <div class="invoice-meta">
        <h1>Tax Invoice &amp; Receipt</h1>
        <div class="meta-tag">PAID &amp; CONFIRMED ✓</div>
        <div class="meta-row"><strong>Invoice No:</strong> {inv_number}</div>
        <div class="meta-row"><strong>Date:</strong> {date_str}</div>
        <div class="meta-row"><strong>Cashfree Ref:</strong> {cf_order_id}</div>
      </div>
    </div>

    <div class="parties-grid">
      <div>
        <div class="party-title">Billed To (Client)</div>
        <div class="party-name">{client_name}</div>
        <div class="party-desc">
          Email: {client_email}<br>
          Phone: {client_phone}
        </div>
      </div>
      <div>
        <div class="party-title">Consultation Service (Advocate)</div>
        <div class="party-name">{lawyer_name}</div>
        <div class="party-desc">
          Practice: {practice_title}<br>
          Scheduled Time: {scheduled_str}
        </div>
      </div>
    </div>

    <table class="invoice-table">
      <thead>
        <tr>
          <th style="width: 5%;">#</th>
          <th style="width: 55%;">Description</th>
          <th style="width: 15%;">SAC / HSN</th>
          <th style="width: 10%;" class="text-right">Rate</th>
          <th style="width: 15%;" class="text-right">Amount (INR)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1</td>
          <td>
            <strong>Advocate Professional Consultation Fee</strong>
            <div class="item-desc">
              Online private video legal consultation with Advocate {lawyer_name} ({practice_title}).<br>
              <em>*Collected by {settings.company_brand} in escrow as a pure collection agent on behalf of the Advocate under Bar Council of India guidelines.</em>
            </div>
          </td>
          <td>Pure Agent</td>
          <td class="text-right">₹{base_price:,.2f}</td>
          <td class="text-right">₹{base_price:,.2f}</td>
        </tr>
        <tr>
          <td>2</td>
          <td>
            <strong>Technology &amp; Platform Infrastructure Usage Fee</strong>
            <div class="item-desc">
              Marketplace platform provisioning, encrypted room infrastructure, end-to-end security &amp; escrow management service.
            </div>
          </td>
          <td>998315</td>
          <td class="text-right">₹{tax_info['base_taxable']:,.2f}</td>
          <td class="text-right">₹{tax_info['base_taxable']:,.2f}</td>
        </tr>
        <tr>
          <td>3</td>
          <td>
            <strong>CGST (9%)</strong>
            <div class="item-desc">Central Goods &amp; Services Tax on platform fee</div>
          </td>
          <td>998315</td>
          <td class="text-right">9%</td>
          <td class="text-right">₹{tax_info['cgst']:,.2f}</td>
        </tr>
        <tr>
          <td>4</td>
          <td>
            <strong>SGST (9%)</strong>
            <div class="item-desc">State Goods &amp; Services Tax on platform fee</div>
          </td>
          <td>998315</td>
          <td class="text-right">9%</td>
          <td class="text-right">₹{tax_info['sgst']:,.2f}</td>
        </tr>
      </tbody>
    </table>

    <div class="summary-section">
      <div class="summary-box">
        <div class="summary-row">
          <span>Advocate Consultation Fee:</span>
          <span>₹{base_price:,.2f}</span>
        </div>
        <div class="summary-row">
          <span>Platform Fee (Taxable):</span>
          <span>₹{tax_info['base_taxable']:,.2f}</span>
        </div>
        <div class="summary-row">
          <span>Total GST (CGST 9% + SGST 9%):</span>
          <span>₹{tax_info['total_gst']:,.2f}</span>
        </div>
        <div class="summary-row total">
          <span>Total Paid:</span>
          <span>₹{total_paid:,.2f}</span>
        </div>
      </div>
    </div>

    <div class="payment-badge">
      <div>
        <strong>Payment Gateway:</strong> Cashfree Payments India Pvt Ltd (Order ID: <code>{cf_order_id}</code>)
      </div>
      <div>
        <strong>Currency:</strong> INR (₹) &middot; <strong>Status:</strong> Completed
      </div>
    </div>

    <div class="disclaimer-box">
      <p><strong>Statutory Notice under Section 79 of the Information Technology Act, 2000:</strong> {settings.company_name} (operating brand "{settings.company_brand}") is an Electronic Marketplace Intermediary. {settings.company_brand} does not provide legal advice, represent clients before courts, or participate in attorney-client privileged relationships. Legal advice is provided solely and directly by independent enrolled Advocates.</p>
      <p><strong>GST Note:</strong> In accordance with Notification No. 12/2017-Central Tax (Rate), legal services provided by individual advocates to non-business entities are exempt from GST / subject to Reverse Charge Mechanism (RCM). GST is charged only on the Technology &amp; Platform Infrastructure Usage Fee.</p>
      <p style="margin-top: 10px; color: var(--slate-600); text-align: center;"><em>This document is an electronically generated Tax Invoice &amp; Payment Receipt and requires no physical signature.</em></p>
    </div>
  </div>

</body>
</html>"""


def generate_lawyer_settlement_advice_html(booking: Booking, lawyer: User) -> str:
    """
    Generate print-ready Settlement Advice (Payout Disbursement Voucher) for Advocates.
    Details gross consultation earnings, platform facilitation deduction, and net disbursement.
    """
    inv_number = f"SA-{get_invoice_number(booking)}"
    payout_dt = booking.payout_at or booking.completed_at or datetime.now(timezone.utc)
    date_str = payout_dt.strftime("%d %B %Y, %I:%M %p UTC")

    gross_fee = round(booking.base_price_minor / 100.0, 2)
    platform_deduction = round(booking.lawyer_platform_fee_minor / 100.0, 2)
    net_payout = round(gross_fee - platform_deduction, 2)
    tax_info = calculate_tax_breakdown(booking.lawyer_platform_fee_minor)

    lawyer_name = html.escape(lawyer.full_name or "Advocate")
    lawyer_email = html.escape(lawyer.email or "N/A")
    practice_title = html.escape(str(booking.practice.value if hasattr(booking.practice, "value") else booking.practice).replace("_", " ").title())
    payout_ref = html.escape(booking.payout_reference_id or booking.cashfree_order_id or "PENDING")

    bank_info = ""
    if lawyer and hasattr(lawyer, "bank_account") and lawyer.bank_account:
        b_acct = lawyer.bank_account
        b_name = html.escape(getattr(b_acct, "bank_name", "") or "")
        raw_num = str(getattr(b_acct, "account_number", "") or "")
        masked_num = f"••••{raw_num[-4:]}" if len(raw_num) >= 4 else "Linked Account"
        if b_name:
            bank_info = f" &middot; <strong>Bank:</strong> {b_name} ({masked_num})"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Advocate Settlement Advice — {inv_number}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #1b4332;
      --forest: #2d6a4f;
      --slate-900: #0f172a;
      --slate-700: #334155;
      --slate-600: #475569;
      --slate-200: #e2e8f0;
      --slate-50: #f8fafc;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--slate-900);
      background: #f1f5f9;
      padding: 30px 16px;
      line-height: 1.5;
    }}
    .action-bar {{
      max-width: 820px;
      margin: 0 auto 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .btn {{
      padding: 10px 20px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      text-decoration: none;
    }}
    .btn-primary {{
      background: var(--primary);
      color: #fff;
      border: 1px solid var(--forest);
    }}
    .btn-outline {{
      background: #fff;
      color: var(--slate-700);
      border: 1px solid var(--slate-200);
    }}
    .card {{
      max-width: 820px;
      margin: 0 auto;
      background: #fff;
      border: 1px solid var(--slate-200);
      border-radius: 12px;
      padding: 44px 48px;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      border-bottom: 2px solid var(--slate-200);
      padding-bottom: 24px;
      margin-bottom: 24px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      margin-bottom: 20px;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--slate-200);
      font-size: 13.5px;
    }}
    th {{ background: #f8fafc; text-align: left; font-weight: 700; color: var(--slate-600); }}
    .text-right {{ text-align: right; }}
    @media print {{
      body {{ background: #fff !important; padding: 0 !important; }}
      .action-bar {{ display: none !important; }}
      .card {{ border: none !important; box-shadow: none !important; padding: 0 !important; }}
    }}
  </style>
</head>
<body>
  <div class="action-bar">
    <a href="javascript:window.history.back()" class="btn btn-outline">← Back</a>
    <button onclick="window.print()" class="btn btn-primary">🖨️ Print / Save Voucher</button>
  </div>

  <div class="card">
    <div class="header">
      <div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; color:var(--primary);">⚖️ {settings.company_brand}</h2>
        <p style="font-size:12.5px; color:var(--slate-600); margin-top:4px;">
          <strong>{settings.company_name}</strong><br>
          GSTIN: {settings.company_gstin} &middot; PAN: {settings.company_pan}<br>
          {settings.company_address}
        </p>
      </div>
      <div style="text-align:right;">
        <h3 style="font-size:18px; text-transform:uppercase;">Payout Settlement Advice</h3>
        <span style="display:inline-block; margin-top:4px; padding:3px 10px; background:#ecfdf5; color:#065f46; border-radius:999px; font-size:12px; font-weight:700;">DISBURSED ✓</span>
        <p style="font-size:13px; color:var(--slate-600); margin-top:6px;"><strong>Voucher:</strong> {inv_number}<br><strong>Disbursement Date:</strong> {date_str}</p>
      </div>
    </div>

    <div style="background:var(--slate-50); border:1px solid var(--slate-200); border-radius:8px; padding:16px 20px; margin-bottom:24px;">
      <p style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--slate-600);">Payee (Advocate)</p>
      <p style="font-size:15px; font-weight:700; color:var(--slate-900);">{lawyer_name}</p>
      <p style="font-size:13px; color:var(--slate-600);">Email: {lawyer_email} &middot; Practice Area: {practice_title}</p>
    </div>

    <table>
      <thead>
        <tr>
          <th>Description</th>
          <th>Reference</th>
          <th class="text-right">Credit (INR)</th>
          <th class="text-right">Debit (INR)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <strong>Consultation Professional Fee (Escrow Release)</strong>
            <div style="font-size:12px; color:var(--slate-500); margin-top:3px;">Consultation ID: {booking.id} (Dispute window cleared)</div>
          </td>
          <td>Escrow Release</td>
          <td class="text-right">₹{gross_fee:,.2f}</td>
          <td class="text-right">-</td>
        </tr>
        <tr>
          <td>
            <strong>VidhiMeet Platform Facilitation Commission</strong>
            <div style="font-size:12px; color:var(--slate-500); margin-top:3px;">Base fee: ₹{tax_info['base_taxable']:,.2f} + 18% GST: ₹{tax_info['total_gst']:,.2f} (SAC 998315)</div>
          </td>
          <td>Platform Fee</td>
          <td class="text-right">-</td>
          <td class="text-right">₹{platform_deduction:,.2f}</td>
        </tr>
        <tr style="font-weight:700; background:#f8fafc; font-size:15px;">
          <td colspan="2">Net Disbursed to Advocate Bank Account:</td>
          <td colspan="2" class="text-right" style="color:var(--primary);">₹{net_payout:,.2f}</td>
        </tr>
      </tbody>
    </table>

    <div style="background:#f8fafc; border:1px dashed #cbd5e1; border-radius:8px; padding:14px 18px; margin-top:20px; font-size:13px;">
      <strong>Disbursement Method:</strong> Direct Bank Transfer (Cashfree Payouts){bank_info} &middot; <strong>UTR / Reference ID:</strong> <code>{payout_ref}</code>
    </div>

    <p style="margin-top:28px; font-size:11.5px; color:var(--slate-500); line-height:1.5;">
      <em>Note: VidhiMeet is an intermediary technology marketplace under Section 79 of the Information Technology Act, 2000. This settlement advice confirms the net transfer of consultation earnings after deduction of the agreed platform infrastructure fee. Advocates practice as independent legal professionals and are responsible for their individual direct tax filings.</em>
    </p>
  </div>
</body>
</html>"""


def send_booking_receipt_email(booking: Booking, client: User, lawyer: User | None = None) -> bool:
    """
    Send an automated booking confirmation and payment receipt email to the client
    via Resend API or SMTP.
    """
    to_email = client.email
    if not to_email:
        return False

    inv_number = get_invoice_number(booking)
    total_paid = round(booking.amount_minor / 100.0, 2)
    base_price = round(booking.base_price_minor / 100.0, 2)
    platform_fee = round(booking.client_platform_fee_minor / 100.0, 2)
    lawyer_name = lawyer.full_name if lawyer else (booking.lawyer_name or "Verified Advocate")
    scheduled_str = booking.starts_at.strftime("%d %b %Y, %I:%M %p UTC") if booking.starts_at else "Scheduled"
    from_email = getattr(settings, "smtp_from_email", "support@vidhimeet.in") or "support@vidhimeet.in"

    subject = f"VidhiMeet — Consultation Confirmed & Payment Receipt ({inv_number})"

    receipt_url = f"https://vidhimeet.in/api/v1/bookings/{booking.id}/receipt"
    try:
        from ..security import create_access_token
        view_token = create_access_token(client)
        receipt_url = f"https://vidhimeet.in/api/v1/bookings/{booking.id}/receipt?token={view_token}"
    except Exception:
        pass

    html_content = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; margin: 0; padding: 24px; }}
    .box {{ max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 32px; }}
    .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 18px; margin-bottom: 20px; }}
    .brand {{ font-size: 20px; font-weight: 800; color: #1b4332; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th, td {{ padding: 10px 12px; text-align: left; font-size: 13.5px; border-bottom: 1px solid #e2e8f0; }}
    th {{ background: #f8fafc; font-weight: 700; color: #475569; }}
    .total {{ font-weight: 800; font-size: 16px; color: #1b4332; }}
    .btn {{ display: inline-block; background-color: #1b4332; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center; }}
    .footer {{ font-size: 11.5px; color: #64748b; margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 16px; line-height: 1.5; }}
  </style>
</head>
<body>
  <div class="box">
    <div class="header">
      <div class="brand">⚖️ {settings.company_brand}</div>
      <p style="font-size: 13px; color: #64748b; margin-top: 4px;">{settings.company_name} &middot; GSTIN: {settings.company_gstin}</p>
    </div>
    <h2 style="font-size: 18px; color: #0f172a; margin-bottom: 8px;">Your consultation is confirmed!</h2>
    <p style="font-size: 14px; color: #334155; line-height: 1.5;">
      Hello <strong>{html.escape(client.full_name or 'Client')}</strong>, your online legal consultation with <strong>Advocate {html.escape(lawyer_name)}</strong> has been booked and your payment of <strong>₹{total_paid:,.2f}</strong> was received successfully.
    </p>

    <div style="background: #f1f5f9; border-radius: 8px; padding: 14px 18px; margin: 20px 0; font-size: 13.5px;">
      <p style="margin: 3px 0;"><strong>Consultation Time:</strong> {scheduled_str}</p>
      <p style="margin: 3px 0;"><strong>Advocate:</strong> {html.escape(lawyer_name)}</p>
      <p style="margin: 3px 0;"><strong>Invoice / Receipt No:</strong> {inv_number}</p>
      <p style="margin: 3px 0;"><strong>Payment Reference:</strong> {booking.cashfree_order_id or 'Online'}</p>
    </div>

    <table>
      <thead>
        <tr>
          <th>Item</th>
          <th style="text-align: right;">Amount</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Advocate Professional Fee (Escrow)</td>
          <td style="text-align: right;">₹{base_price:,.2f}</td>
        </tr>
        <tr>
          <td>Platform Usage Fee (incl. 18% GST)</td>
          <td style="text-align: right;">₹{platform_fee:,.2f}</td>
        </tr>
        <tr class="total">
          <td>Total Paid</td>
          <td style="text-align: right;">₹{total_paid:,.2f}</td>
        </tr>
      </tbody>
    </table>

    <div style="text-align: center; margin: 26px 0 20px;">
      <a href="{receipt_url}" target="_blank" class="btn">
        🧾 View &amp; Print Official Tax Invoice (PDF)
      </a>
    </div>

    <p style="font-size: 13px; color: #334155;">
      You can access your secure video room 15 minutes before the scheduled time directly from your VidhiMeet dashboard.
    </p>

    <div class="footer">
      <p><strong>VidhiMeet Marketplace Intermediary Notice:</strong> {settings.company_name} is an intermediary under Sec 79 of the IT Act 2000. Professional legal counsel is rendered exclusively by independent enrolled Advocates.</p>
    </div>
  </div>
</body>
</html>"""

    # Dispatch via Resend API or SMTP
    smtp_server = (getattr(settings, "smtp_server", "") or "").strip()
    smtp_port = int(getattr(settings, "smtp_port", 587) or 587)
    smtp_user = (getattr(settings, "smtp_user", "") or "").strip()
    smtp_password = (getattr(settings, "smtp_password", "") or "").strip()

    # 1. Resend HTTPS API (Port 443) - reliable in serverless/PaaS
    if smtp_password.startswith("re_") or smtp_server.lower() == "smtp.resend.com":
        try:
            payload = {
                "from": f"VidhiMeet Billing <{from_email}>",
                "to": [to_email],
                "reply_to": from_email,
                "subject": subject,
                "html": html_content,
            }
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {smtp_password}",
                    "Content-Type": "application/json",
                    "User-Agent": "VidhiMeet-Backend/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    log.info("Booking receipt email dispatched via Resend", recipient=to_email, booking_id=booking.id)
                    return True
        except Exception as exc:
            log.warning("Failed to send receipt email via Resend API", error=str(exc))

    # 2. Standard SMTP Dispatch (Supports SSL port 465 and STARTTLS port 587)
    if smtp_server and smtp_user:
        try:
            from email.message import EmailMessage
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = f"VidhiMeet Billing <{from_email}>"
            msg["Reply-To"] = from_email
            msg["To"] = to_email
            msg.set_content(
                f"Your consultation with Advocate {lawyer_name} is confirmed.\n"
                f"Total Paid: ₹{total_paid:,.2f}\n"
                f"Invoice / Receipt No: {inv_number}\n"
                f"View and print your official Tax Invoice: {receipt_url}"
            )
            msg.add_alternative(html_content, subtype="html")

            if smtp_port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=10) as server:
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)

            log.info("Booking receipt email dispatched via SMTP", recipient=to_email, booking_id=booking.id)
            return True
        except Exception as exc:
            log.warning("Failed to send receipt email via SMTP", error=str(exc))
    else:
        log.info("Booking receipt email generated (SMTP/Resend not configured in environment)", recipient=to_email, receipt_url=receipt_url)

    return False
