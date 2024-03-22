

import frappe
from frappe import _
from tourism_portal.utils import get_portal_setting

no_cache=1
def get_context(context):
	context.no_cache=1
	if frappe.session.user != 'Guest':
		frappe.local.flags.redirect_location = '/home'
		raise frappe.Redirect
	
	context.title = "Home"
	context.settings = frappe.get_single("Tourism Website Settings")


@frappe.whitelist(allow_guest=True)
def submit_contact_form(
		contact_name,
		contact_email,
		contact_subject,
		contact_message):
	frappe.get_doc({
		"doctype": "Website Contact Messages",
		"contact_name": contact_name,
		"contact_email": contact_email,
		"contact_subject": contact_subject,
		"contact_message": contact_message
	}).insert(ignore_permissions=True)
	return True