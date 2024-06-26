import json
from tourism_portal.utils import get_location_full_name
import frappe
from frappe import _
from tourism_portal.api.company import get_company_details
from tourism_portal.tourism_portal.doctype.sales_invoice.reserve import add_rooms_to_invoice, add_tours_to_invoice, add_transfers_to_invoice

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
    company_details = get_company_details()#frappe.db.get_value("User", user, "company")
    hotel_margin, transfer_margin, tour_margin = 0, 0, 0
    if company_details.get('is_child_company'):
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": company_details.get('company'),
            "child_company": company_details.get('child_company'),
            "customer": user,
            "post_date": frappe.utils.nowdate(),
            "post_time": frappe.utils.nowtime()
        })
        hotel_margin, transfer_margin, tour_margin = frappe.db.get_value("Company", company_details.get('child_company'), ['hotel_margin', 'transfer_margin', 'tour_margin'])
    else:
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": company_details.get('company'),
            "customer": user,
            "post_date": frappe.utils.nowdate(),
            "post_time": frappe.utils.nowtime()
        })
    if type(params.rooms) == str:
        rooms = json.loads(params.rooms)
    else:
        rooms = params.rooms
    if type(params.transfers) == str:
        transfers = json.loads(params.transfers)
    else:
        transfers = params.transfers
    if type(params.tours) == str:
        tours = json.loads(params.tours)
    else:
        tours = params.tours
    add_rooms_to_invoice(invoice, rooms, hotel_margin)
    add_transfers_to_invoice(invoice, transfers, transfer_margin)
    add_tours_to_invoice(invoice, tours, tour_margin)
    
    invoice.insert(ignore_permissions=True)
    return invoice.name



