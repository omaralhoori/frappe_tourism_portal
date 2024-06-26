import frappe
from tourism_portal.utils import get_utils_company_details


def add_rooms_to_invoice(invoice, rooms, hotel_margin):
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
            total_price_company = 0
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
                room_price.nights = frappe.utils.date_diff(room_price.check_out, room_price.check_in) + 1
                if room_price.nights < 1:
                    frappe.throw("Check out date must be greater than check in date")
                room_price.selling_price = float(contract['selling_price']) #/ room_price.nights
                room_price.selling_price_company = float(contract['selling_price_company']) #/ room_price.nights
                room_price.total_selling_price = float(contract['total_price'])
                room_price.total_selling_price_company = float(contract['total_price_company'])
                total_price += float(contract['total_price'])
                total_price_company += float(contract['total_price_company'])
                #room_price.contract_id = contract.get('contract_id')
                room_price.contract_price = contract.get('price_id') if contract.get('price_id') and contract.get('price_id') != 'None' and contract.get('price_id') != 'null' and contract.get('price_id') != 'undefined' else None
                room_price.inquiry_id = contract.get('inquiry_price_id') if contract.get('inquiry_price_id') and contract.get('inquiry_price_id') != 'None' and contract.get('inquiry_price_id') != 'null' and contract.get('inquiry_price_id') != 'undefined' else None
                if room_price.inquiry_id:
                    room_price.buying_currency,room_price.buying_price, inquiry = frappe.db.get_value("Hotel Inquiry Buying Price", room_price.inquiry_id,["buying_currency", "buying_price", "parent"])
                    frappe.db.set_value("Hotel Inquiry Request", inquiry, "used", 1)
                elif room_price.contract_price:
                    room_price.contract_id = frappe.db.get_value("Hotel Room Price", room_price.contract_price, "room_contract", cache=True)
                    room_price.buying_currency,room_price.buying_price = frappe.db.get_value("Hotel Room Price", room_price.contract_price,["buying_currency", "buying_price"])
                if not room_price.buying_currency:
                    frappe.throw("Check your request, there is missing information. Please contact your system administrator.")
                if room_price.contract_id:
                    room_price.cancellation_policy = frappe.db.get_value("Hotel Room Contract",room_price.contract_id, "cancellation_policy", cache=True)
                if not room_price.cancellation_policy:
                    hotel = frappe.db.get_value("Hotel Room",  room['room_id'], "hotel", cache=True)
                    room_price.cancellation_policy = frappe.db.get_value("Hotel", hotel, "hotel_cancellation_policy")
            if total_price <= 0:
                frappe.throw("Please check your request, there is missing information. Please contact your system administrator.")
            invc_room.total_price = total_price
            invc_room.total_price_company = total_price_company
    

def add_transfers_to_invoice(invoice, transfers, transfer_margin):
    total_amount = 0
    total_company_amount = 0
    for searchName in transfers:
        search = transfers[searchName]
        for transferName in search:
            transfer = transfers[searchName][transferName]
            invc_transfer = invoice.append("transfers")
            invc_transfer.transfer_search = searchName
            invc_transfer.transfer_name = transferName
            invc_transfer.transfer_type = transfer['transfer_type']
            invc_transfer.transfer = transfer['transfer_id']
            invc_transfer.transfer_price = float(transfer['transfer_price'])
            invc_transfer.transfer_price_company = float(transfer['transfer_price_company'])
            total_amount += float(transfer['transfer_price'])
            total_company_amount += float(transfer['transfer_price_company'])
            invc_transfer.adults = transfer['pax_info'].get('adults')
            invc_transfer.children = transfer['pax_info'].get('children')
            invc_transfer.pick_up = transfer['pick_up']
            invc_transfer.pick_up_type = transfer['pick_up_type']
            invc_transfer.pick_up_postal_code = transfer['pick_up_postal_code']
            invc_transfer.transfer_date = transfer['transfer_date']
            invc_transfer.drop_off = transfer['drop_off']
            invc_transfer.drop_off_type = transfer['drop_off_type']
            invc_transfer.drop_off_postal_code = transfer['drop_off_postal_code']
            invc_transfer.flight_no = transfer.get('flight_no')
            for i in range(int(transfer['pax_info'].get('adults'))):
                    guest = invoice.append("transfer_pax_info")
                    guest.transfer_name = transferName
                    guest.transfer_search = searchName
                    guest.guest_type = 'Adult'
            for child_age in transfer['pax_info'].get('childrenInfo'):
                guest = invoice.append("transfer_pax_info")
                guest.guest_type = 'Child'
                guest.transfer_search = searchName
                guest.transfer_name = transferName
                guest.guest_age = int(child_age)
    return total_amount, total_company_amount

