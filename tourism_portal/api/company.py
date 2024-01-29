import frappe
from frappe import _
import json
from tourism_portal.tourism_portal.doctype.company.company import get_account_settings

from tourism_portal.tourism_portal.doctype.company_payment.company_payment import add_child_company_deposit, get_child_company_balance, get_company_balance, get_company_transactions
from tourism_portal.utils import can_update_agency, get_utils_company_details


@frappe.whitelist()
def get_customer_balance():
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        balance = get_child_company_balance(company=company_details.get('child_company'))
    else:
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

@frappe.whitelist()
def get_company_details():
    return get_utils_company_details()

@frappe.whitelist()
def create_agency():
    if frappe.has_permission("Company", "create") == False:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_data = frappe.form_dict.agency_data
    if type(agency_data) == str:
        agency_data = json.loads(agency_data)
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency = frappe.new_doc("Company")
    agency.company_name = agency_data.get('agency_name')
    # agency.company_code = agency_data.get('agency_code')
    agency.is_child_company = 1
    agency.parent_company = company_details['company']
    agency.country = frappe.db.get_value("Company", company_details['company'], "country")
    agency.account_type = "Debit"
    agency.save()
    agency.add_user(agency_data.get('email'), agency_data.get('password'), agency_data.get('fullname'))
    return "success"

@frappe.whitelist()
def add_agency_money():
    amount = float(frappe.form_dict.amount)
    agency = frappe.form_dict.agency
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_doc = frappe.get_doc("Company", agency)
    if not agency_doc.is_child_company or agency_doc.parent_company != company_details['company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    company_balance = get_company_balance()
    if company_balance < amount:
        frappe.throw(_("You don't have enough balance to transfer."), frappe.ValidationError)
    add_child_company_deposit(amount, agency, company_details['company'])
    return "success"

# "args": {
#     "hotel_profit": hotelProfit,
#     "transfer_profit": transferProfit,
#     "tour_profit": tourProfit,
#     "agency": agency
# },
@frappe.whitelist()
def update_agency_profit():
    hotel_profit = frappe.form_dict.hotel_profit
    transfer_profit = frappe.form_dict.transfer_profit
    tour_profit = frappe.form_dict.tour_profit
    agency = frappe.form_dict.agency
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_doc = frappe.get_doc("Company", agency)
    if not agency_doc.is_child_company or agency_doc.parent_company != company_details['company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_doc.hotel_margin = hotel_profit
    agency_doc.transfer_margin = transfer_profit
    agency_doc.tour_margin = tour_profit
    agency_doc.save()
    return "success"

@frappe.whitelist()
def disable_agency(agency_id):
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_doc = frappe.get_doc("Company", agency_id)
    if not agency_doc.is_child_company or agency_doc.parent_company != company_details['company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_doc.disabled = 1
    agency_doc.save()
    frappe.db.set_value("User", {"company": agency_id}, "enabled", 0)
    return "success"

@frappe.whitelist()
def enable_agency(agency_id):
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_doc = frappe.get_doc("Company", agency_id)
    if not agency_doc.is_child_company or agency_doc.parent_company != company_details['company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_doc.disabled = 0
    agency_doc.save()
    frappe.db.set_value("User", {"company": agency_id}, "enabled", 1)
    return "success"

@frappe.whitelist()
def disable_user(user):
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)

    frappe.db.set_value("User", {"company": company_details['company'], "name": user}, "enabled", 0)
    return "success"

@frappe.whitelist()
def enable_user(user):
    company_details = get_company_details()
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)

    frappe.db.set_value("User", {"company": company_details['company'], "name": user}, "enabled", 1)
    return "success"


@frappe.whitelist()
def update_agency_info():
    if not can_update_agency():
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    agency_info = frappe.form_dict.agency_info
    if type(agency_info) == str:
        agency_info = json.loads(agency_info)
    company = frappe.db.get_value("User", frappe.session.user, "company")
    agency = frappe.get_doc("Company",company)
    agency.update(agency_info)
    agency.save()
    return "success"