import frappe
from tourism_portal.api.company import get_company_details
from tourism_portal.pdf import get_voucher_pdf, get_invoice_pdf
from tourism_portal.tourism_portal.doctype.turf.turf import get_company_turfs
from tourism_portal.utils import get_absolute_path


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
def print_invoice(voucher_no):
    company_details = get_company_details()
    if company_details['is_child_company']:
        invoice = frappe.get_doc("Sales Invoice", {"voucher_no": voucher_no, "child_company": company_details['child_company']})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"voucher_no": voucher_no, "company": company_details['company']})
    return get_invoice_pdf(invoice)


@frappe.whitelist()
def print_invoice_voucher(invoice_no):
    user_type = frappe.db.get_value("User", frappe.session.user, "user_type", cache=True)
    if user_type != "System User":
        return "You are not allowed to print invoice voucher"

    invoice = frappe.get_doc("Sales Invoice", invoice_no)
    return get_voucher_pdf(invoice)

@frappe.whitelist()
def print_invoice_invoice(invoice_no):
    user_type = frappe.db.get_value("User", frappe.session.user, "user_type", cache=True)
    if user_type != "System User":
        return "You are not allowed to print invoice voucher"
    
    invoice = frappe.get_doc("Sales Invoice", invoice_no)
    return get_invoice_pdf(invoice)

@frappe.whitelist()
def view_turf(turf):
    turfs = get_company_turfs()
    turf_link = None
    turf_name = None
    for t in turfs:
        print(t)
        if t.get("turf").get('name') == turf:
            turf_link = t.get("turf").get("turf_file")
            turf_name = t.get("turf").get("name")
            break
    if not turf_link:
        frappe.throw("Turf not found")
    
    file_path = get_absolute_path(turf_link)
    file_content = None
    with open(file_path, "rb") as f:
        file_content = f.read()
    frappe.local.response.filename = turf_name
    frappe.local.response.filecontent = file_content
    frappe.local.response.type = "pdf"

@frappe.whitelist()
def download_turf(turf):
    turfs = get_company_turfs()
    turf_link = None
    turf_name = None
    for t in turfs:
        print(t)
        if t.get("turf").get('name') == turf:
            turf_link = t.get("turf").get("turf_file")
            turf_name = t.get("turf").get("name")
            break
    if not turf_link:
        frappe.throw("Turf not found")
    
    file_path = get_absolute_path(turf_link)
    file_content = None
    with open(file_path, "rb") as f:
        file_content = f.read()
    frappe.local.response.filename = turf_name + "." + file_path.split(".")[-1]
    frappe.local.response.filecontent = file_content
    frappe.local.response.type = "download"
    