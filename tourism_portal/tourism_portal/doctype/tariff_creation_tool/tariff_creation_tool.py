# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.utils import calculate_extra_price
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from frappe.model.naming import make_autoname

class TariffCreationTool(Document):
	pass



@frappe.whitelist()
def fetch_data(from_date, to_date, company_class, template):
	template = frappe.get_doc("Tariff Template", template)
	hotels = {}

	for hotel in template.hotels:
		hotel_rate = get_hotel_rates(hotel.hotel, from_date, to_date, company_class, hotel.location, template.tariff_type)
		hotels[hotel.hotel] = hotel_rate
	
	return {
		"hotels": hotels,
	}

@frappe.whitelist()
def generate_title(from_date, to_date, template):
	template = frappe.get_doc("Tariff Template", template)
	naming_series = template.naming_series 
	title = make_autoname(naming_series, "Tariff")
	title = title + "  " + from_date.split("-")[2] + "."+ from_date.split("-")[1] +  " TILL "  + to_date.split("-")[2] + "." + to_date.split("-")[1]
	title = title.replace(" ", "_")
	return title
def get_hotel_rates(hotel, from_date, to_date, company_class, location, tariff_type):
	rates = frappe.db.sql("""
		SELECT
			prc.name as price_id,
			prc.hotel,
			hotel.hotel_name,
			hotel.star_rating as hotel_stars,
			prc.room_accommodation_type as room_accommodation_type, 
			prc_cmpny.extra_type,
			prc_cmpny.extra_profit,
			cntrct.room_type, 
			prc.selling_price, 
			IF(prc.check_in_from_date > %(from_date)s,prc.check_in_from_date ,%(from_date)s) as check_in_from_date, 
			IF(prc.check_in_to_date < %(to_date)s,prc.check_in_to_date ,%(to_date)s) as check_in_to_date
		FROM
			`tabHotel Room Price` as prc
		INNER JOIN
			`tabHotel Room Contract` as cntrct ON prc.room_contract=cntrct.name
		INNER JOIN
			`tabHotel Room Price Company` as prc_cmpny ON prc.name=prc_cmpny.parent AND prc_cmpny.company_class=%(company_class)s
		INNER JOIN
			`tabHotel` as hotel ON prc.hotel=hotel.name
		WHERE
			prc.hotel=%(hotel)s AND prc.check_in_from_date<=%(to_date)s AND prc.check_in_to_date>=%(from_date)s
		ORDER BY
			prc.check_in_from_date
	""", {"hotel": hotel, "from_date": from_date, "to_date": to_date, "company_class": company_class}, as_dict=True)
	hotel_rates = {}
	
	for rate in rates:
		if not hotel_rates.get(rate.room_type + '-'+rate.check_in_from_date + "-" + rate.check_in_to_date):
			hotel_rates[rate.room_type + '-'+ rate.check_in_from_date + "-" + rate.check_in_to_date] = {}
		if rate['check_in_from_date'] != from_date or rate['check_in_to_date'] != to_date:
			rate['special_period'] = rate['check_in_from_date'].split("-")[2] +'.' +rate['check_in_from_date'].split("-")[1] +" - " + rate['check_in_to_date'].split("-")[2] + '.'+ rate['check_in_to_date'].split("-")[1]
		rate['location'] = location
		rate['selling_price'] = calculate_extra_price(rate['selling_price'], rate['extra_type'], rate['extra_profit'])
		if rate.room_accommodation_type == "SGL":
			if rate.room_type != 'STD':
				rate['hotel_name'] += f" ({frappe.db.get_value('Room Type', rate.room_type, 'room_type', cache=True)})"
			hotel_rates[rate.room_type + '-'+ rate.check_in_from_date + "-" + rate.check_in_to_date]["SGL"] = rate
		elif rate.room_accommodation_type == "DBL":
			if tariff_type == 'Per Person':
				rate['selling_price'] = rate['selling_price'] / 2
			hotel_rates[rate.room_type + '-'+ rate.check_in_from_date + "-" + rate.check_in_to_date]["DBL"] = rate
		elif rate.room_accommodation_type == "TRPL":

			if tariff_type == 'Per Person':
				rate['selling_price'] = rate['selling_price'] / 3
			hotel_rates[rate.room_type + '-'+ rate.check_in_from_date + "-" + rate.check_in_to_date]["TRPL"] = rate
	
	return hotel_rates

@frappe.whitelist()
def create_tariff(template, hotels, from_date, to_date, updated_date, title="Tariff"):
	tariff_template = frappe.get_doc("Tariff Template", template)
	tariff_header = frappe.db.get_value('Tariff Template Asset', tariff_template.header, 'asset_file')
	tariff_footer = frappe.db.get_value('Tariff Template Asset', tariff_template.footer, 'asset_file')
	terms = None
	if tariff_template.terms_and_conditions:
		terms = frappe.db.get_all("Tariff Template Policy Item", filters={"parent": tariff_template.terms_and_conditions}, fields=["policy_details"])
	html = frappe.render_template('tourism_portal/templates/tariff/tariff_base.html', {
		"template": tariff_template,
		'header': tariff_header,
		'footer': tariff_footer,
		'from_date': from_date.split("-")[2] + '.' + from_date.split("-")[1],
		'to_date': to_date.split("-")[2] + '.' + to_date.split("-")[1],
		'updated_date': updated_date.split("-")[2] + '.' + updated_date.split("-")[1],
		"hotels": frappe.parse_json(hotels),
		"title": title,
		"terms": terms
	})
	css = CSS(string=frappe.render_template('tourism_portal/templates/tariff/tariff_style.css', {"template": tariff_template}))
	font_config = FontConfiguration()
	pdf = HTML(string=html)
	site = frappe.get_site_path()
	tariff_path = site+'/public/files/example.pdf'
	pdf.write_pdf(tariff_path, stylesheets=[css], font_config=font_config)
	return '/files/example.pdf'

import unittest
from frappe.tests.test_commands import BaseTestCommands
class TestCreateTariff(BaseTestCommands, unittest.TestCase):
	def test_execute(self):
		result = create_tariff("Test Template", '{"hotel1": {"STD-2024-01-01-2024-12-31": {"price_id": "00001", "hotel": "hotel1", "hotel_name": "Hotel 1", "hotel_stars": 5, "room_accommodation_type": "SGL", "extra_type": "Percentage", "extra_profit": 10, "room_type": "STD", "selling_price": 100, "check_in_from_date": "2024-01-01", "check_in_to_date": "2024-12-31", "special_period": "01.01 - 31.12", "location": "Dubai"}, "STD-2024-01-01-2024-12-31": {"price_id": "00002", "hotel": "hotel1", "hotel_name": "Hotel 1", "hotel_stars": 5, "room_accommodation_type": "DBL", "extra_type": "Percentage", "extra_profit": 10, "room_type": "STD", "selling_price": 200, "check_in_from_date": "2024-01-01", "check_in_to_date": "2024-12-31", "special_period": "01.01 - 31.12", "location": "Dubai"}}}')
		self.assertTrue(result)