// Copyright (c) 2024, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tariff Creation Tool', {
	refresh: function(frm) {
		frm.disable_save()
		frm.add_custom_button(__('Generate Title'), function() {
			frm.events.generate_title(frm);
		});
		
		frm.add_custom_button(__('Create Tariff'), function() {
			frm.events.create_tariff(frm);
		});
		frm.add_custom_button(__('Fetch Data'), function() {
			frm.events.fetch_data(frm);
		});
		if (!frm.doc.updated_date){
			frm.set_value("updated_date", frappe.datetime.nowdate());
		}
		if(frm.doc.tariff_file){
			frm.add_custom_button(__('Download Tariff'), function() {
				var url =  frm.doc.tariff_file;
				window.open(url, '_blank');
			});
			frm.add_custom_button(__('Publish Tariff'), function() {
				frappe.confirm('Are you sure you want to proceed?',
				() => {
					frm.events.publish_tariff(frm);
				}, () => {
					// action to perform if No is selected
				})
			});
		
		}
	},
	publish_tariff: function(frm){
		frappe.call({
			"method": "tourism_portal.tourism_portal.doctype.tariff_creation_tool.tariff_creation_tool.publish_tariff",
			args: {
				"template": frm.doc.tariff_template,
				'tariff_file': frm.doc.tariff_file,
				'tariff_path': frm.doc.tariff_path,
				'title': frm.doc.title,
				'from_date': frm.doc.check_in_from_date,
				'to_date': frm.doc.check_in_to_date,
				'publish_from_date':  frm.doc.publish_from_date,
				'publish_to_date': frm.doc.publish_to_date,
				'company_class': frm.doc.company_class,
			},
			callback: (res)=> {
				console.log(res.message)
				if (res.message) {
					frappe.msgprint("Tariff Published Successfully");
				}else{
					frappe.msgprint("Error in publishing tariff");
				}
			}
		})
	},
	fetch_data: function(frm) {
		frappe.call({
			"method": "tourism_portal.tourism_portal.doctype.tariff_creation_tool.tariff_creation_tool.fetch_data",
			args: {
				"from_date": frm.doc.check_in_from_date,
				"to_date": frm.doc.check_in_to_date,
				"company_class": frm.doc.company_class,
				"template": frm.doc.tariff_template,
				"from_night": frm.doc.from_night,
				"to_night": frm.doc.to_night,
				"tariff_type": frm.doc.tariff_type
			},
			callback: (res)=> {
				console.log(res.message)
				if (res.message) {
					frm.events.set_tariff_data(frm, res.message);
				}else{
					frappe.msgprint("No data found for the selected dates");
				}
			}
		})
	},
	generate_title: function(frm) {
		frappe.call({
			"method": "tourism_portal.tourism_portal.doctype.tariff_creation_tool.tariff_creation_tool.generate_title",
			args: {
				"from_date": frm.doc.check_in_from_date,
				"to_date": frm.doc.check_in_to_date,
				"company_class": frm.doc.company_class,
				"template": frm.doc.tariff_template,
			},
			callback: (res)=> {
				console.log(res.message)
				if (res.message) {
					frm.doc.title = res.message;
					frm.refresh_field("title");
				}else{
					frappe.msgprint("No data found for the selected dates");
				}
			}
		})
	},
	set_tariff_data: function(frm, data) {
		frm.doc.hotels = [];
		for (var hotelId in data.hotels){
			for (var hotelPeriod in data.hotels[hotelId]){
				var hotel = data.hotels[hotelId][hotelPeriod];
				if (hotel){
					let row = frappe.model.add_child(frm.doc, "Tariff Creation Tool Hotels", "hotels");
					var hotelPro = null
					if (hotel['SGL']){
						hotelPro = hotel['SGL']
					}else if (hotel['DBL']){
						hotelPro = hotel['DBL']
					}else if (hotel['TRPL']){
						hotelPro = hotel['TRPL']
					}
					if(! hotelPro){
						console.log("Cannot find room acmnd")
						console.log(hotelId)
						console.log(hotelPeriod)
						continue
					} 
					row.hotel = hotelPro['hotel'];
					row.hotel_name = hotelPro['hotel_name'];
					row.special_period = hotelPro['special_period'];
					row.location = hotelPro['location'];
					row.hotel_stars = hotelPro['hotel_stars'];
					if (hotel['SGL'] && hotel['SGL']['selling_price']){
						row.single_price = hotel['SGL']['selling_price'];
					}else{
						row.single_price = 0;
					}
					if (hotel['DBL']&& hotel['DBL']['selling_price']){
						row.double_price = hotel['DBL']['selling_price'];
					}else{
						row.double_price = 0;
					}
					
					if(hotel['TRPL'] && hotel['TRPL']['selling_price']){
						row.triple_price = hotel['TRPL']['selling_price'];
					}else{
						row.triple_price = 0;
					}
				}else{
					console.log('Cannot find hotel')
					console.log(hotelId)
					console.log(hotelPeriod)
				}
				
				
				
			}
		}
		frm.refresh_field("hotels");
		
		
	},
	create_tariff: function(frm){
		frm.doc.tariff_file = "";
		frm.doc.file_path = "";
		frm.refresh_field("tariff_file");
		frappe.show_progress('Loading..', 50, 100, 'Please wait');
		frm.refresh()
		frappe.call({
			"method": "tourism_portal.tourism_portal.doctype.tariff_creation_tool.tariff_creation_tool.create_tariff",
			args: {
				"template": frm.doc.tariff_template,
				'hotels': frm.doc.hotels,
				"from_date": frm.doc.check_in_from_date,
				"to_date": frm.doc.check_in_to_date,
				'updated_date': frm.doc.updated_date,
			},
			callback: (res)=> {
				console.log(res.message)
				if (res.message) {
					frappe.show_progress('Loading..', 100, 100, 'Please wait');
					frappe.hide_progress();
					frm.doc.tariff_file = res.message.file;
					frm.doc.tariff_path = res.message.file_path
					frm.refresh_field("tariff_file");
					frm.refresh()
					frappe.msgprint("Tariff Created Successfully");
				}else{
					frappe.msgprint("Error in creating tariff");
				}
			}
		})
			
	}
});
