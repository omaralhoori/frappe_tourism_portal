import json
import frappe
from frappe import _

"""
rooms -> [{
    room_name,
	room_id,
	contract_id-> nullable,
	price_id -> nullable,
	inquiry_id -> nullable,
	pax_info -> {
		adults: num,
		children: num,
		childrenInfo: [num]
	},
	price:
}]
"""

@frappe.whitelist()
def create_reservation():
    params = frappe.form_dict
    user = frappe.session.user
    company = frappe.db.get_value("User", user, "company")
    invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "company": company,
        "customer": user,
        "post_date": frappe.utils.nowdate(),
        "post_time": frappe.utils.nowtime()
    })
    if type(params.rooms) == str:
        rooms = json.loads(params.rooms)
    else:
        rooms = params.rooms
    for searchName in rooms:
        search = rooms[searchName]
        for roomName in search:
            room = rooms[searchName][roomName]
            invc_room = invoice.append("rooms")
            invc_room.room = room['room_id']
            invc_room.hotel_search = searchName
            invc_room.room_name = roomName#room['room_name']
            invc_room.nationality = room.get('nationality')
            invc_room.check_in = room.get('check_in')
            invc_room.check_out = room.get('check_out')
            total_price = 0
            for i in range(int(room['pax_info'].get('adults'))):
                guest = invoice.append("room_pax_info")
                guest.room_name = roomName#room['room_name']
                guest.hotel_search = searchName
                guest.guest_type = 'Adult'
            for child_age in room['pax_info'].get('childrenInfo'):
                guest = invoice.append("room_pax_info")
                guest.guest_type = 'Child'
                guest.hotel_search = searchName
                guest.room_name = roomName#room['room_name']
                guest.guest_age = int(child_age)
            for contract in room['contracts']:
                room_price = invoice.append('room_price')
                room_price.room_name=  roomName
                room_price.hotel_search = searchName
                room_price.check_in = contract['check_in']
                room_price.check_out = contract['check_out']
                room_price.nights = frappe.utils.date_diff(room_price.check_out, room_price.check_in)
                room_price.selling_price = float(contract['price']) / room_price.nights
                room_price.total_selling_price = float(contract['price'])
                total_price += float(contract['price'])
                room_price.contract_id = contract.get('contract_id')
                room_price.contract_price = contract.get('price_id')
                room_price.inquiry_id = contract.get('inquiry_id')
                if room_price.contract_price:
                    room_price.buying_currency,room_price.buying_price = frappe.db.get_value("Hotel Room Price", room_price.contract_price,["buying_currency", "buying_price"])
                elif room_price.inquiry_id:
                    room_price.buying_currency,room_price.buying_price = frappe.db.get_value("Hotel Inquiry Request", room_price.inquiry_id,["buying_currency", "buying_price"])
                if room_price.contract_id:
                    room_price.cancellation_policy = frappe.db.get_value("Hotel Room Contract",room_price.contract_id, "cancellation_policy" )
                if not room_price.cancellation_policy:
                    hotel = frappe.db.get_value("Hotel Room",  room['room_id'], "hotel", cache=True)
                    room_price.cancellation_policy = frappe.db.get_value("Hotel", hotel, "hotel_cancellation_policy")
            invc_room.total_price = total_price
    invoice.insert(ignore_permissions=True)
    return invoice.name

