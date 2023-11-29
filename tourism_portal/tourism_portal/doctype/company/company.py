# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.password import update_password
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import get_company_balance

class Company(Document):
	def before_save(self):
		self.credit_current_limit = self.credit_limit - self.credit
	@frappe.whitelist()
	def get_company_balance(self):
		return get_company_balance(self.name)
	@frappe.whitelist()
	def add_user(self, email, password, first_name, last_name=None):
		if frappe.db.exists("User", {"email": email}):
			frappe.throw("User already exists")
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"last_name": last_name,
			"company": self.name
		})
		user.insert()
		update_password(user=user.name, pwd=password)


def get_account_settings(company=None):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")

	account_details = frappe.db.get_value("Company", company, ["account_type", "credit_limit", "credit_current_limit", "credit"], as_dict=True)
	return account_details or {}