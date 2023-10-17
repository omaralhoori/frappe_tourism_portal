import frappe
from frappe import _
from tourism_portal.utils import get_portal_setting
import json
def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("Log in to access this page."), frappe.PermissionError)
	params = frappe.form_dict.params
	params = json.loads(params)
	print(params)
	return context