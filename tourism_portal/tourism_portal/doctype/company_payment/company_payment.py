# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompanyPayment(Document):
	def on_submit(self):
		self.add_debit_credit()
		self.calculate_balance()
	def before_insert(self):
		self.add_debit_credit()
	def on_cancel(self):
		self.calculate_balance()
	def calculate_balance(self):
		company_balance = get_company_balance_all(self.company)
		frappe.cache().hset("company_balance",self.company, company_balance)
	def add_debit_credit(self):
		self.credit = 0
		self.debit = 0
		if self.payment_type == 'Pay' or self.payment_type == 'Reserve':
			self.credit = self.amount
		elif self.payment_type == 'Deposit' or self.payment_type == 'Refund' or self.payment_type == 'Release':
			self.debit = self.amount




def create_payment(company, amount, payment_type,currency=None, against_doctype=None, against_docname=None, remarks=''):
	balance = get_company_balance(company, update_cache=True)
	if (payment_type == 'Payment' or payment_type == 'Pay' or payment_type == 'Reserve') and balance < amount:
		frappe.throw("Insufficient Balance")
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
	return payment.name
def create_child_company_payment(company, parent_company, amount, parent_amount, payment_type,currency=None, against_doctype=None, against_docname=None, remarks=''):
	if payment_type == 'Payment' or payment_type == 'Pay':
		balance = get_child_company_balance(company, update_cache=True)
		if balance < amount:
			frappe.throw("Insufficient Balance")
	payment= frappe.get_doc({
		"doctype": "Child Company Transaction",
		"child_company": company,
		"parent_company": parent_company,
		"transaction_type": payment_type,
		"transaction_date": frappe.utils.nowdate(),
		"amount": amount,
		"parent_amount": parent_amount,
		"voucher_type": against_doctype,
		"voucher_no": against_docname,
		"remarks": remarks
	})

	payment.insert()
	payment.submit()
	if payment_type == 'Payment':
		create_payment(parent_company, amount, payment_type='Release', remarks='Release for '+company)
	return payment.name

def add_child_company_deposit(deposit, company, parent_company):
	create_payment(parent_company, deposit, payment_type='Reserve', remarks='Deposit for '+company)
	create_child_company_payment(company, parent_company, deposit,0, payment_type='Deposit')
def get_company_balance(company=None, update_cache=False):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")
	cached_balance = frappe.cache().hget("company_balance", company)
	if cached_balance and not update_cache:
		return cached_balance
	balance = get_company_balance_all(company)
	frappe.cache().hset("company_balance" , company, balance)
	return balance
	
def get_child_company_balance(company=None, update_cache=False):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")
	cached_balance = frappe.cache().hget("company_balance", company)
	if cached_balance and not update_cache:
		return cached_balance
	balance = get_child_company_balance_all(company)
	frappe.cache().hset("company_balance" , company, balance)
	return balance
	
def get_child_company_balance_all(company=None):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")
	payments = frappe.db.get_all("Child Company Transaction", {"child_company": company, "docstatus": 1}, ['amount', 'transaction_type'])
	balance = 0
	for payment in payments:
		if payment.get('transaction_type') == 'Payment' or payment.get('transaction_type') == 'Reserve':
			balance -= payment.get('amount')
		elif payment.get('transaction_type') == 'Deposit' or payment.get('transaction_type') == 'Refund':
			balance += payment.get('amount')
	return balance

def get_company_balance_all(company=None):
	if not company:
		company = frappe.db.get_value("User", frappe.session.user, "company")
	payments = frappe.db.get_all("Company Payment", {"company": company, "docstatus": 1}, ['amount', 'payment_type'])
	balance = 0
	for payment in payments:
		if payment.get('payment_type') == 'Pay' or payment.get('payment_type') == 'Reserve':
			balance -= payment.get('amount')
		elif payment.get('payment_type') == 'Deposit' or payment.get('payment_type') == 'Refund' or payment.get('payment_type') == 'Release':
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

def add_child_company_refund(refund,parent_refund, company, parent_company, voucher_type=None, voucher_no=None, remarks=''):
	create_child_company_payment(company, parent_company,refund,parent_refund, payment_type='Refund', against_docname=voucher_no, against_doctype=voucher_type, remarks=remarks)
