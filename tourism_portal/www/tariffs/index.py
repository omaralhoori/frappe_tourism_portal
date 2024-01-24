import frappe
from frappe import _
import json
from tourism_portal.api.company import get_company_details

from tourism_portal.api.reserve import get_all_invoices
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import get_company_transactions
from tourism_portal.tourism_portal.doctype.tariff.tariff import get_company_tariffs

no_cache = 1
def get_context(context):
    context.no_cache = True
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        context.tariffs = []
        return
    context.tariffs = get_company_tariffs(company_details.get('company'))
