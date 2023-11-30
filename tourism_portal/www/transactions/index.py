import frappe
from frappe import _
import json

from tourism_portal.api.reserve import get_all_invoices
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import get_company_transactions

no_cache = 1
def get_context(context):
    context.no_cache = True
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    page = frappe.form_dict.page or 1
    start = (int(page) - 1) * 20
    context.transactions = get_company_transactions(start=start)
