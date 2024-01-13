import frappe
from frappe import _
from tourism_portal.api.company import get_company_details
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import get_child_company_balance, get_company_balance

no_cache=1
def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    company_details = get_company_details()
    context.from_date = frappe.form_dict.get('from_date')
    context.to_date = frappe.form_dict.get('to_date')
    if not context.from_date:
        context.from_date = frappe.utils.today()
    if not context.to_date:
        context.to_date = frappe.utils.today()
    context.include_sidebar = True
    if company_details['is_child_company']:
        context.transactions = get_child_company_transactions(company_details['child_company'],company_details['company'], context.from_date, context.to_date)
    else:
        context.transactions = get_company_transactions(company_details['company'], context.from_date, context.to_date)
    return context


def get_company_transactions(company, from_date, to_date):
    return frappe.db.sql("""
        SELECT
        name, post_date, debit, credit, remarks, (debit - credit) as balance
        FROM `tabCompany Payment`
        WHERE company = %(company)s AND docstatus = 1 AND post_date >= %(from_date)s AND post_date <= %(to_date)s
        ORDER BY post_date ASC, name asc
    """, {"company": company, "from_date": from_date, "to_date": to_date}, as_dict=True)
    


def get_child_company_transactions(company,parent_company, from_date, to_date):
    return frappe.db.sql("""
        SELECT
        name, transaction_date as post_date, debit, credit, remarks, (debit - credit) as balance
        FROM `tabChild Company Transaction`
        WHERE child_company = %(company)s AND parent_company=%(parent_company)s AND docstatus = 1 AND transaction_date >= %(from_date)s AND transaction_date <= %(to_date)s
        ORDER BY transaction_date ASC
    """, {"company": company, "parent_company":parent_company, "from_date": from_date, "to_date": to_date}, as_dict=True)
    

def calculate_company_balance(company, from_date, to_date):
    transactions = get_company_transactions(company, from_date, to_date)
    balance = 0
    for transaction in transactions:
        balance += transaction.debit - transaction.credit
    return balance