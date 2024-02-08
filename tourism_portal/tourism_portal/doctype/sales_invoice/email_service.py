import frappe
from tourism_portal.pdf import get_invoice_pdf, get_voucher_pdf


def send_agency_invoice_email(invoice):
    company = frappe.get_doc("Company", invoice.company)
    if not company.accounting_email:
        return
    # frappe.throw("Please enter accounting email in company")
    invoice_pdf = get_invoice_pdf(invoice, return_content=True)
    frappe.sendmail(
    recipients=[company.accounting_email],
    doctype="Sales Invoice",
    name=invoice.name,
    message="New Sales Invoice has been created",
    subject="Sales Invoice: " + invoice.invoice_no,
    attachments=[{"fname": invoice.invoice_no + ".pdf", "fcontent": invoice_pdf}],
    now=1,
    )

def send_agency_voucher_email(invoice):
    company = frappe.get_doc("Company", invoice.company)
    if not company.reservation_email:
        return
    # frappe.throw("Please enter accounting email in company")
    invoice_pdf = get_voucher_pdf(invoice, return_content=True)
    frappe.sendmail(
    recipients=[company.reservation_email],
    doctype="Sales Invoice",
    name=invoice.name,
    message="New Voucher has been created",
    subject="Reservation Voucher: " + invoice.voucher_no,
    attachments=[{"fname": invoice.voucher_no + ".pdf", "fcontent": invoice_pdf}],
    now=1,
    )