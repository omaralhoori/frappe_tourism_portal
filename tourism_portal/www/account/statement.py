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
        pmnt.name, pmnt.post_date, pmnt.debit, pmnt.credit, pmnt.remarks, (pmnt.debit - pmnt.credit) as balance, si.voucher_no, si.name as invoice_name
        FROM `tabCompany Payment` as pmnt
        LEFT JOIN `tabSales Invoice` as si ON si.name = pmnt.voucher_no
        WHERE 
            pmnt.company = %(company)s AND pmnt.docstatus = 1 
            AND pmnt.post_date >= %(from_date)s AND pmnt.post_date <= %(to_date)s
            AND pmnt.payment_type NOT IN ('Release', 'Reserve')
        ORDER BY pmnt.post_date ASC, pmnt.name asc
    """, {"company": company, "from_date": from_date, "to_date": to_date}, as_dict=True)
    


def get_child_company_transactions(company,parent_company, from_date, to_date):
    return frappe.db.sql("""
        SELECT
        pmnt.name, pmnt.transaction_date as post_date, pmnt.debit, pmnt.credit, pmnt.remarks, (pmnt.debit - pmnt.credit) as balance,  si.voucher_no, si.name as invoice_name
        FROM `tabChild Company Transaction` as pmnt
        LEFT JOIN `tabSales Invoice` as si ON si.name = pmnt.voucher_no
        WHERE pmnt.child_company = %(company)s AND pmnt.parent_company=%(parent_company)s AND pmnt.docstatus = 1 AND pmnt.transaction_date >= %(from_date)s AND pmnt.transaction_date <= %(to_date)s
        ORDER BY pmnt.transaction_date ASC, pmnt.creation asc
    """, {"company": company, "parent_company":parent_company, "from_date": from_date, "to_date": to_date}, as_dict=True)
    

def calculate_company_balance(company, from_date, to_date):
    transactions = get_company_transactions(company, from_date, to_date)
    balance = 0
    for transaction in transactions:
        balance += transaction.debit - transaction.credit
    return balance