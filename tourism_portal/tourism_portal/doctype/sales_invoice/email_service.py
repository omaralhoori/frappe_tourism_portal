from tourism_portal.utils import get_location_full_name
import frappe
from tourism_portal.pdf import get_invoice_pdf, get_voucher_pdf


def send_agency_invoice_email(invoice):
    company = frappe.get_doc("Company", invoice.company)
    if not company.accounting_email:
        return
    # frappe.throw("Please enter accounting email in company")
    invoice_pdf = get_invoice_pdf(invoice, return_content=True)
    frappe.sendmail(
    recipients=[company.accounting_email],
    doctype="Sales Invoice",
    name=invoice.name,
    message="New Sales Invoice has been created",
    subject="Sales Invoice: " + invoice.invoice_no,
    attachments=[{"fname": invoice.invoice_no + ".pdf", "fcontent": invoice_pdf}],
    now=1,
    )

def send_agency_voucher_email(invoice):
    company = frappe.get_doc("Company", invoice.company)
    if not company.reservation_email:
        return
    # frappe.throw("Please enter accounting email in company")
    invoice_pdf = get_voucher_pdf(invoice, return_content=True)
    frappe.sendmail(
    recipients=[company.reservation_email],
    doctype="Sales Invoice",
    name=invoice.name,
    message="New Voucher has been created",
    subject="Reservation Voucher: " + invoice.voucher_no,
    attachments=[{"fname": invoice.voucher_no + ".pdf", "fcontent": invoice_pdf}],
    now=1,
    )


def check_flight_entered():
    if not frappe.db.get_single_value("Tourism Portal Settings", "enable_flight_notification"):
        return
    check_datetime = frappe.utils.add_days(frappe.utils.nowdate(), 1)
    invoices = frappe.db.sql("""
        SELECT 
            siti.name ,siti.parent as invoice, siti.flight_no, siti.transfer_date, 
            siti.pick_up as pickup, siti.drop_off as dropoff,
            siti.pick_up_type as pickup_type, siti.drop_off_type as dropoff_type
         FROM `tabSales Invoice Transfer Item` as siti 
                  WHERE transfer_date = %(transfer_date)s 
                  AND (pick_up_type = 'airport' OR drop_off_type = 'airport')
""", {"transfer_date": check_datetime}, as_dict=True)
    for invoice in invoices:
        if frappe.db.exists("Transfer Flight Notification", {"sales_invoice": invoice.invoice, "row_id": invoice.name}):
            continue
        drop_off = get_location_full_name(invoice.dropoff, invoice.dropoff_type)
        pick_up = get_location_full_name(invoice.pickup, invoice.pickup_type)
        frappe.get_doc({
            "row_id": invoice.name,
            "sales_invoice": invoice.invoice,
            "doctype": "Transfer Flight Notification",
            "invoice": invoice.invoice,
            "flight_no": invoice.flight_no,
            "transfer_date": invoice.transfer_date,
            "dropoff": drop_off,
            "pickup": pick_up
        }).insert(ignore_permissions=True)

def notifiy_flight_changed(invoice, transfer_row):
    send_mail = frappe.db.get_single_value("Portal Notification Settings", "on_flight_update_email")
    if not send_mail:
        return
    opertaion_email = frappe.db.get_single_value("Portal Notification Settings", "operation_email")
    pick_up = get_location_full_name(transfer_row.pick_up, transfer_row.pick_up_type)
    drop_off = get_location_full_name(transfer_row.drop_off, transfer_row.drop_off_type)
    msg = "Voucher No: "+ invoice.voucher_no + "\n"
    msg += "Flight no has been updated to " + transfer_row.flight_no + " For transfer from " + pick_up + " to " + drop_off
    frappe.sendmail(
    recipients=[opertaion_email],
    doctype="Sales Invoice",
    name=invoice.name,
    message= msg,
    subject="Voucher: " + invoice.voucher_no + ", Flight No Changed",
    now=1,
    )