@frappe.whitelist()
def get_invoice_data(sales_invoice):
    company_details = get_company_details()#frappe.db.get_value("User", frappe.session.user, "company")
    if company_details.get('is_child_company'):
        invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company_details.get('company')})
    if invoice.status == "Cancelled":
        #frappe.throw("This invoice has been cancelled!")
        return {
        "invoice_id": invoice.name,
        "session_expires": invoice.session_expires,
        "post_date": invoice.post_date,
        "post_time": invoice.post_time,
        "hotel_fees": invoice.hotel_fees,
        "transfer_fees": invoice.transfer_fees,
        "tour_fees": invoice.tour_fees,
        "grand_total": invoice.grand_total,
        "invoice_check_out": invoice.invoice_check_out,
        "rooms": {},
        "tours": {},
        "transfers": {},
        "docstatus": invoice.docstatus,
        "status": invoice.status,
        "sales_invoice": sales_invoice, 
        "customer_name": invoice.customer_name,
        "customer_email": invoice.customer_email,
        "customer_mobile_no": invoice.customer_mobile_no
    }
    rooms = {}
    tours = {}
    transfers = {}
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
        room_type, room_acmnd_type_code = frappe.db.get_value("Hotel Room", room.room, ['room_type', 'room_accommodation_type'])
        room_type = frappe.db.get_value("Room Type", room_type, 'room_type', cache=True)
        room_acmnd_type = frappe.db.get_value("Room Accommodation Type", room_acmnd_type_code, 'accommodation_type_name', cache=True)
        hotel_room = {
            "room_name": room.room_name,
            "row_id": room.name,
            "total_price": room.total_price,
            "hotel": room.hotel,
            "room_acmnd_type_code": room_acmnd_type_code,
            "accommodation_type": room_acmnd_type,
            "room_type": room_type,
        }
        adult_paxes = []
        child_paxes = []
        for pax in invoice.room_pax_info:
            if pax.room_name == room.room_name and pax.hotel_search == room.hotel_search:
                if pax.guest_type == 'Adult':
                    adult_paxes.append({
                        "row_id": pax.name,
                        "guest_salutation": pax.guest_salutation,
                        "guest_name": pax.guest_name,
                        "guest_type": pax.guest_type,
                        "guest_age": pax.guest_age,
                        "mobile_no": pax.mobile_no
                    })
                if pax.guest_type == 'Child':
                    child_paxes.append({
                        "row_id": pax.name,
                        "guest_name": pax.guest_name,
                        "guest_type": pax.guest_type,
                        "guest_age": pax.guest_age,
                        "mobile_no": pax.mobile_no,
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
    for tour in invoice.tours:
        if tour.is_canceled:
            continue
        if not tours.get(tour.get('search_name')):
            tours[tour.get('search_name')] = {}
        tours[tour.get('search_name')]['search_name'] = tour.get('search_name')
        tours[tour.get('search_name')]['check_in'] = tour.get('from_date')
        tours[tour.get('search_name')]['check_out'] = tour.get('to_date')
        tours[tour.get('search_name')]['pickup'] = tour.get('pick_up')
        tours[tour.get('search_name')]['pickup_type'] = tour.get('pick_up_type')
        tours[tour.get('search_name')]['pickup_name'] = get_location_name(tour.get('pick_up'), tour.get('pick_up_type'))
        tours[tour.get('search_name')]['tours'] = []
        tours[tour.get('search_name')]['total_price'] = tour.get('tour_price')
        tours[tour.get('search_name')]['adults'] = tour.get('adults')
        tours[tour.get('search_name')]['children'] = tour.get('children')
        tours[tour.get('search_name')]['tour_type'] = tour.get('tour_type')
        for tour_type in invoice.tour_types:
            if tour_type.search_name == tour.get('search_name'):
                tour_details = {
                    "tour_id": tour_type.tour_name,
                    "tour_name": frappe.db.get_value("Tour Type", tour_type.tour_name, "tour_name", cache=True),
                    "tour_type": tour_type.tour_type,
                    "tour_date": tour_type.tour_date,
                    "package": tour_type.package_id,
                    "tour_price": tour_type.tour_price,
                }
                tours[tour_type.search_name]['tours'].append(tour_details)
        adult_paxes = []
        child_paxes = []
        for tour_pax in invoice.tour_pax_info:
            if tour_pax.search_name == tour.get('search_name'):
                if tour_pax.guest_type == 'Adult':
                    adult_paxes.append( {
                        "row_id": tour_pax.name,
                        "guest_salutation": tour_pax.guest_salutation,
                        "guest_name": tour_pax.guest_name,
                        "guest_type": tour_pax.guest_type,
                        "guest_age": tour_pax.guest_age,
                        "mobile_no": tour_pax.mobile_no,
                    })
                if tour_pax.guest_type == 'Child':
                    child_paxes.append({
                        "row_id": tour_pax.name,
                        "guest_name": tour_pax.guest_name,
                        "guest_type": tour_pax.guest_type,
                        "guest_age": tour_pax.guest_age,
                        "mobile_no": tour_pax.mobile_no,
                    })
        tours[tour.get('search_name')]['adult_paxes'] = adult_paxes
        tours[tour.get('search_name')]['child_paxes'] = child_paxes
    for transfer in invoice.transfers:
        if transfer.is_canceled:
            continue
        transfer_search = transfer.get('transfer_search')
        transfer_name = transfer.get('transfer_name')
        if not transfers.get(transfer_search):
            transfers[transfer_search] = {}
        transfers[transfer_search][transfer_name] = {}
        transfers[transfer_search][transfer_name]['transfer_name'] = transfer_name
        transfers[transfer_search][transfer_name]['transfer_search'] = transfer_search
        transfers[transfer_search][transfer_name]['transfer_type'] = transfer.get('transfer_type')
        transfers[transfer_search][transfer_name]['transfer_id'] = transfer.get('transfer')
        transfers[transfer_search][transfer_name]['transfer_price'] = transfer.get('transfer_price')
        transfers[transfer_search][transfer_name]['pax_info'] = {
            "adults": transfer.get('adults'),
            "children": transfer.get('children'),
            "childrenInfo": []
        }
        transfers[transfer_search][transfer_name]['pickup'] = transfer.get('pick_up')
        transfers[transfer_search][transfer_name]['pickup_type'] = transfer.get('pick_up_type')
        transfers[transfer_search][transfer_name]['pickup_name'] = get_location_name(transfer.get('pick_up'), transfer.get('pick_up_type'))
        transfers[transfer_search][transfer_name]['dropoff'] = transfer.get('drop_off')
        transfers[transfer_search][transfer_name]['dropoff_type'] = transfer.get('drop_off_type')
        transfers[transfer_search][transfer_name]['dropoff_name'] = get_location_name(transfer.get('drop_off'), transfer.get('drop_off_type'))
        transfers[transfer_search][transfer_name]['transfer_date'] = transfer.get('transfer_date')
        transfers[transfer_search][transfer_name]['pick_up_postal_code'] = transfer.get('pick_up_postal_code')
        transfers[transfer_search][transfer_name]['drop_off_postal_code'] = transfer.get('drop_off_postal_code')
        transfers[transfer_search][transfer_name]['flight_no'] = transfer.get('flight_no')
        adult_paxes = []
        child_paxes = []
        for transfer_pax in invoice.transfer_pax_info:
            if transfer_pax.transfer_search == transfer_search and transfer_pax.transfer_name == transfer_name:
                if transfer_pax.guest_type == 'Adult':
                    adult_paxes.append( {
                        "row_id": transfer_pax.name,
                        "guest_salutation": transfer_pax.guest_salutation,
                        "guest_name": transfer_pax.guest_name,
                        "guest_type": transfer_pax.guest_type,
                        "guest_age": transfer_pax.guest_age,
                        "mobile_no": transfer_pax.mobile_no,
                    })
                if transfer_pax.guest_type == 'Child':
                    child_paxes.append({
                        "row_id": transfer_pax.name,
                        "guest_name": transfer_pax.guest_name,
                        "guest_type": transfer_pax.guest_type,
                        "guest_age": transfer_pax.guest_age,
                        "mobile_no": transfer_pax.mobile_no,
                    })
        transfers[transfer_search][transfer_name]['adult_paxes'] = adult_paxes
        transfers[transfer_search][transfer_name]['child_paxes'] = child_paxes

    return {
        "invoice_id": invoice.name,
        "session_expires": invoice.session_expires,
        "voucher_no": invoice.voucher_no,
        "post_date": invoice.post_date,
        "post_time": invoice.post_time,
        "hotel_fees": invoice.hotel_fees,
        "transfer_fees": invoice.transfer_fees,
        "tour_fees": invoice.tour_fees,
        "grand_total": invoice.grand_total,
        "rooms": rooms,
        "tours": tours,
        "transfers": transfers,
        "docstatus": invoice.docstatus,
        "sales_invoice": sales_invoice, 
        "customer_name": invoice.customer_name,
        "customer_email": invoice.customer_email,
        "customer_mobile_no": invoice.customer_mobile_no,
        "status": invoice.status,
    }

def get_location_name(location, location_type):
    return get_location_full_name(location, location_type)

@frappe.whitelist()
def get_all_invoices(voucher_no='', start=0, limit=20):
    #company = frappe.db.get_value("User", frappe.session.user, "company")
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        if voucher_no:
            return frappe.db.get_all("Sales Invoice", {"child_company": company_details.get('child_company'), "status": ["!=", "Cancelled"], "voucher_no": ["like", "%"+ voucher_no +"%"]}, [
                "name", "voucher_no", "grand_total", "post_date", "status",
                "post_time", "session_expires", "docstatus"], order_by="creation DESC" ,limit=limit, start=start)
        else:
            return frappe.db.get_all("Sales Invoice", {"child_company": company_details.get('child_company'), "status": ["!=", "Cancelled"]}, [
                "name","voucher_no", "grand_total", "post_date", "status",
                "post_time", "session_expires", "docstatus"], order_by="creation DESC" ,limit=limit, start=start)
    else:
        voucher_search = ''
        if voucher_no:
            voucher_search = "and si.voucher_no like %(voucher_no)s"

        bookings =  frappe.db.sql("""
            SELECT si.name, si.voucher_no, si.grand_total, si.post_date, si.status, si.post_time, si.session_expires, si.docstatus, si.child_company, si.company
                                FROM `tabSales Invoice` si
                                WHERE si.docstatus = 1
                                AND si.company = %(company)s and si.child_company is null and si.status != 'Cancelled' {voucher_search}
                             ORDER BY si.creation DESC LIMIT %(limit)s OFFSET %(start)s
""".format(voucher_search=voucher_search), {"voucher_no": "%%%s%%" % voucher_no, "company": company_details.get('company'),
        "limit": limit, "start": start
      }, as_dict=True)
        print(bookings)
        return bookings

@frappe.whitelist()
def get_all_invoices_subagency(voucher_no='', start=0, limit=20):
    #company = frappe.db.get_value("User", frappe.session.user, "company")
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        frappe.throw("You are not allowed to access this page")
    else:
        voucher_search = ''
        if voucher_no:
            voucher_search = "and si.voucher_no like %(voucher_no)s"
        return frappe.db.sql("""
            SELECT si.name, si.voucher_no, si.grand_total, si.post_date, si.status, si.post_time, si.session_expires, si.docstatus, si.child_company, 
                             cmp.company_name as child_company 
                                FROM `tabSales Invoice` si
                             INNER JOIN `tabCompany` as cmp ON cmp.name = si.child_company
                                WHERE si.docstatus = 1
                                AND si.company = %(company)s and si.child_company is not null and si.status != 'Cancelled' {voucher_search}
                                ORDER BY si.creation DESC LIMIT %(limit)s OFFSET %(start)s
    """.format(voucher_search=voucher_search), {"voucher_no": "%%%s%%" % voucher_no, "company": company_details.get('company'),
          "limit": limit, "start": start
          }, as_dict=True) 

def get_bookings_detials(voucher_no=''):
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        return {"agency_bookings": frappe.db.sql("""
        SELECT count(si.name) as bookings, sum(si.grand_total) as total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1 and si.status != 'Cancelled'
        AND si.child_company = %(child_company)s AND si.company = %(company)s
    """, {"voucher_no": "%%%s%%" % voucher_no, "child_company": company_details.get('child_company'), "company": company_details.get('company')}, as_dict=True)[0],
    "subagency_bookings": {
        "bookings": 0,
        "total": 0
    }}
    else:

        agency_bookings = frappe.db.sql("""
        SELECT count(si.name) as bookings, sum(si.grand_total) as total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1  and si.status != 'Cancelled'
        AND si.company = %(company)s and si.child_company is null
    """, {"voucher_no": "%%%s%%" % voucher_no, "company": company_details.get('company')}, as_dict=True)
        if len(agency_bookings) > 0:
            agency_bookings = agency_bookings[0]
        else:
            agency_bookings = {"bookings": 0, "total": 0}
        subagency_bookings = frappe.db.sql("""
            SELECT count(si.name) as bookings, sum(si.grand_total) as total
            FROM `tabSales Invoice` si
            WHERE si.docstatus = 1 and si.status != 'Cancelled'
            AND si.company = %(company)s and si.child_company is not null   """,
            { "company": company_details.get('company')}, as_dict=True) 
        if len(subagency_bookings) > 0:
            subagency_bookings = subagency_bookings[0]
        else:
            subagency_bookings = {"bookings": 0, "total": 0}
        return {
            "subagency_bookings": subagency_bookings,
            "agency_bookings": agency_bookings,
        }
@frappe.whitelist()
def complete_reservation():
    invoice = frappe.get_doc("Sales Invoice", {"name": frappe.form_dict.sales_invoice, "customer": frappe.session.user})
    print(frappe.form_dict.rooms)
    if type(frappe.form_dict.rooms) != dict:
        rooms = json.loads(frappe.form_dict.rooms)
    else:
        rooms = frappe.form_dict.rooms
    if type(frappe.form_dict.tours) != dict:
        tours = json.loads(frappe.form_dict.tours)
    else:
        tours = frappe.form_dict.tours
    if type(frappe.form_dict.transfers) != dict:
        transfers = json.loads(frappe.form_dict.transfers)
    else:
        transfers = frappe.form_dict.transfers
    invoice.room_extras = []
    
    for roomRowId in rooms:
        extras = rooms[roomRowId].pop('extras')
        roomDetails = rooms[roomRowId].pop('details')
        hotel_search = None
        for room in invoice.rooms:
            if room.name == roomRowId:
                if roomDetails.get('board'):
                    room.board = roomDetails.get('board')
                    room.board_extra_price = invoice.get_board_price(room.board, room, board_price=float(roomDetails.get('board_price')))#float(roomDetails.get('board_price'))
                if roomDetails.get('bed_type'):
                    room.bed_type = roomDetails.get('bed_type')
        for paxRowId in rooms[roomRowId]:
            for pax in invoice.room_pax_info:
                if pax.name == paxRowId:
                    pax.guest_salutation = rooms[roomRowId][paxRowId]['salut']
                    pax.guest_name = rooms[roomRowId][paxRowId]['guest_name']
                    pax.mobile_no = rooms[roomRowId][paxRowId]['mobile_no']
                    hotel_search = pax.hotel_search
        for extra in extras:
            extra_row = invoice.append('room_extras')
            extra_row.hotel_search = hotel_search
            extra_row.extra = extra['extra']
            extra_row.room_name = extra['room_name']
            extra_row.extra_price = float(extra['extra_price'])
            extra_row.room_row_id = roomRowId
            # ToDo make extra for amount and percentage
    for searchName in tours:
        tourPax = tours[searchName]
        for paxRowId in tourPax:
            for pax in invoice.tour_pax_info:
                if pax.name == paxRowId:
                    pax.guest_salutation = tourPax[paxRowId]['salut']
                    pax.guest_name = tourPax[paxRowId]['guest_name']
                    pax.mobile_no = tourPax[paxRowId]['mobile_no']
                    break
    for searchName in transfers:
        transferSearch = transfers[searchName]
        for transferName in transferSearch:
            transferPax = transferSearch[transferName]['paxes']
            for paxRowId in transferPax:
                for pax in invoice.transfer_pax_info:
                    if pax.name == paxRowId:
                        pax.guest_salutation = transferPax[paxRowId]['salut']
                        pax.guest_name = transferPax[paxRowId]['guest_name']
                        pax.mobile_no = transferPax[paxRowId]['mobile_no']
                        break
            for transfer in invoice.transfers:
                if str(transfer.transfer_name) == str(transferName) and transfer.transfer_search == searchName:
                    transfer.flight_no = transferSearch[transferName]['flight_no']
                    break
    invoice.customer_name = frappe.form_dict.customer_name
    invoice.customer_email = frappe.form_dict.customer_email
    invoice.customer_mobile_no = frappe.form_dict.customer_mobile_no
    invoice.save(ignore_permissions=True)
    invoice.submit()
    frappe.db.commit()
    return {"success_key": 1, "message": ""}


@frappe.whitelist()
def cancel_reservation(invoice_id):
    #company = frappe.db.get_value("User", frappe.session.user, "company")
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company')})
    invoice.cancel_invoice()
    invoice.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success_key": 1}


@frappe.whitelist()
def add_nights_to_room(sales_invoice, row_id, check_in=None, check_out=None):
    if not check_in and not check_out:
        frappe.throw("Please Select new Check-in or new Check-out")
    company = frappe.db.get_value("User", frappe.session.user, "company")
    invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company})
    invoice.add_nights(row_id, check_in, check_out)
    frappe.db.commit()

