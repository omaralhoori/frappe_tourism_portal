import frappe

@frappe.whitelist()
def get_invoice_data_2(invoice):
    if type(invoice) == str:
        invoice = frappe.get_doc("Sales Invoice", invoice)
    return invoice.as_dict()

@frappe.whitelist()
def get_invoice_data(invoice):
    invoice = frappe.get_doc("Sales Invoice", invoice)
    invoice_details = {
        **get_invoice_details(invoice),
    }
    return invoice_details

def get_invoice_details(invoice):
    invoice_details = {
        "id": invoice.name, 
        "turop": frappe.db.get_value("Company",invoice.company, "system_code", cache=True), # Turop - Get from company
        "invoice_no": invoice.invoice_no, 
        "voucher": invoice.voucher_no.split("-")[-1], # Voucher - Split and get last number
        "post_date": invoice.post_date, # AcTarihi, UpdTarihi
        "post_time": invoice.post_time,
        "invoice_check_out": invoice.invoice_check_out,
        "status": invoice.status,
        "transfer_total": invoice.transfer_fees_company,
        "tour_total": invoice.tour_fees_company,
        "hotel_total": invoice.hotel_fees_company,
        "grand_total": invoice.grand_total_company,
    }
    return invoice_details

def get_customer_details(invoice):
    customers = {} 

# def get_hotel_details(invoice):
#     hotels = {}
#     main_count = 0
#     for 