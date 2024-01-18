import frappe
from frappe import _
import json

from tourism_portal.api.reserve import get_invoice_data
from tourism_portal.utils import get_portal_setting

no_cache = 1
def get_context(context):
    context.no_cache = True
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    invoice = frappe.form_dict.invoice
    context.invoice_details = get_invoice_data(invoice)


    context.nationalities = frappe.db.get_all("Nationality")
    context.max_rooms = get_portal_setting("max_hotel_rooms_selected")
    context.max_room_adults = get_portal_setting("max_adults_per_room")
    context.max_room_children = get_portal_setting("max_children_per_room")

    context.max_adults_per_transfer = get_portal_setting("max_adults_per_transfer")
    context.max_children_per_transfer = get_portal_setting("max_children_per_transfer")
    context.max_adults_per_tour = get_portal_setting("max_adults_per_tour")
    context.max_children_per_tour = get_portal_setting("max_children_per_tour")
    context.max_child_age = get_portal_setting("max_child_age")