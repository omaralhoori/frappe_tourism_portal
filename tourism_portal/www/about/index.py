import frappe
from frappe import _
from tourism_portal.utils import get_portal_setting

no_cache=1
def get_context(context):
	context.no_cache=1
	context.title = "About Us"
	context.settings = frappe.get_single("About Page Settings")
