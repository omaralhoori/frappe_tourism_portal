# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt
import calendar

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate

class TourSchedulingTool(Document):
	@frappe.whitelist()
	def schedule_tour(self, days):
		"""Creates tour schedules as per specified parameters"""

		tour_schedules = []
		tour_schedules_errors = []
		rescheduled = []
		reschedule_errors = []

		self.validate_mandatory(days)
		self.validate_date()


		date = self.from_date
		while date < self.to_date:
			if calendar.day_name[getdate(date).weekday()] in days:
				tour_schedule = self.make_tour_schedule(date)
				try:
					tour_schedule.save()
				except:
					tour_schedules_errors.append(date)
				else:
					tour_schedules.append(tour_schedule)

			date = add_days(date, 1)

		return dict(
			tour_schedules=tour_schedules,
			tour_schedules_errors=tour_schedules_errors,
			rescheduled=rescheduled,
			reschedule_errors=reschedule_errors,
		)

	def validate_mandatory(self, days):
		"""Validates all mandatory fields"""
		if not days:
			frappe.throw(_("Please select at least one day to schedule the tour."))
		fields = [
			"tour_type",
			"from_date",
			"to_date",
		]
		for d in fields:
			if not self.get(d):
				frappe.throw(_("{0} is mandatory").format(self.meta.get_label(d)))

	def validate_date(self):
		"""Validates if tour Start Date is greater than tour End Date"""
		if self.from_date > self.to_date:
			frappe.throw(_("tour Start Date cannot be greater than tour End Date."))

	def delete_tour_schedule(self, rescheduled, reschedule_errors, days):
		"""Delete all tour schedule within the Date range and specified filters"""
		schedules = frappe.get_list(
			"Tour Schedule",
			fields=["name", "schedule_date"],
			filters=[
				["tour_type", "=", self.tour_type],
				["schedule_date", ">=", self.from_date],
				["schedule_date", "<=", self.to_date],
			],
		)

		for d in schedules:
			try:
				if calendar.day_name[getdate(d.schedule_date).weekday()] in days:
					frappe.delete_doc("Tour Schedule", d.name)
					rescheduled.append(d.name)
			except Exception:
				reschedule_errors.append(d.name)
		return rescheduled, reschedule_errors

	def make_tour_schedule(self, date):
		"""Makes a new tour Schedule.
		:param date: Date on which tour Schedule will be created."""
		tour_schedule = frappe.new_doc("Tour Schedule")
		tour_schedule.tour_type = self.tour_type
		tour_schedule.limit = self.limit
		tour_schedule.schedule_date = date
		return tour_schedule