@frappe.whitelist()
def delete_reservation():
    sales_invoice = frappe.form_dict.invoice
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company_details.get('company')})
    if invoice.docstatus == 0:
        invoice.delete()
    frappe.db.commit()

@frappe.whitelist()
def add_transfers_to_completed_invoice():
    invoice_id = frappe.form_dict.invoice_id
    selected_transfers = frappe.form_dict.selected_transfers
    if type(selected_transfers) == str:
        selected_transfers = json.loads(selected_transfers)
    company_details = get_company_details()
    try:
        if company_details.get('is_child_company'):
            invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
        else:
            invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company')})
    except:
        return {"success_key": 0, "message": "Invoice not found"}
    res = invoice.add_transfers(selected_transfers)
    invoice.notifiy_invoice_edit("Invoice " + invoice_id + " has been updated","Transfers have been added to the invoice")
    frappe.db.commit()  
    if res:
        return {"success_key": 1, "message": ""}
    else:
        return {"success_key": 0, "message": "Unable to add transfers"}

@frappe.whitelist()
def add_tours_to_completed_invoice():
    invoice_id = frappe.form_dict.invoice_id
    selected_tours = frappe.form_dict.selected_tours
    print(selected_tours)
    if type(selected_tours) == str:
        selected_tours = json.loads(selected_tours)
    company_details = get_company_details()
    try:
        if company_details.get('is_child_company'):
            invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
        else:
            invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company')})
    except:
        return {"success_key": 0, "message": "Invoice not found"}
    res = invoice.add_tours(selected_tours)
    invoice.notifiy_invoice_edit("Invoice " + invoice_id + " has been updated","Tours have been added to the invoice")
    frappe.db.commit()
    if res:
        return {"success_key": 1, "message": ""}
    else:
        return {"success_key": 0, "message": "Unable to add tours"}
    