@frappe.whitelist()
def get_invoice_data(sales_invoice):
    company = frappe.db.get_value("User", frappe.session.user, "company")
    invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company})
    rooms = {}
    for room in invoice.rooms:
        if not rooms.get(room.get('hotel_search')):
            rooms[room.get('hotel_search')] = {}
        if not rooms[room.get('hotel_search')].get(room.get('hotel')):
            # ToDo make for multiple hotels get check in and check out for every different rooms and get room names 
            rooms[room.get('hotel_search')][room.get('hotel')] = {}
            rooms[room.get('hotel_search')][room.get('hotel')]['rooms'] = []
            rooms[room.get('hotel_search')][room.get('hotel')]['details'] = frappe.db.get_value("Hotel", room.get('hotel'), ["hotel_name", "hotel_image", "hotel_cancellation_policy"], as_dict=True)
            rooms[room.get('hotel_search')][room.get('hotel')]['details']['policy_description'] = frappe.db.get_value("Cancellation Policy",rooms[room.get('hotel_search')][room.get('hotel')]['details']['hotel_cancellation_policy'] ,'policy_description')
            rooms[room.get('hotel_search')][room.get('hotel')]['booking_details'] = {
                "check_in": room.get('check_in'),
                "nationality": room.get('nationality'),
                "check_out": room.get('check_out'),
            }
        room_type, room_acmnd_type = frappe.db.get_value("Hotel Room", room.room, ['room_type', 'room_accommodation_type'])
        room_type = frappe.db.get_value("Room Type", room_type, 'room_type', cache=True)
        room_acmnd_type = frappe.db.get_value("Room Accommodation Type", room_acmnd_type, 'accommodation_type_name', cache=True)
        hotel_room = {
            "room_name": room.room_name,
            "row_id": room.name,
            "total_price": room.total_price,
            "hotel": room.hotel,
            "accommodation_type": room_acmnd_type,
            "room_type": room_type,
        }
        adult_paxes = []
        child_paxes = []
        for pax in invoice.room_pax_info:
            if pax.room_name == room.room_name:
                if pax.guest_type == 'Adult':
                    adult_paxes.append({
                        "row_id": pax.name,
                        "guest_salutation": pax.guest_salutation,
                        "guest_name": pax.guest_name,
                        "guest_type": pax.guest_type,
                        "guest_age": pax.guest_age
                    })
                if pax.guest_type == 'Child':
                    child_paxes.append({
                        "row_id": pax.name,
                        "guest_name": pax.guest_name,
                        "guest_type": pax.guest_type,
                        "guest_age": pax.guest_age
                    })
        extras = []
        for extra in invoice.room_extras:
            if extra.room_name == room.room_name and extra.hotel_search == room.hotel_search:
                extras.append({
                    "service": extra.extra,
                    "extra_price": extra.extra_price,
                })

        hotel_room['adult_paxes'] = adult_paxes
        hotel_room['child_paxes'] = child_paxes
        hotel_room['extras'] = extras
        rooms[room.get('hotel_search')][room.get('hotel')]['rooms'].append(hotel_room)
    return {
        "invoice_id": invoice.name,
        "session_expires": invoice.session_expires,
        "post_date": invoice.post_date,
        "post_time": invoice.post_time,
        "hotel_fees": invoice.hotel_fees,
        "grand_total": invoice.grand_total,
        "rooms": rooms,
        "docstatus": invoice.docstatus,
        "sales_invoice": sales_invoice, 
        "customer_name": invoice.customer_name,
        "customer_email": invoice.customer_email,
        "customer_mobile_no": invoice.customer_mobile_no
    }


@frappe.whitelist()
def get_all_invoices(start=0, limit=20):
    company = frappe.db.get_value("User", frappe.session.user, "company")
    return frappe.db.get_all("Sales Invoice", {"company": company}, [
        "name", "grand_total", "post_date", "status",
          "post_time", "session_expires", "docstatus"], order_by="creation DESC" ,limit=limit, start=start)


@frappe.whitelist()
def complete_reservation():
    invoice = frappe.get_doc("Sales Invoice", {"name": frappe.form_dict.sales_invoice, "customer": frappe.session.user})
    rooms = json.loads(frappe.form_dict.rooms)
    invoice.room_extras = []
    for roomRowId in rooms:
        extras = rooms[roomRowId].pop('extras')
        for paxRowId in rooms[roomRowId]:
            for pax in invoice.room_pax_info:
                if pax.name == paxRowId:
                    pax.guest_salutation = rooms[roomRowId][paxRowId]['salut']
                    pax.guest_name = rooms[roomRowId][paxRowId]['guest_name']
        for extra in extras:
            extra_row = invoice.append('room_extras')
            extra_row.extra = extra['extra']
            extra_row.room_name = extra['room_name']
            extra_row.extra_price = float(extra['extra_price'])
            extra_row.room_row_id = roomRowId
            # ToDo make extra for amount and percentage
    invoice.customer_name = frappe.form_dict.customer_name
    invoice.customer_email = frappe.form_dict.customer_email
    invoice.customer_mobile_no = frappe.form_dict.customer_mobile_no
    invoice.save(ignore_permissions=True)
    invoice.submit()
    return {"success_key": 1, "message": ""}


@frappe.whitelist()
def cancel_reservation(invoice_id):
    company = frappe.db.get_value("User", frappe.session.user, "company")
    invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company})
    invoice.cancel_invoice()
    invoice.save(ignore_permissions=True)
    return {"success_key": 1}


@frappe.whitelist()
def add_nights_to_room(sales_invoice, row_id, check_in=None, check_out=None):
    if not check_in and not check_out:
        frappe.throw("Please Select new Check-in or new Check-out")
    company = frappe.db.get_value("User", frappe.session.user, "company")
    invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company})
    invoice.add_nights(row_id, check_in, check_out)