# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomerInvoiceEditRequest(Document):
	def after_insert(self):
		invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
		invoice.notifiy_invoice_edit(self.subject, self.request)
