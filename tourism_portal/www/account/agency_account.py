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
    if company_details['is_child_company']:
        frappe.throw(_("You are not allowed to access this page."), frappe.PermissionError)
    context.from_date = frappe.form_dict.get('from_date')
    context.to_date = frappe.form_dict.get('to_date')
    context.company = frappe.form_dict.get('company') or ''
    context.agencies = frappe.db.get_all("Company", {"is_child_company": 1, "parent_company": company_details.get('company')}, ['name', 'company_name', 'company_code'])
    if not context.from_date:
        context.from_date = frappe.utils.today()
    if not context.to_date:
        context.to_date = frappe.utils.today()
    context.include_sidebar = True
    context.transactions = get_child_company_transactions(context.company, company_details['company'], context.from_date, context.to_date)
    
    return context



def get_child_company_transactions(company,parent_company, from_date, to_date):
    if company == '':
        return []
    return frappe.db.sql("""
        SELECT
        name, transaction_date as post_date, debit, credit, remarks, (debit - credit) as balance
        FROM `tabChild Company Transaction`
        WHERE child_company = %(company)s AND parent_company=%(parent_company)s AND docstatus = 1 AND transaction_date >= %(from_date)s AND transaction_date <= %(to_date)s
        ORDER BY transaction_date ASC
    """, {"company": company, "parent_company":parent_company, "from_date": from_date, "to_date": to_date}, as_dict=True)
    
