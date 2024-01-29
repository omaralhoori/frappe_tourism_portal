import frappe
from frappe import _
from frappe.core.doctype.user.user import update_password
from tourism_portal.utils import can_update_agency

no_cache=1
def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    context.update_agency = can_update_agency()
    if context.update_agency:
        context.agency_info = get_agency_info()
        context.countries = frappe.db.get_all("Country", fields=["name", "country_name"])
        context.cities = frappe.db.get_all("City", fields=["name", "city_name", "country"])
    
    return context


def get_agency_info():
    agency = frappe.db.get_value("User", frappe.session.user, "company")
    agency_info = frappe.db.get_value("Company", agency, "*", as_dict=True)
    return agency_info

@frappe.whitelist()
def updatePassword(old_password, new_password):
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    try:
        update_password(new_password=new_password, old_password=old_password)
        return {
            "success_key": 1,
            "message": "Password updated successfully"
        }
    except:
        return {
            "success_key": 0,
            "message": "Old password is incorrect"
        }