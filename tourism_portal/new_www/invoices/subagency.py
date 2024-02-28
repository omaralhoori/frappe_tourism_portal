import frappe
from frappe import _
import json

from tourism_portal.api.reserve import get_all_invoices, get_all_invoices_subagency, get_bookings_detials

no_cache = 1
def get_context(context):
    context.no_cache = True
    context.title = 'My Bookings'
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    page_size = 20
    page = frappe.form_dict.page or 1
    start = (int(page) - 1) * page_size
    voucher_no = frappe.form_dict.voucher_no
    booking_details = get_bookings_detials(voucher_no=voucher_no or '')
    context.booking_details = booking_details['subagency_bookings']
    context.subagency_bookings = booking_details['subagency_bookings']
    context.pages = int(context.booking_details.get('bookings')/ page_size) + 1
    context.current_page = int(page)
    context.subagency_page = True
    
    context.invoices = get_all_invoices_subagency(voucher_no=voucher_no, start=start, limit=page_size)
