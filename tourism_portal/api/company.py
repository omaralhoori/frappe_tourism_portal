import frappe
from frappe import _
import json
from tourism_portal.tourism_portal.doctype.company.company import get_account_settings

from tourism_portal.tourism_portal.doctype.company_payment.company_payment import get_company_balance, get_company_transactions


@frappe.whitelist()
def get_customer_balance():
    balance = get_company_balance()
    return balance

@frappe.whitelist()
def get_company_account_settings():
    return get_account_settings()

@frappe.whitelist()
def get_account_balance_details():
    return {
        "balance": get_customer_balance(),
        "account": get_company_account_settings()
    }

@frappe.whitelist()
def get_account_transactions(start=0, limit=20):
    return get_company_transactions(start=start, limit=limit)