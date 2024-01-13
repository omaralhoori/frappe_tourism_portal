# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import get_child_company_balance_all

class ChildCompanyTransaction(Document):
	def on_submit(self):
		self.add_debit_credit()
		self.calculate_balance()
	def on_cancel(self):
		self.calculate_balance()
	def calculate_balance(self):
		company_balance = get_child_company_balance_all(self.child_company)
		frappe.cache().hset("company_balance",self.child_company, company_balance)

	def before_insert(self):
		self.add_debit_credit()

	def add_debit_credit(self):
		self.credit = 0
		self.debit = 0
		if self.transaction_type == 'Payment' or self.transaction_type == 'Reserve':
			self.credit = self.amount
		elif self.transaction_type == 'Deposit' or self.transaction_type == 'Refund' or self.transaction_type == 'Release':
			self.debit = self.amount