@frappe.whitelist()
def update_reservation():
    invoice_id = frappe.form_dict.invoice_id
    transfers_info = frappe.form_dict.transfers_info
    tours_info = frappe.form_dict.tours_info

    if type(transfers_info) == str:
        transfers_info  = json.loads(transfers_info)
    if type(tours_info) == str:
        tours_info = json.loads(tours_info)
    company_details = get_company_details()
    try:
        if company_details.get('is_child_company'):
            invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
        else:
            invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company')})
    except:
        return {"success_key": 0, "message": "Invoice not found"}
    invoice.update_transfers(transfers_info)
    invoice.update_tours(tours_info)
    invoice.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success_key": 1, "message": ""}

@frappe.whitelist()
def cancel_transfer(invoice_id, transfer_search, transfer_name):
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company')})
    invoice.cancel_transfer(transfer_search, transfer_name)
    invoice.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success_key": 1, "message": ""}

@frappe.whitelist()
def cancel_tour(invoice_id, tour_search):
    company_details = get_company_details()
    if company_details.get('is_child_company'):
        invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company'), "child_company": company_details.get('child_company')})
    else:
        invoice = frappe.get_doc("Sales Invoice", {"name": invoice_id, "company": company_details.get('company')})
    invoice.cancel_tour(tour_search)
    invoice.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success_key": 1, "message": ""}