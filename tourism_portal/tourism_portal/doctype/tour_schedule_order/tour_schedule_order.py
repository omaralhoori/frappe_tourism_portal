# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.utils import get_date_weekday, get_location_city

class TourScheduleOrder(Document):
	pass


def schedule_tours_dates(tour_search):
	#tour_search = get_tour_search_test()
	schedules = []
	if tour_search['tour_type'] == 'package':
		schedules = schedule_tours_dates_package(tour_search)
	elif tour_search['tour_type'] in ('vip', 'group-economic'):
		schedules = schedule_tours_dates_normal(tour_search)
	elif tour_search['tour_type'] == 'group-premium':
		schedules = schedule_tours_dates_premium(tour_search)

					
	return schedules
def schedule_tours_dates_normal(tour_search):
	tour_search_data = get_tour_search_data(tour_search)
	tour_search_data = schedule_tours_dates_package_normal(tour_search_data, tour_search['tours'])
	return tour_search_data

def schedule_tours_dates_premium(tour_search):
	tour_search_data = get_tour_search_data(tour_search)
	tour_search_data = schedule_tours_dates_package_premium(tour_search_data, tour_search['tours'])
	return tour_search_data

def schedule_tours_dates_package(tour_search):
	#for tour in tour_search['tours']:
	tour_search_data = get_tour_search_data(tour_search)
	packages = {}
	for tour in tour_search['tours']:
		if not packages.get(tour['package']):
			packages[tour['package']] = []
		packages[tour['package']].append(tour)
	for package in packages:
		if frappe.db.get_value("Tour Package", package, "is_premium"):
			tour_search_data = schedule_tours_dates_package_premium(tour_search_data, packages[package])
		else:
			tour_search_data = schedule_tours_dates_package_normal(tour_search_data, packages[package])
	return tour_search_data
def schedule_tours_dates_package_normal(tour_search_data, tours):
	for tour in tours:
		if len(tour_search_data['date_list']) > 0:
			sDate = tour_search_data['date_list'].pop(0)
			tour_search_data['schedules'].append({
				"tour": tour['tour'],
				"date": sDate
			})
		else:
			tour_search_data['schedules'].append({
				"tour": tour['tour'],
				"date": None
			})
	return tour_search_data['schedules']
def schedule_tours_dates_package_premium(tour_search_data, tours):
	schedules = get_scheduler(tour_search_data)
	available_dates = tour_search_data['date_list'].copy()
	for i in range(len(schedules)):
		if i < len(tour_search_data['date_list']):
			tourId = schedules[i]['tour_type']
			for tour in tours:
				if tour['tour'] == tourId:
					tour_search_data['schedules'].append({
						"tour": tour['tour'],
						"date": tour_search_data['date_list'][i]
					})
					available_dates.remove(tour_search_data['date_list'][i])
					tour['tour_date'] = tour_search_data['date_list'][i]
					break
	for tour in tours:
		if tour['tour_date'] == None:
			if len(available_dates) > 0:
				tour_search_data['schedules'].append({
					"tour": tour['tour'],
					"date": available_dates.pop(0)
				})
			else:
				tour_search_data['schedules'].append({
					"tour": tour['tour'],
					"date": None
				})
	return tour_search_data['schedules']
def get_scheduler(tour_search_data):
	query = """
		SELECT tsoi.tour_type, tsoi.idx tour_order
		FROM `tabTour Schedule Order Item` as tsoi
		INNER JOIN `tabTour Schedule Order` as tso ON tso.name = tsoi.parent
		WHERE pickup_city = %(pickup_city)s
				AND advent_day = %(arrival_day)s
		order by tsoi.idx
	"""
	tours_schedule_order = frappe.db.sql(query, {"pickup_city": tour_search_data['pickup_city'],
											   "arrival_day": tour_search_data['arrival_day']}, as_dict=True)
	return tours_schedule_order
def get_tour_search_data(tour_search):
	pickup_city = get_location_city(tour_search['pickup_type'], tour_search['pickup'])
	arrival_day = get_date_weekday(tour_search['check_in'])
	date_list = get_dates_between_two_dates(tour_search['check_in'], tour_search['check_out'])
	return {
		"pickup_city": pickup_city,
		"arrival_day": arrival_day,
		"date_list": date_list,
		"schedules": []
	}

def check_alltours_scheduled(schedules, tours):
	non_scheduled_tours = [tour['tour'] for tour in tours if tour['tour_date'] == None]
	if len(non_scheduled_tours) > 0:
		for tour in non_scheduled_tours:
			schedules.append({
				"tour": tour,
				"date": None
			})
	return schedules
def get_tour_search_test():
	return {
		'check_in': "2023-12-16", 'check_out': "2023-12-19", 
		'tours': [
			{'package': 'IST5TOURPRM', 'tour_type': 'package', 'tour': 'Sahara', 'tour_date': None},
			  {'package': 'IST5TOURPRM', 'tour_type': 'package', 'tour': 'Emirate', 'tour_date': None}, 
			  {'package': 'IST5TOURPRM','tour_type': 'package', 'tour': 'Sapanca', 'tour_date': None},
			    {'package': 'IST5TOURPRM','tour_type': 'package', 'tour': 'Bosfor', 'tour_date': None}, 
				{'package': 'IST5TOURPRM', 'tour_type': 'package', 'tour': 'BORS', 'tour_date': None}], 
		'tour_type': 'group-economic', 'pickup': 'Konak', 'pickup_type': 'hotel'}
def check_valid_date(tours, date):
	for tour in tours:
		if tour['tour_date'] == date:
			return False
	return True
def get_schedule_date(date_list, tours):
	sDate = date_list.pop(0)
	while not check_valid_date(tours, sDate):
		if len(date_list) == 0:
			return None, date_list
		sDate = date_list.pop(0)
	return sDate, date_list
def get_dates_between_two_dates(from_date, to_date):
	from_date = frappe.utils.get_datetime(from_date)
	to_date = frappe.utils.get_datetime(to_date)
	dates = []
	while from_date <= to_date:
		dates.append(from_date.strftime("%Y-%m-%d"))
		from_date += frappe.utils.datetime.timedelta(days=1)
	#dates.reverse()
	return dates