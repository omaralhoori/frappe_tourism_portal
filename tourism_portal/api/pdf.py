import frappe
from tourism_portal.api.company import get_company_details
from frappe.utils.pdf import get_pdf
import pdfkit
@frappe.whitelist()
def print_voucher(voucher_no):
    company_details = get_company_details()
    if company_details['is_child_company']:
        invoice = frappe.get_doc("Sales Invoice", {"voucher_no": voucher_no, "child_company": company_details['child_company']})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"voucher_no": voucher_no, "company": company_details['company']})
    pdf = frappe.get_print(doctype="Sales Invoice", name=invoice.name, print_format="Sales Voucher", as_pdf=True, no_letterhead=0)
    frappe.local.response.filename = invoice.voucher_no + ".pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"

def get_voucher_pdf(invoice):
    from frappe.utils import get_html_format
    html = frappe.get_print#frappe.render_template("tourism_portal/templates/voucher.html", {"doc": invoice})
    pdf = pdfkit.from_string(html, False, options={"quiet": ""})
    frappe.local.response.filename = invoice.voucher_no + ".pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"

    return pdf