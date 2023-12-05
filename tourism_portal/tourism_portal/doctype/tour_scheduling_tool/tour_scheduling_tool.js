// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tour Scheduling Tool', {
	refresh: function(frm) {
		frm.disable_save();
		frm.trigger("render_days");
		frm.page.set_primary_action(__('Schedule Tour'), () => {
			frappe.dom.freeze(__("Scheduling..."));
			frm.call('schedule_tour', { days: frm.days.get_checked_options() })
				.fail(() => {
					frappe.dom.unfreeze();
					frappe.msgprint(__("Tour Scheduling Failed"));
				})
				.then(r => {
					frappe.dom.unfreeze();
					if (!r.message) {
						frappe.throw(__('There were errors creating Tour Schedule'));
					}
					const { tour_schedules } = r.message;
					if (tour_schedules) {
						const tour_schedules_html = tour_schedules.map(c => `
							<tr>
								<td><a href="/app/tour-schedule/${c.name}">${c.name}</a></td>
								<td>${c.schedule_date}</td>
							</tr>
						`).join('');

						const html = `
							<table class="table table-bordered">
								<caption>${__('Following tour schedules were created')}</caption>
								<thead><tr><th>${__("Tour")}</th><th>${__("Date")}</th></tr></thead>
								<tbody>
									${tour_schedules_html}
								</tbody>
							</table>
						`;

						frappe.msgprint(html);
					}
				});
		});
	},
	render_days: function(frm) {
		const days_html = $('<div class="days-editor">').appendTo(
			frm.fields_dict.days_html.wrapper
		);

		if (!frm.days) {
			frm.days = frappe.ui.form.make_control({
				parent: days_html,
				df: {
					fieldname: "days",
					fieldtype: "MultiCheck",
					select_all: true,
					columns: 4,
					options: [
						{
							label: __("Monday"),
							value: "Monday",
							checked: 0,
						},
						{
							label: __("Tuesday"),
							value: "Tuesday",
							checked: 0,
						},
						{
							label: __("Wednesday"),
							value: "Wednesday",
							checked: 0,
						},
						{
							label: __("Thursday"),
							value: "Thursday",
							checked: 0,
						},
						{
							label: __("Friday"),
							value: "Friday",
							checked: 0,
						},
						{
							label: __("Saturday"),
							value: "Saturday",
							checked: 0,
						},
						{
							label: __("Sunday"),
							value: "Sunday",
							checked: 0,
						},
					],
				},
				render_input: true,
			});
		}
	}
});