def add_tours_to_invoice(invoice, tours, tour_margin):
    total_amount = 0
    total_company_amount = 0
    for searchName in tours:
        total_price = 0
        total_price_company = 0
        search = tours[searchName]
        tour_search = invoice.append("tours")
        tour_search.search_name = searchName
        tour_search.pick_up = search['pickup']
        tour_search.pick_up_type = search['pickup_type']
        tour_search.from_date = search['check_in']
        tour_search.to_date = search['check_out']
        tour_search.tour_type = search['tour_type']
        tour_search.adults = int(search['paxes'].get('adults'))
        tour_search.children = int(search['paxes'].get('children'))
        for selected_tour in search['selected_tours']:
            total_price += float(selected_tour['price'])
            total_price_company += float(selected_tour['priceCompany'])#get_company_price(float(selected_tour['price']), tour_margin)
            tour_type = get_tour_doctype(search['tour_type'])
            if tour_type == "single":
                for tour in selected_tour['tours']:
                    invoice_tour = invoice.append("tour_types")
                    invoice_tour.search_name = searchName
                    invoice_tour.tour_type = tour_type
                    invoice_tour.tour_name = tour
                    if search['tour_type'] == 'vip':
                        invoice_tour.tour_price = float(selected_tour['price'])
                        invoice_tour.tour_price_company = float(selected_tour['priceCompany'])#get_company_price(float(selected_tour['price']), tour_margin)
                    else:
                        invoice_tour.tour_price = float(selected_tour['toursPrice'].get(tour, '0'))
                        invoice_tour.tour_price_company = float(selected_tour['toursPriceCompany'].get(tour, '0')) #get_company_price(float(selected_tour['toursPrice'].get(tour, '0')), tour_margin)
            else:
                for package in selected_tour['tours']:
                    package_tours = get_package_tours(package)
                    for package_tour in package_tours:
                        invoice_tour = invoice.append("tour_types")
                        invoice_tour.search_name = searchName
                        invoice_tour.tour_type = tour_type
                        invoice_tour.tour_name = package_tour['tour']
                        invoice_tour.package_id = package
        for i in range(int(search['paxes'].get('adults'))):
                guest = invoice.append("tour_pax_info")
                guest.search_name = searchName
                guest.guest_type = 'Adult'
        for child_age in search['paxes'].get('child-ages'):
            guest = invoice.append("tour_pax_info")
            guest.guest_type = 'Child'
            guest.search_name = searchName
            guest.guest_age = int(child_age)
        tour_search.tour_price = total_price
        tour_search.tour_price_company = total_price_company
        total_amount += total_price
        total_company_amount += total_price_company
    return total_amount, total_company_amount

def get_tour_doctype(tour_type):
    doctype = "single"
    if tour_type == "package":
        doctype = "package"

    return doctype

def get_package_tours(package):
    return frappe.db.get_all("Tour Package Item", {"parent": package}, ["tour"])



def get_company_price(selling_price, margin):
    if float(selling_price) == 0:
        return 0
    return float(selling_price) - float(margin) 
