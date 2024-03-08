import frappe

@frappe.whitelist()
def get_invoice_data(invoice):
    if type(invoice) == str:
        invoice = frappe.get_doc("Sales Invoice", invoice)
    return invoice.as_dict()
    invoice_details = {
        "customer": invoice.customer,
        "posting_date": invoice.posting_date,
        "due_date": invoice.due_date,
        "grand_total": invoice.grand_total,
        "outstanding_amount": invoice.outstanding_amount,
        "currency": invoice.currency,
        "rooms": invoice.rooms,
        "transfers": invoice.transfers,
        "tours": invoice.tours,
        "other_services": invoice.other_services,
        "total_rooms": len(invoice.rooms),
        "total_transfers": len(invoice.transfers),
        "total_tours": len(invoice.tours),
        "total_other_services": len(invoice.other_services),
        "total_services": len(invoice.rooms) + len(invoice.transfers) + len(invoice.tours) + len(invoice.other_services),
        "total_services_amount": sum([i.amount for i in invoice.rooms] + [i.amount for i in invoice.transfers] + [i.amount for i in invoice.tours] + [i.amount for i in invoice.other_services])
    }
    return invoice_details