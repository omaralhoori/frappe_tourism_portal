# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
class SalesInvoice(Document):
	def after_insert(self):
		session_expires_in = frappe.db.get_single_value("Tourism Portal Settings", "session_expires_in")
		session_expires = frappe.utils.now_datetime()+frappe.utils.datetime.timedelta(seconds=int(session_expires_in))
		self.db_set('session_expires',session_expires)



def create_reservation():
	pass