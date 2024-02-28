import datetime

def get_hotel_total_days(hotelParams):
	total_days = 0
	if not hotelParams: return None
	for search in hotelParams:
		hotel = hotelParams[search]
		date_format = "%Y-%m-%d"
		delta = datetime.strptime(hotel.get('checkout'), date_format) - datetime.strptime(hotel.get('checkin'), date_format)
		total_days += delta.days
	return total_days