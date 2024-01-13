import frappe
from frappe import _

no_cache=1
def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    context.include_sidebar = True
    company = frappe.db.get_value("User", frappe.session.user, "company")
    users = frappe.db.get_all("User", {"company": company}, ['name', 'full_name', 'email', ])
    context.users = users
    return context