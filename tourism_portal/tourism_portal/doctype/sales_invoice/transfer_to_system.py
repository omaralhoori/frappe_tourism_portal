import frappe

@frappe.whitelist()
def get_invoice_data_2(invoice):
    if type(invoice) == str:
        invoice = frappe.get_doc("Sales Invoice", invoice)
    return invoice.as_dict()

@frappe.whitelist()
def get_pending_invoices():
    frappe.only_for('Maintenance User')
    pending_invoices = frappe.db.get_value("Sales Invoice", {"main_system_transferred": 0, "main_system_error": 0}, "name")
    if pending_invoices:
        return get_invoice_data(pending_invoices)
    return

@frappe.whitelist()
def mark_completed_invoices(invoice, status):
    frappe.only_for('Maintenance User')
    values = {"main_system_transferred": 1, "main_system_error": 0}
    if not status or int(status) == 0:
        values =  {"main_system_transferred": 0, "main_system_error": 1}
    frappe.db.set_value("Sales Invoice", invoice, values)
def get_invoice_data(invoice):
    #frappe.only_for('System Manager')
    invoice = frappe.get_doc("Sales Invoice", invoice)
    invoice_details = {
        **get_invoice_details(invoice),
        "reservations": get_reservations(invoice),
        "customers": get_customer_details(invoice)
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

def get_reservations(invoice):
    reservations = []
    reservations = get_hotel_reservations(invoice) 
    return reservations

def get_hotel_reservations(invoice):
    hotel_reservations = []
    for room in invoice.rooms:
        room_type, room_acmnd = frappe.db.get_value("Hotel Room", room.room, ["room_type", "room_accommodation_type"])
        room_type = frappe.db.get_value("Room Type", room_type, "system_code", cache=True)
        room_acmnd = frappe.db.get_value("Room Accommodation Type", room_acmnd, "system_code", cache=True)
        area = frappe.db.get_value("Hotel", room.hotel, "area", cache=True)
        area = frappe.db.get_value("Area", area, "system_code", cache=True)
        board = frappe.db.get_value("Hotel Boarding Type", room.board, "system_code", cache=True)
        bed_type = frappe.db.get_value("Room Bed Type", room.bed_type, "system_code", cache=True)
        res = {
            "hotel": frappe.db.get_value("Hotel", room.hotel, "system_code", cache=True),
            "room": room.room,
            "room_type": room_type,
            "room_acmnd": room_acmnd,
            "area": area,
            "check_in": format_date(room.check_in),
            "check_out": format_date(room.check_out),
            "board": board,
            "bed_type": bed_type,
            "hotel_search": room.hotel_search,
            "room_name": room.room_name,
            **get_selling_buying_prices(invoice, room.hotel_search, room.room_name)
        }
        hotel_reservations.append(res)
    return hotel_reservations


def get_selling_buying_prices(invoice, hotel_search, room_name):
    total_selling_price = 0
    total_nights = 0
    total_buying_price = 0
    selling_currency = 'USD'
    buying_currency = None
    for room_price in invoice.room_price:
        total_selling_price += room_price.selling_price_company * room_price.nights
        total_nights += room_price.nights
        total_buying_price += room_price.buying_price * room_price.nights
        buying_currency = room_price.buying_currency
    return {
        "nights": total_nights,
        "selling_price": total_selling_price / total_nights,
        "buying_price": total_buying_price / total_nights,
        "buying_currency": buying_currency,
        "selling_currency": selling_currency
    }

def get_customer_details(invoice):
    customers_names = []
    customers = {}
    hotel_search = None
    for pax in invoice.room_pax_info:
        if not hotel_search:
            hotel_search = pax.hotel_search
        pax_name = pax.guest_salutation + "-" +pax.guest_type + "-" + pax.guest_name + "-" + str(pax.guest_age)
        if not customers.get(pax_name):
            customers[pax_name] = {
                "guest_title": pax.guest_salutation,
                "guest_name": pax.guest_name,
                "guest_type": pax.guest_type,
                "guest_age": pax.guest_age,
                "mobile_no": pax.mobile_no,
                "rooms": [{
                    "hotel_search": pax.hotel_search,
                    "room_name": pax.room_name,
                }],
                'transfers': [],
                'tours': []
            }
        else:
            customers[pax_name]['rooms'].append({
                    "hotel_search": pax.hotel_search,
                    "room_name": pax.room_name,
                })
    for pax in invoice.transfer_pax_info:
        pax_name = pax.guest_salutation + "-" +pax.guest_type + "-" + pax.guest_name + "-" + str(pax.guest_age)
        if not customers.get(pax_name):
            customers[pax_name] = {
                "guest_title": pax.guest_salutation,
                "guest_name": pax.guest_name,
                "guest_type": pax.guest_type,
                "guest_age": pax.guest_age,
                "mobile_no": pax.mobile_no,
                "transfers": [{
                    "transfer_search": pax.transfer_search,
                    "transfer_name": pax.transfer_name,
                }],
                'rooms': [],
                'tours': []
            }
        else:
            if not customers[pax_name].get('transfers'):
                customers[pax_name]['transfers'] = []
            customers[pax_name]['transfers'].append({
                    "transfer_search": pax.transfer_search,
                    "transfer_name": pax.transfer_name,
                })
    for pax in invoice.tour_pax_info:
        pax_name = pax.guest_salutation + "-" +pax.guest_type + "-" + pax.guest_name + "-" + str(pax.guest_age)
        if not customers.get(pax_name):
            customers[pax_name] = {
                "guest_title": pax.guest_salutation,
                "guest_name": pax.guest_name,
                "guest_type": pax.guest_type,
                "guest_age": pax.guest_age,
                "mobile_no": pax.mobile_no,
                "tours": [{
                    "tour_search": pax.search_name,
                }],
                'rooms': [],
                'transfers': []
            }
        else:
            if not customers[pax_name].get('tours'):
                customers[pax_name]['tours'] = []
            customers[pax_name]['tours'].append({
                    "tour_search": pax.search_name,
                })
        # if pax_name in customers_names:
        #     if pax.hotel_search != hotel_search:
        #         continue
        #         # ToDo: add hotel details to customer
        #     else:
        #         customers[pax_name]
        

    return customers

# def get_hotel_details(invoice):
#     hotels = {}
#     main_count = 0
#     for 

import datetime
def format_date(date_str):
    if type(date_str) == datetime.date:
        date_str = date_str.strftime("%Y-%m-%d")
        return date_str
    # Parse the date string using strptime and assuming day, month, year order
    date_obj = datetime.datetime.strptime(date_str, "%d-%m-%Y")

    # Format the date object in the new format (YYYY-MM-DD)
    new_date_str = date_obj.strftime("%Y-%m-%d")

    return new_date_str