import frappe
from frappe.utils.pdf import get_pdf

def get_voucher_pdf(invoice, return_content=False):
    html = frappe.render_template("tourism_portal/templates/voucher.html", {"doc": invoice})
    options = {
        "quiet": "",
         "--margin-left" : "0","--margin-right" : "0","--margin-bottom": "10mm",
    }
    pdf = get_pdf(html, options=options)#pdfkit.from_string(html, False, options={"quiet": ""})
    if return_content:
        return pdf

    frappe.local.response.filename = invoice.voucher_no + ".pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"

    return pdf

def get_invoice_pdf(invoice, return_content=False):
    html = frappe.render_template("tourism_portal/templates/invoice.html", {"doc": invoice})
    options = {
        "quiet": "",
        "margin-left": "2mm","margin-right": "2mm",
         "--margin-left" : "2mm","--margin-right" : "2mm",
         "--margin-bottom": "10mm",
    }
    pdf = get_pdf(html, options=options)#pdfkit.from_string(html, False, options={"quiet": ""})
    if return_content:
        return pdf
    frappe.local.response.filename = invoice.voucher_no + ".pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"

    return pdf