# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompanyPayment(Document):
	pass



def create_payment(company, amount, payment_type,currency=None, against_doctype=None, against_docname=None, remarks=''):
	if not currency:
		currency = frappe.db.get_single_value("Tourism Portal Settings", "selling_currency")
	payment= frappe.get_doc({
		"doctype": "Company Payment",
		"company": company,
		"payment_type": payment_type,
		"post_date": frappe.utils.nowdate(),
		"amount": amount,
		"currency": currency,
		"voucher_type": against_doctype,
		"voucher_no": against_docname,
		"remarks": remarks
	})

	payment.insert()
	payment.submit()

def get_company_balance(company=None):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")
	payments = frappe.db.get_all("Company Payment", {"company": company, "docstatus": 1}, ['amount', 'payment_type'])
	balance = 0
	for payment in payments:
		if payment.get('payment_type') == 'Pay':
			balance -= payment.get('amount')
		elif payment.get('payment_type') == 'Deposit' or payment.get('payment_type') == 'Refund':
			balance += payment.get('amount')
	return balance
	

def get_company_transactions(company=None, start=0, limit=20):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")
	return frappe.db.get_all("Company Payment", {"company": company,  "docstatus": 1}, ['name', 'amount', 'payment_type', 'remarks', 'post_date', 'voucher_no'], start=start, limit=limit, order_by='post_date desc, name desc')

def add_company_refund(refund, company=None, voucher_type=None, voucher_no=None, remarks=''):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")

	create_payment(company, refund, payment_type='Refund', against_docname=voucher_no, against_doctype=voucher_type, remarks=remarks)
