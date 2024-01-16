import frappe
from tourism_portal.api.company import get_company_details
from tourism_portal.pdf import get_voucher_pdf


@frappe.whitelist()
def print_voucher(voucher_no):
    company_details = get_company_details()
    if company_details['is_child_company']:
        invoice = frappe.get_doc("Sales Invoice", {"voucher_no": voucher_no, "child_company": company_details['child_company']})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"voucher_no": voucher_no, "company": company_details['company']})
    # pdf = frappe.get_print(doctype="Sales Invoice", name=invoice.name, print_format="Sales Voucher", as_pdf=True, letterhead='VOUCHER HEADER')
    # frappe.local.response.filename = invoice.voucher_no + ".pdf"
    # frappe.local.response.filecontent = pdf
    # frappe.local.response.type = "pdf"
    return get_voucher_pdf(invoice)


@frappe.whitelist()
def print_invoice_voucher(invoice_no):
    user_type = frappe.db.get_value("User", frappe.session.user, "user_type", cache=True)
    if user_type != "System User":
        return "You are not allowed to print invoice voucher"
    print(invoice_no)
    invoice = frappe.get_doc("Sales Invoice", invoice_no)
    return get_voucher_pdf(invoice)