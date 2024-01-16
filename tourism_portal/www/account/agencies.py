import frappe
from frappe import _
from tourism_portal.api.company import get_company_details
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import get_child_company_balance, get_company_balance

no_cache=1
def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    context.include_sidebar = True
    agencies = frappe.db.sql("""
    SELECT 
    name, company_code as agency_code, 
    company_name as agency_name,
    hotel_margin, transfer_margin, tour_margin, disabled
    FROM `tabCompany`
    WHERE is_child_company = 1 AND parent_company = %(parent_company)s
""", {"parent_company": company_details['company']}, as_dict=True)
    for agency in agencies:
        agency['agency_balance'] = get_child_company_balance(agency.name)
        agency['user'] = frappe.db.get_value("User", {"company": agency.name}, ['name'])
    context.agencies = agencies
    context.company_balance = get_company_balance()
    return context
