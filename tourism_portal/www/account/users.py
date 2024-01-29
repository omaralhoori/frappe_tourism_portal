import frappe
from frappe import _
from tourism_portal.utils import can_add_user

no_cache=1
def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    if not can_add_user():
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    company = frappe.db.get_value("User", frappe.session.user, "company")
    users = frappe.db.get_all("User", {"company": company}, ['name', 'full_name', 'email', 'enabled'])
    context.users = users
    return context