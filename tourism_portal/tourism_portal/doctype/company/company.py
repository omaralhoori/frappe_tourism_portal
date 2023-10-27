# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.password import update_password

class Company(Document):
	
	@frappe.whitelist()
	def get_company_balance(self):
		payments = frappe.db.get_all("Company Payment", {"company": self.name, "docstatus": 1}, ['amount', 'payment_type'])
		balance = 0
		for payment in payments:
			if payment.get('payment_type') == 'Pay':
				balance -= payment.get('amount')
			elif payment.get('payment_type') == 'Deposit':
				balance += payment.get('amount')
		return balance
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
