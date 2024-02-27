$(document).ready(function () {
  var hotelsBackage = 1;
  var toursBackage = 1;
  var transfersBackage = 1;

  var hotels = 1;
  var tours = 1;
  var transfers = 1;

  var currentDate = new Date();
  var today = currentDate.toISOString().slice(0, 10);




  $(document).on("change", ".children-select", function () {

    var selectedValue = $(this).val();
    var row = $(this).data('row');
    var className = 'ages' + row;

    var newSelect = "";

    if ($(this).data('type') == 'transfer') {
      var row2 = $(this).data('row2');
      className = 'ages' + row2;

      for (var i = 1; i <= selectedValue; i++) {
        newSelect += `
          <div class="search_item col-lg-4">
              <div>Child #${i} Age</div>
              <div class="form-group tm-form-element tm-form-element-2 custom-input p-0">
                  <select class="form-group tm-form-element tm-form-element-2 custom-input"  name="transfer[${row}][children][${row2}][${i - 1}]">
                          <option selected disabled hidden>
                           Age
                          </option>
                          <option value="1">1</option>
                          <option value="2">2</option>
                          <option value="3">3</option>
                          <option value="4">4</option>
                          <option value="5">5</option>
                          <option value="6">6</option>
                          <option value="6">6</option>
                          <option value="7">7</option>
                          <option value="8">8</option>
                          <option value="9">9</option>
                          <option value="10">10</option>
                          <option value="11">11</option>
                          <option value="12">12</option>
                        </select>
              </div>
          </div>
      `;
      }



      $(this).closest(".row").find("." + className).html(newSelect);


    }
    else if ($(this).data('type') == 'tour') {


      for (var i = 1; i <= selectedValue; i++) {
        newSelect += `
          <div class="search_item col-lg-4">
              <div>Child #${i} Age</div>
              <div class="form-group tm-form-element tm-form-element-2 custom-input p-0">
                  <select class="form-group tm-form-element tm-form-element-2 custom-input"  name="tour[${row}][children][${row2}][${i - 1}]">
                          <option selected disabled hidden>
                           Age
                          </option>
                          <option value="1">1</option>
                          <option value="2">2</option>
                          <option value="3">3</option>
                          <option value="4">4</option>
                          <option value="5">5</option>
                          <option value="6">6</option>
                          <option value="6">6</option>
                          <option value="7">7</option>
                          <option value="8">8</option>
                          <option value="9">9</option>
                          <option value="10">10</option>
                          <option value="11">11</option>
                          <option value="12">12</option>
                        </select>
              </div>
          </div>
      `;
      }

      $(this).closest(".row").find("." + className).html(newSelect);
    }
    else {


      for (var i = 1; i <= selectedValue; i++) {
        newSelect += `
          <div class="search_item col-lg-4">
              <div>Child #${i} Age</div>
              <div class="form-group tm-form-element tm-form-element-2 custom-input p-0">
                  <select class="form-group tm-form-element tm-form-element-2 custom-input"  name="hotel[${row}][children][${row2}][${i - 1}]">
                          <option selected disabled hidden>
                           Age
                          </option>
                          <option value="1">1</option>
                          <option value="2">2</option>
                          <option value="3">3</option>
                          <option value="4">4</option>
                          <option value="5">5</option>
                          <option value="6">6</option>
                          <option value="6">6</option>
                          <option value="7">7</option>
                          <option value="8">8</option>
                          <option value="9">9</option>
                          <option value="10">10</option>
                          <option value="11">11</option>
                          <option value="12">12</option>
                        </select>
              </div>
          </div>
      `;
      }

      console.log(".room" + $(this).data('row'));
      console.log(className);
      $(this).closest(".room" + $(this).data('row')).find("." + className).html(newSelect);
    }
  });


  $(document).on("change", ".rooms_select", function () {
    var selectedValue = $(this).val();
    var newSelect = "";
    hotel = $(this).data('hotel');

    for (var i = 1; i <= selectedValue; i++) {
      newSelect += `

        <h4 class="p-2">Room #${i}</h4>
      <div class="row w-100 px-2 px-2 room${i}">
      <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div
                            class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input"
                              name="hotel[${hotel}][rooms][${i - 1}][adults]" data-row="ages${i - 1}">
                              <option selected disabled hidden>
                               Adults
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-3">
                          <div>Children</div>
                          <div
                            class="form-group tm-form-element tm-form-element-2 custom-input p-1">
                            <select data-row="${i}"
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              name="hotel[${hotel}][rooms][${i - 1}][children]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                         <div class="ages${i} row px-3 w-100">

                        </div>
                      </div>

                        
      `;
    }


    className = $(this).data('row');
    console.log("." + className);

    $(this).closest(".row").find("." + className).html(newSelect);

  });



  $(".nationality_select").select2({
    theme: "bootstrap-5",
    // placeholder: "Select nationality",
    width: "100%",
    templateResult: formatOption

  });

  // $(".location_select").select2({
  //   theme: "bootstrap-5",
  //   // placeholder: "Select location",
  //   width: "100%",
  //   templateResult: formatOption


  // });


 


  $(".transfer_dropoff_select").select2({
    ajax: {
      url: 'https://api.github.com/orgs/select2/repos',
      dataType: 'json',
      delay: 250,
      data: function (params) {
        return {
          search: params.term,
          pickup: $(this).closest(".row").find(".transfer_pickup_select").val(),
          type: 'public'
        };
      },
      processResults: function (data) {
        var options = data.map(function (repo) {
          return {
            id: repo.id,
            text: repo.name
          };
        });

        return {
          results: options
        };
      },
      cache: true
    },
    // minimumInputLength: 1,
    templateResult: formatOption
  });




  $(".transfer_pickup_select").select2({
    ajax: {
      url: 'https://api.github.com/orgs/select2/repos',
      dataType: 'json',
      delay: 250,
      data: function (params) {
        return {
          search: params.term,
          type: 'public'
        };


      },
      processResults: function (data) {
        var options = data.map(function (repo) {
          return {
            id: repo.id,
            text: repo.name
          };
        });

        return {
          results: options
        };
      },
      cache: true
    },
    // minimumInputLength: 1,
    templateResult: formatOption

  });




  function formatOption(option) {
    var $option = $(
      '<div><strong>' + option.text + '</strong></div><span class="px-2 small">' + option.title + '</span class="px-2 small">'
    );
    return $option;
  };

  var currentDate = new Date();
  var today = currentDate.toISOString().slice(0, 10);

  $(".datepicker").prop("min", today);





  $('form').submit(function () {
    var allFieldsFilled = true;

    // Iterate over each input field
    $(this).find('input, select').each(function () {
      if ($(this).val() === '') {
        allFieldsFilled = false;
        return false;
      }
    });

    if (!allFieldsFilled) {

      toastr.error('Please Fill all fields', 'Error', {
        positionClass: 'toast-bottom-left',
        timeOut: 2000
      });

      return false;
    }

    return true;
  });



  $(document).on("change", ".transfer_pickup_select , .transfer_dropoff_select , .transfer_type , .transfer_date", function () {

    var parent = $(this).closest(".row");

    if (parent.find('.transfer_pickup_select').val() && parent.find('.transfer_dropoff_select').val() &&
      parent.find('.transfer_type').val() && parent.find('.transfer_date').val()) {



if (parent.find('.transfer_type ').val()  == "group") {


    var row = $(this).data("row");
    var row2 = $(this).data("row2");

   parent.find(".transfer_type_cont").html(`
    <div class="search_item mx-1 col-lg-5 m-2">
    <div>Allowed Flights</div>
    <div class="form-group tm-form-element tm-form-element-2 custom-input">
      <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select transfer_flight_type"
        name="transfer[${row}][flight_type][${row2}]">
        <option value="" selected disabled>Select Flight</option>
        <option value="flight1">flight1</option>
        <option value="flight2">flight2</option>
      </select>
    </div>
  </div>
    `);
  } else {
    parent.find(".transfer_type_cont").html(``);
  }




      //call api here





      // get api response to append to select: 


      // data.forEach(element => {
      //   parent.find('.transfer_flight_type').html(`
      //   <option value="${element.id}">${element.name}</option>`)
      // });




    }

  });



  $(document).on("change", ".tour_check_out , .tour_check_in , .tour_type_select, .tour_location_select", function () {

var parent = $(this).parent().closest(".row");

if (parent.find('.tour_check_out').val() && parent.find('.tour_check_in').val() &&
parent.find('.tour_type_select').val() && parent.find('.tour_location_select').val()) {
  var i = parent.find('.custom-check').data("row");
  
  parent.find('.custom-check').html(`
  <div class="custom-check-success">
                            <input type="checkbox" class="checkbox" name="checkbox" id="checkbox${i}-1" />
                            <label for="checkbox${i}-1">First Tour</label>
                            <div class="funky-info" data-toggle="modal" data-target="#infoModal" data-tour="">
                              <i class="fa fa-info-circle fa-x1" aria-hidden="true"></i>
                            </div>
                          </div>

                          <div class="custom-check-success">
                            <input type="checkbox" name="checkbox"  class="checkbox"id="checkbox${i}-2" />
                            <label for="checkbox${i}-2">Seond Tour</label>
                            <div class="funky-info" data-toggle="modal" data-target="#infoModal" data-tour="">
                              <i class="fa fa-info-circle fa-x1" aria-hidden="true"></i>
                            </div>
                          </div>

                          <div class="custom-check-success">
                            <input type="checkbox" name="checkbox"  class="checkbox" id="checkbox${i}-3" />
                            <label for="checkbox${i}-3">Third Tour

                            </label>
                            <div class="funky-info" data-toggle="modal" data-target="#infoModal" data-tour="">
                              <i class="fa fa-info-circle fa-x1" aria-hidden="true"></i>
                            </div>

                          </div>
`);
}else{
  parent.find('.custom-check').html(``);
}
});



$(document).on("change", ".checkbox", function () {

var date1 = new Date($(this).parent().closest('.row').find(".tour_check_in").val());
var date2 = new Date($(this).parent().closest('.row').find(".tour_check_out").val());

  var differenceInMilliseconds = date2 - date1;
  var differenceInDays = differenceInMilliseconds / (1000 * 60 * 60 * 24);
  if(differenceInDays === 0){
    differenceInDays=1;
  }
console.log(differenceInDays)
  var checkboxes = $(this).parent().closest('.custom-check').find('.checkbox');
  var checkedCheckboxes = checkboxes.filter(':checked');
  var uncheckedCheckboxes = checkboxes.not(':checked');

  if (checkedCheckboxes.length === differenceInDays) {
    uncheckedCheckboxes.siblings('label').addClass('disabledCheck');
    uncheckedCheckboxes.prop('disabled', true);

  } else {
    uncheckedCheckboxes.siblings('label').removeClass('disabledCheck');
    uncheckedCheckboxes.prop('disabled', false);    
  }
  if (checkedCheckboxes.length > differenceInDays) {
    uncheckedCheckboxes.siblings('label').removeClass('disabledCheck');
    uncheckedCheckboxes.prop('disabled', false);    
      }
});




  // $(document).on("change", ".tour_location_select , .tour_check_in , .tour_check_out ", function () {


  //   var parent = $(this).closest(".row");

  //   if (parent.find('.tour_location_select').val() && parent.find('.tour_check_in').val() &&
  //     parent.find('.tour_check_out').val()) {


        



      //call api here






      // get api response to append to select: 


      // data.forEach(element => {
      //   parent.find('.transfer_flight_type').html(`
      //   <option value="${element.id}">${element.name}</option>`)
      // });




  //   }

  // });





  $(".datepicker").prop("min", today);

  $(".add_booking").on("click", function () {
    var target = $(this).data("target");

    if ($(this).data("button") == "hotel") {
      $("#" + target).append(
        `
  <div class="booking_cont col-lg-6">
  <div id="hotel_booking${hotels}" class="row justify-content-start align-items-center p-0 m-0 search_panel_content flex-row">
  <div class="search_item col-lg-12">
 

<div class="modal-header p-0">
        <h5 class="modal-title" id="exampleModalLongTitle">Hotel Booking <span class="hotelsCounter">#` +
        (hotels + 1) +`</span>
        </h5>
        <button type="button" class="close close-btn" data-cart="hotel" aria-label="Close">
        <span aria-hidden="true">×</span>
        </button>
  </div>
</div>
    <div class="search_item col-lg-5">
      <div>
        Location
        <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
      </div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
      <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
      <select class="form-group tm-form-element tm-form-element-2 custom-input location_select"
        name="hotel[${hotels}][location]">
        <option value="" selected disabled>Select location</option>

        <option value="Jordan">Istanbul</option>

        <option value="Istanbul">Istanbul</option>
        <option value="Adana">Adana</option>
        <option value="Antalya">Antalya</option>
      </select>

    </div>
    </div>

    <div class="search_item mx-1 col-lg-5 ">
      <div>Nationality</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
        <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select" name="hotel[${hotels}][nationality]">
        <option value="" selected disabled>Select nationality</option>
          <option value="Jordan">Jordan</option>
        </select>
      </div>
    </div>

    <div class="search_item col-lg-5 ">
      <div>check in</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
        <input type="date" class="search_input bg-none datepicker checkin" placeholder="YYYY-MM-DD" name="hotel[${hotels}][check_in]">
      </div>
    </div>

    <div class="search_item mx-2 col-lg-5 ">
      <div>check out</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
        <input type="date" class="search_input bg-none datepicker checkout" placeholder="YYYY-MM-DD" name="hotel[${hotels}][check_out]">
      </div>
    </div>

    <div class="search_item col-lg-3">
      <div>Room</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
        <select class="form-group tm-form-element tm-form-element-2 custom-input rooms_select p-1" name="hotel[${hotels}][rooms][0[count]" data-row="rooms${hotels}" data-hotel="${hotels}">
          <option selected="" disabled="" hidden="">Rooms</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>
    </div>
    <!-- <div class="search_item col-lg-3">
      <div>Adults</div>
      <div
        class="form-group tm-form-element tm-form-element-2 custom-input"
      >
        <select
          class="form-group tm-form-element tm-form-element-2 custom-input p-1"
          name="hotel[${hotels}][rooms][0][adults]"
        >
          <option selected disabled hidden>Adults</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>
    </div>

    <div class="search_item col-lg-5">
      <div>Children</div>
      <div
        class="form-group tm-form-element tm-form-element-2 custom-input  p-1"
      >
        <select  class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
          name="hotel[${hotels}][rooms][0][children]"
        >
          <option selected disabled hidden>
            Children
          </option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>
    </div> -->


    <div class="rooms${hotels} row px-3 w-100"></div>
  </div>
</div>
        `
      );
      hotels += 1;
    } else if ($(this).data("button") == "hotelsBackage") {
      $("#" + target).append(
        `
  <div class="booking_cont col-lg-6">
  <div id="hotel_booking${hotelsBackage}" class="row justify-content-start align-items-center p-0 m-0 search_panel_content flex-row">
  <div class="search_item col-lg-12">
 

<div class="modal-header p-0">
        <h5 class="modal-title" id="exampleModalLongTitle">Hotel Booking  <span class="hotelsBackageCounter">#` +
        (hotelsBackage + 1) +`</span>
        </h5>
        <button type="button" class="close close-btn" data-cart="hotelBackage" aria-label="Close">
        <span aria-hidden="true">×</span>
        </button>
  </div>
</div>
    <div class="search_item col-lg-5">
      <div>
        Location
        <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
      </div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
      <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
      <select class="form-group tm-form-element tm-form-element-2 custom-input location_select"
        name="hotel[${hotelsBackage}][location]">
        <option value="" selected disabled>Select location</option>

        <option value="Jordan">Istanbul</option>

        <option value="Istanbul">Istanbul</option>
        <option value="Adana">Adana</option>
        <option value="Antalya">Antalya</option>
      </select>

    </div>
    </div>

    <div class="search_item mx-1 col-lg-5 ">
      <div>Nationality</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
        <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select" name="hotel[${hotelsBackage}][nationality]">
        <option value="" selected disabled>Select nationality</option>
          <option value="Jordan">Jordan</option>
        </select>
      </div>
    </div>

    <div class="search_item col-lg-5 ">
      <div>check in</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
        <input type="date" class="search_input bg-none datepicker checkin" placeholder="YYYY-MM-DD" name="hotel[${hotelsBackage}][check_in]">
      </div>
    </div>

    <div class="search_item mx-2 col-lg-5 ">
      <div>check out</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input">
        <input type="date" class="search_input bg-none datepicker checkout" placeholder="YYYY-MM-DD" name="hotel[${hotelsBackage}][check_out]">
      </div>
    </div>

    <div class="search_item col-lg-3">
      <div>Room</div>
      <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
        <select class="form-group tm-form-element tm-form-element-2 custom-input rooms_select p-1" name="hotel[${hotelsBackage}][rooms][0[count]" data-row="rooms${hotelsBackage}" data-hotel="${hotelsBackage}">
          <option selected="" disabled="" hidden="">Rooms</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>
    </div>
    <!-- <div class="search_item col-lg-3">
      <div>Adults</div>
      <div
        class="form-group tm-form-element tm-form-element-2 custom-input"
      >
        <select
          class="form-group tm-form-element tm-form-element-2 custom-input p-1"
          name="hotel[${hotelsBackage}][rooms][0][adults]"
        > 
          <option selected disabled hidden>Adults</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>
    </div>

    <div class="search_item col-lg-5">
      <div>Children</div>
      <div
        class="form-group tm-form-element tm-form-element-2 custom-input  p-1"
      >
        <select  class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
          name="hotel[${hotelsBackage}][rooms][0][children]"
        >
          <option selected disabled hidden>
            Children
          </option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>
    </div> -->


    <div class="rooms${hotelsBackage} row px-3 w-100"></div>
  </div>
</div>
        `
      );
      hotelsBackage += 1;
    } else if ($(this).data("button") == "transfer") {
      $("#" + target).append(` 
      <div class="booking_cont col-lg-6">
                      <div class="row justify-content-start align-items-center p-0 m-0 search_panel_content flex-row">

                        <div class="search_item col-lg-12">
                          <div class="modal-header p-0">
                            <h5 class="modal-title" id="exampleModalLongTitle">Transfer Booking <span class="transfersCounter">#${transfers+1}</span></h5>
                            <div class="ways px-4">
                              <div class="btn btn-success font-weight-bold one-way way-type" data-row="${transfers}" data-way="one-way"><i
                                  class="fa fa-long-arrow-right" aria-hidden="true" ></i> One Way</div>
                              <div class="btn font-weight-bold two-way way-type" data-row="${transfers}"  data-way="two-way"><i
                                  class="fa fa-exchange" aria-hidden="true"></i> Two Way</div>
                                  <input type="hidden" name="transfer[${transfers}][type]" value="oneway"/>
                            </div>
                            <button type="button" class="close close-btn" data-cart="transfer" aria-label="Close">
                            <span aria-hidden="true">×</span>
                            </button>
                          </div>
                        </div>



                        <div class="search_item col-lg-5">
                          <div>
                            Pickup
                            <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_pickup_select w-100"
                              name="transfer[${transfers}][pickup_location][0]" data-row="${transfers}"  data-row2="0">
                              <option value="" selected disabled>Select pickup</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5">
                          <div>
                            Drop off
                            <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_dropoff_select w-100"
                              name="transfer[${transfers}][dropoff_location][0]" data-row="${transfers}"  data-row2="0">
                              <option value="" selected disabled>Select drop off</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5 ">
                          <div>Date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <input type="date" class="search_input bg-none datepicker checkin transfer_date check_in search_input" placeholder="YYYY-MM-DD" name="transfer[${transfers}][date][0]" data-row="${transfers}"  data-row2="0"/>
                          </div>
                        </div>



                        <div class="search_item mx-1 col-lg-5">
                        <div>Type</div>
                        <div class="form-group tm-form-element tm-form-element-2 custom-input">
                          <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select transfer_type" data-row="${transfers}" data-row2="0"
                            name="transfer[${transfers}][type][0]" data-row="${transfers}"  data-row2="0">
                            <option value="" selected disabled>Select type</option>
                            <option value="group">Group</option>
                            <option value="vip">VIP</option>
                          </select>
                        </div>
                      </div>
                      
                      <div class="transfer_type_cont row px-3 w-100"></div>



                        <div class="search_item mx-2 col-lg-5 ">
                          <div>Flight No#</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input ">
                            <input type="text" class="search_input bg-none" placeholder="Flight #"
                              name="transfer[${transfers}][flight][0]" />
                          </div>
                        </div>



                        <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input p-1"
                              name="transfer[${transfers}][adults][0]">
                              <option selected disabled hidden>Adults</option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-5">
                          <div>Children</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              data-row="${transfers}" data-row2="0" data-type="transfer" name="transfer[${transfers}][children_count][0]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                        <div class="ages0 row px-3 w-100"></div>

                        <div class="back row px-3 w-100">
                        
                        
                        
                        <hr/>

                        <div class="search_item col-lg-5">
                          <div>
                            Pickup
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_pickup_select w-100"
                              name="transfer[${transfers}][pickup_location][1]" data-row="${transfers}"  data-row2="1">
                              <option value="" selected disabled>Select pickup</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5">
                          <div>
                            Drop off
                            <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_dropoff_select w-100"
                              name="transfer[${transfers}][dropoff_location][1]" data-row="${transfers}"  data-row2="1">
                              <option value="" selected disabled>Select drop off</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5 ">
                          <div>Date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <input type="date" class="search_input bg-none datepicker checkin transfer_date check_in search_input" placeholder="YYYY-MM-DD" name="transfer[${transfers}][date][1]" data-row="${transfers}"  data-row2="1"/>
                          </div>
                        </div>


                        <div class="search_item mx-1 col-lg-5">
                        <div>Type</div>
                        <div class="form-group tm-form-element tm-form-element-2 custom-input">
                          <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select transfer_type" data-row="${transfers}" data-row2="1"
                            name="transfer[${transfers}][type][1]">
                            <option value="" selected disabled>Select type</option>
                            <option value="group">Group</option>
                            <option value="vip">VIP</option>
                          </select>
                        </div>
                      </div>
                      
                      <div class="transfer_type_cont row px-3 w-100"></div>


                        <div class="search_item mx-2 col-lg-5 ">
                          <div>Flight No#</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input ">
                            <input type="text" class="search_input bg-none" placeholder="Flight #"
                              name="transfer[${transfers}][flight][1]" data-row="${transfers}"  data-row2="1" />
                          </div>
                        </div>



                        <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input p-1"
                              name="transfer[${transfers}][adults][1]">
                              <option selected disabled hidden>Adults</option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-5">
                          <div>Children</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              data-row="${transfers}" data-row2="1" data-type="transfer" name="transfer[${transfers}][children_count][1]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                        <div class="ages1 row px-3 w-100"></div>
                        
                        
                        
                        </div>

                      </div>
                    </div>
                    `);

      transfers += 1;
    } else if ($(this).data("button") == "transfersBackage") {
      $("#" + target).append(`
      <div class="booking_cont col-lg-6">
                      <div class="row justify-content-start align-items-center p-0 m-0 search_panel_content flex-row">

                        <div class="search_item col-lg-12">
                          <div class="modal-header p-0">
                            <h5 class="modal-title" id="exampleModalLongTitle">Transfer Booking <span class="transfersBackageCounter">#${transfersBackage + 1}</span></h5>
                            <div class="ways px-4">
                              <div class="btn btn-success font-weight-bold one-way way-type" data-row="${transfersBackage}" data-way="one-way"><i
                                  class="fa fa-long-arrow-right" aria-hidden="true" ></i> One Way</div>
                              <div class="btn font-weight-bold two-way way-type" data-row="${transfersBackage}" data-way="two-way"><i
                                  class="fa fa-exchange" aria-hidden="true"></i> Two Way</div>
                                  <input type="hidden" name="transfer[${transfersBackage}][type]" value="oneway"/>
                            </div>
                            <button type="button" class="close close-btn" data-cart="transferBackage" aria-label="Close">
                            <span aria-hidden="true">×</span>
                            </button>
                          </div>
                        </div>



                        <div class="search_item col-lg-5">
                          <div>
                            Pickup
                            <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_pickup_select w-100"
                              name="transfer[${transfersBackage}][pickup_location][0]">
                              <option value="" selected disabled>Select pickup</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5">
                          <div>
                            Drop off
                            <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_dropoff_select w-100"
                              name="transfer[${transfersBackage}][dropoff_location][0]">
                              <option value="" selected disabled>Select drop off</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5 ">
                          <div>Date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <input type="date" class="search_input bg-none datepicker checkin transfer_date check_in search_input" placeholder="YYYY-MM-DD" name="transfer[${transfersBackage}][date][0]" />
                          </div>
                        </div>



                        <div class="search_item mx-1 col-lg-5">
                        <div>Type</div>
                        <div class="form-group tm-form-element tm-form-element-2 custom-input">
                          <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select transfer_type" data-row="${transfersBackage}" data-row2="0"
                            name="transfer[${transfersBackage}][type][0]">
                            <option value="" selected disabled>Select type</option>
                            <option value="group">Group</option>
                            <option value="vip">VIP</option>
                          </select>
                        </div>
                      </div>
                      
                      <div class="transfer_type_cont row px-3 w-100"></div>



                        <div class="search_item mx-2 col-lg-5 ">
                          <div>Flight No#</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input ">
                            <input type="text" class="search_input bg-none" placeholder="Flight #"
                              name="transfer[${transfersBackage}][flight][0]" />
                          </div>
                        </div>



                        <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input p-1"
                              name="transfer[${transfersBackage}][adults][0]">
                              <option selected disabled hidden>Adults</option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-5">
                          <div>Children</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              data-row="${transfersBackage}" data-row2="0" data-type="transfer" name="transfer[${transfersBackage}][children_count][0]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                        <div class="ages0 row px-3 w-100"></div>

                        <div class="back row px-3 w-100">
                        <hr/>

                        <div class="search_item col-lg-5">
                          <div>
                            Pickup
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_pickup_select w-100"
                              name="transfer[${transfersBackage}][pickup_location][1]">
                              <option value="" selected disabled>Select pickup</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5">
                          <div>
                            Drop off
                            <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_dropoff_select w-100"
                              name="transfer[${transfersBackage}][dropoff_location][1]">
                              <option value="" selected disabled>Select drop off</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5 ">
                          <div>Date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <input type="date" class="search_input bg-none datepicker checkin transfer_date check_in search_input" placeholder="YYYY-MM-DD" name="transfer[${transfersBackage}][date][1]" />
                          </div>
                        </div>


                        <div class="search_item mx-1 col-lg-5">
                        <div>Type</div>
                        <div class="form-group tm-form-element tm-form-element-2 custom-input">
                          <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select transfer_type" data-row="${transfersBackage}" data-row2="1"
                            name="transfer[${transfersBackage}][type][1]">
                            <option value="" selected disabled>Select type</option>
                            <option value="group">Group</option>
                            <option value="vip">VIP</option>
                          </select>
                        </div>
                      </div>
                      
                      <div class="transfer_type_cont row px-3 w-100"></div>


                        <div class="search_item mx-2 col-lg-5 ">
                          <div>Flight No#</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input ">
                            <input type="text" class="search_input bg-none" placeholder="Flight #"
                              name="transfer[${transfersBackage}][flight][1]" />
                          </div>
                        </div>



                        <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input p-1"
                              name="transfer[${transfersBackage}][adults][1]">
                              <option selected disabled hidden>Adults</option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-5">
                          <div>Children</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              data-row="${transfersBackage}" data-row2="1" data-type="transfer" name="transfer[${transfersBackage}][children_count][1]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                        <div class="ages1 row px-3 w-100"></div>
                        </div>

                      </div>
                    </div>
                    `);

      transfersBackage += 1;
    } else if ($(this).data("button") == "tour") {
      $("#" + target).append(` 
    <div class="booking_cont col-lg-6">
                      <div class="row justify-content-start align-items-center p-0 m-0 search_panel_content flex-row">

                        <div class="search_item col-lg-12">
                          <div class="modal-header p-0">
                            <h5 class="modal-title" id="exampleModalLongTitle">Tour Booking <span class="toursCounter">#${tours + 1}</span></h5>
                            <button type="button" class="close close-btn" data-cart="tour" aria-label="Close">
                            <span aria-hidden="true">×</span>
                            </button>
                          </div>
                        </div>


                        <div class="search_item mx-1 col-lg-5">
                          <div>Type</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select tour_type_select"
                              name="tour[${tours}][type]">
                              <option value="" selected disabled>Select type</option>
                              <option value="vip">VIP</option>
                            </select>
                          </div>
                        </div>


                        <div class="search_item col-lg-5">
                          <div>
                            Location
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input location_select w-100 tour_location_select" 
                              name="tour[${tours}][location_location]">
                              <option value="" selected disabled>Select location</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>



                        <div class="search_item col-lg-5 ">
                          <div>Start date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                          <input type="date" class="search_input bg-none datepicker check_in search_input tour_check_in" placeholder="YYYY-MM-DD"
                          name="tour[${tours}][start_date]" />                          </div>
                        </div>

                        <div class="search_item mx-2 col-lg-5 ">
                          <div>End date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input ">
                          <input type="date" class="search_input bg-none checkout tour_check_out "
                          placeholder="YYYY-MM-DD" name="tour[${tours}][end_date]" />
                          </div>
                        </div>


                        





                        <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input p-1 tour_check_out"
                              name="tour[${tours}][adults]">
                              <option selected disabled hidden>Adults</option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-5">
                          <div>Children</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              data-row="${tours}" data-type="tour" name="tour[${tours}][children_count]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                        <div class="ages${tours} row px-3 w-100"></div>
                        <div class="custom-check w-100" data-row="tour-${tours}"></div>
                      </div>
                    </div>
`);

      tours += 1;
    } else if ($(this).data("button") == "toursBackage") {
      $("#" + target).append(` 
    <div class="booking_cont col-lg-6">
                      <div class="row justify-content-start align-items-center p-0 m-0 search_panel_content flex-row">

                        <div class="search_item col-lg-12">
                          <div class="modal-header p-0">
                            <h5 class="modal-title" id="exampleModalLongTitle">Tour Booking <span class="toursBackageCounter">#${toursBackage + 1}</span></h5>
                            <button type="button" class="close close-btn" data-cart="tourBackage" aria-label="Close">
                               <span aria-hidden="true">×</span>
                            </button>
                          </div>
                        </div>


                        <div class="search_item mx-1 col-lg-5">
                          <div>Type</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select tour_type_select"
                              name="tour[${toursBackage}][type]">
                              <option value="" selected disabled>Select type</option>
                              <option value="vip">VIP</option>
                            </select>
                          </div>
                        </div>


                        <div class="search_item col-lg-5">
                          <div>
                            Location
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input location_select w-100 tour_location_select"
                              name="tour[${toursBackage}][location_location]">
                              <option value="" selected disabled>Select location</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>



                        <div class="search_item col-lg-5 ">
                          <div>Start date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                          <input type="date" class="search_input bg-none datepicker check_in search_input tour_check_in" placeholder="YYYY-MM-DD"
                          name="tour[${toursBackage}][start_date]" />
                          </div>
                        </div>

                        <div class="search_item mx-2 col-lg-5 ">
                          <div>End date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input ">
                          <input type="date" class="search_input bg-none checkout tour_check_out "
                          placeholder="YYYY-MM-DD" name="tour[${toursBackage}][end_date]" />
                              
                          </div>
                        </div>


                        





                        <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input p-1"
                              name="tour[${toursBackage}][adults]">
                              <option selected disabled hidden>Adults</option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-5">
                          <div>Children</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              data-row="${toursBackage}" data-type="tour" name="tour[${toursBackage}][children_count]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                        <div class="ages${toursBackage} row px-3 w-100"></div>
                         <div class="custom-check w-100" data-row="tourBackage-${toursBackage}"></div>
                      </div>
                    </div>
`);

      toursBackage += 1;
    }

    $(".nationality_select").select2({
      theme: "bootstrap-5",
      // placeholder: "Select nationality",
      width: "100%",
    });

    $(".location_select").select2({
      theme: "bootstrap-5",
      // placeholder: "Select location",
      width: "100%",
    });

    $(".transfer_dropoff_select").select2({
      ajax: {
        url: "https://api.github.com/orgs/select2/repos",
        dataType: "json",
        delay: 250,
        data: function (params) {
          return {
            search: params.term,
            pickup: $(this)
              .closest(".row")
              .find(".transfer_pickup_select")
              .val(),
            type: "public",
          };
        },
        processResults: function (data) {
          var options = data.map(function (repo) {
            return {
              id: repo.id,
              text: repo.name,
            };
          });

          return {
            results: options,
          };
        },
        cache: true,
      },
      // minimumInputLength: 1,
      templateResult: formatOption,
    });

    $(".transfer_pickup_select").select2({
      ajax: {
        url: "https://api.github.com/orgs/select2/repos",
        dataType: "json",
        delay: 250,
        data: function (params) {
          return {
            search: params.term,
            type: "public",
          };
        },
        processResults: function (data) {
          var options = data.map(function (repo) {
            return {
              id: repo.id,
              text: repo.name,
            };
          });

          return {
            results: options,
          };
        },
        cache: true,
      },
      // minimumInputLength: 1,
      templateResult: formatOption,
    });

    $(this).parent().parent().find(".arrows-cont").removeClass("d-none");
    $(this)
      .parent()
      .parent()
      .find(".scrollabel")
      .animate({ scrollLeft: "+=500" }, 1000);

    $(".datepicker").prop("min", today);
  });

  $(".left_arrow_scrolle").on("click", function () {
    $(this)
      .parent()
      .parent()
      .find(".scrollabel")
      .animate({ scrollLeft: "-=460px" }, 1000);
  });

  $(".right_arrow_scrolle").on("click", function () {
    $(this)
      .parent()
      .parent()
      .find(".scrollabel")
      .animate({ scrollLeft: "+=460" }, 1000);
  });

  $(document).on("change", ".datepicker", function () {
    if ($(this).hasClass("checkin")) {
      console.log($(this).val());
      $(this).closest(".row").find(".checkout").val("");
      var currentDate = new Date($(this).val());
      currentDate.setDate(currentDate.getDate() + 1);

      var nextDay = currentDate.toISOString().slice(0, 10);

      $(this).closest(".row").find(".checkout").prop("min", nextDay);
      $(this).closest(".row").find(".checkout").val(nextDay);
    }else{
      $(this).closest(".row").find(".checkout").val("");
      var currentDateTemp = new Date($(this).val());
      currentDateTemp.setDate(currentDateTemp.getDate());
      
      var currentDate = currentDateTemp.toISOString().slice(0, 10);


      $(this).closest(".row").find(".checkout").prop("min", currentDate);
    }
  });

  $(document).on("click", ".booking_cont .close-btn", function () {

    if($(this).data("cart") == "hotelBackage"){
      if(hotelsBackage > 1){
        $(this).closest(".booking_cont").remove();
        hotelsBackage--;
        resortCards('hotelsBackageCounter');
      }else{
        if(toursBackage > 0 && transfersBackage > 0){
          $(this).closest(".booking_cont").remove();
          hotelsBackage--;
        resortCards('hotelsBackageCounter');
        }
        else{
        toastr.error('Please set at least two programs', 'Error', {
          positionClass: 'toast-bottom-left',
          timeOut: 2000
        });
      }
      }
    }
    else if($(this).data("cart") == "tourBackage"){
      if(toursBackage > 1){
        $(this).closest(".booking_cont").remove();
        toursBackage--;
        resortCards('toursBackageCounter');
      }else{
        if(hotelsBackage > 0 && transfersBackage > 0){
          $(this).closest(".booking_cont").remove();
          toursBackage--;
        resortCards('toursBackageCounter');

        }
        else{
        toastr.error('Please set at least two programs', 'Error', {
          positionClass: 'toast-bottom-left',
          timeOut: 2000
        });
      }
      }
    }

    else if($(this).data("cart") == "transferBackage"){
      if(transfersBackage > 1){
        $(this).closest(".booking_cont").remove();
        transfersBackage--;
        resortCards('transfersBackageCounter');
      }else{
        if(hotelsBackage > 0 && toursBackage > 0){
          $(this).closest(".booking_cont").remove();
          transfersBackage--;
        resortCards('transfersBackageCounter');
        }
        else{
        toastr.error('Please set at least two programs', 'Error', {
          positionClass: 'toast-bottom-left',
          timeOut: 2000
        });
      }
      }
    }
    else if($(this).data("cart") == "hotel"){
      if(hotels > 1){
      $(this).closest(".booking_cont").remove();
      hotels--;
      resortCards('hotelsCounter');}
      else{
        toastr.error('Please set at least one programs', 'Error', {
          positionClass: 'toast-bottom-left',
          timeOut: 2000
        });
      }

    }
    else if($(this).data("cart") == "transfer"){
      if(transfers > 1){
      $(this).closest(".booking_cont").remove();
      transfers--;
      resortCards('transfersCounter');
      }
      else{
        toastr.error('Please set at least one programs', 'Error', {
          positionClass: 'toast-bottom-left',
          timeOut: 2000
        });
      }

     }

     else if($(this).data("cart") == "tour"){
     console.log("tours:"+tours);

      if(tours > 1){
      $(this).closest(".booking_cont").remove();
      tours--;
      resortCards('toursCounter');
      }
      else{
        toastr.error('Please set at least one programs', 'Error', {
          positionClass: 'toast-bottom-left',
          timeOut: 2000
        });
      }

     }


     console.log("hotels:"+hotels);
     console.log("transfer:"+transfers);


  });

  $(document).on("click", ".way-type", function () {
    var i = $(this).data("row");
    if ($(this).data("way") == "one-way") {
      console.log($(this).data("way"));
      $(this).closest(".booking_cont").find(".back").html(``);

      $(this).addClass("btn-success");

      $(this).parent().find(".two-way").removeClass("btn-success");
      $(this)
        .closest(".ways")
        .find('input[name="transfer[' + i + '][type]"]')
        .val("one_way");
    } else {
      $(this)
        .closest(".ways")
        .find('input[name="transfer[' + i + '][type]"]')
        .val("two_way");

      console.log(
        $(this)
          .parent()
          .find('input[name="transfer[' + i + '][type][1]"]')
          .remove()
      );

      $(this).closest(".booking_cont").find(".back").html(`

    <hr/>

                        <div class="search_item col-lg-5">
                          <div>
                            Pickup
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_pickup_select w-100"
                              name="transfer[${i}][pickup_location][1]">
                              <option value="" selected disabled>Select pickup</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5">
                          <div>
                            Drop off
                            <!-- <i class="fa fa-map-marker fa-2x tm-form-element-icon tm-color-primary"></i> -->
                          </div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <i class="fa fa-map-marker fa-1x mx-1 tm-form-element-icon tm-color-primary"></i>
                            <select
                              class="form-group tm-form-element tm-form-element-2 custom-input transfer_dropoff_select w-100"
                              name="transfer[${i}][dropoff_location][1]">
                              <option value="" selected disabled>Select drop off</option>
                              <option value="Istanbul" title="turkey">Istanbul</option>
                              <option value="Adana" title="turkey">Adana</option>
                              <option value="Antalya" title="turkey">Antalya</option>
                            </select>

                          </div>
                        </div>


                        <div class="search_item col-lg-5 ">
                          <div>Date</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <input type="date" class="search_input bg-none datepicker checkin check_in search_input" placeholder="YYYY-MM-DD" name="transfer[${i}][date][1]" />
                          </div>
                        </div>


                        <div class="search_item mx-1 col-lg-5">
                        <div>Type</div>
                        <div class="form-group tm-form-element tm-form-element-2 custom-input">
                          <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select transfer_type" data-row="${i}" data-row2="1"
                            name="transfer[${i}][type][1]">
                            <option value="" selected disabled>Select type</option>
                            <option value="group">Group</option>
                            <option value="vip">VIP</option>
                          </select>
                        </div>
                      </div>
                      
                      <div class="transfer_type_cont row px-3 w-100"></div>


                        <div class="search_item mx-2 col-lg-5 ">
                          <div>Flight No#</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input ">
                            <input type="text" class="search_input bg-none" placeholder="Flight #"
                              name="transfer[${i}][flight][1]" />
                          </div>
                        </div>



                        <div class="search_item col-lg-3">
                          <div>Adults</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input">
                            <select class="form-group tm-form-element tm-form-element-2 custom-input p-1"
                              name="transfer[${i}][adults][1]">
                              <option selected disabled hidden>Adults</option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>

                        <div class="search_item col-lg-5">
                          <div>Children</div>
                          <div class="form-group tm-form-element tm-form-element-2 custom-input  p-1">
                            <select
                              class="form-group tm-form-element tm-form-element-2 dropdown_item_select custom-input children-select"
                              data-row="${i}" data-row2="1" data-type="transfer" name="transfer[${i}][children_count][1]">
                              <option selected disabled hidden>
                                Children
                              </option>
                              <option value="1">1</option>
                              <option value="2">2</option>
                              <option value="3">3</option>
                            </select>
                          </div>
                        </div>
                        <div class="ages1 row px-3 w-100"></div>
                        `);

      $(".nationality_select").select2({
        theme: "bootstrap-5",
        // placeholder: "Select nationality",
        width: "100%",
        templateResult: formatOption,
      });

      $(".location_select").select2({
        theme: "bootstrap-5",
        // placeholder: "Select location",
        width: "100%",
        templateResult: formatOption,
      });

      $(".transfer_dropoff_select").select2({
        ajax: {
          url: "https://api.github.com/orgs/select2/repos",
          dataType: "json",
          delay: 250,
          data: function (params) {
            return {
              search: params.term,
              pickup: $(this)
                .closest(".row")
                .find(".transfer_pickup_select")
                .val(),
              type: "public",
            };
          },
          processResults: function (data) {
            var options = data.map(function (repo) {
              return {
                id: repo.id,
                text: repo.name,
              };
            });

            return {
              results: options,
            };
          },
          cache: true,
        },
        // minimumInputLength: 1,
        templateResult: formatOption,
      });

      $(".transfer_pickup_select").select2({
        ajax: {
          url: "https://api.github.com/orgs/select2/repos",
          dataType: "json",
          delay: 250,
          data: function (params) {
            return {
              search: params.term,
              type: "public",
            };
          },
          processResults: function (data) {
            var options = data.map(function (repo) {
              return {
                id: repo.id,
                text: repo.name,
              };
            });

            return {
              results: options,
            };
          },
          cache: true,
        },
        // minimumInputLength: 1,
        templateResult: formatOption,
      });

      $(this).addClass("btn-success");

      $(this).parent().find(".one-way").removeClass("btn-success");
    }

    function formatOption(option) {
      var $option = $(
        "<div><strong>" +
        option.text +
        '</strong></div><span class="px-2 small">' +
        option.title +
        '</span class="px-2 small">'
      );
      return $option;
    }
  });

  $(document).on("change", ".transfer_type", function () {
    // if ($(this).val() == "group") {
    //   console.log("group");
    //   var row = $(this).data("row");
    //   var row2 = $(this).data("row2");

    //   $(this).closest(".row").find(".transfer_type_cont").html(`
    //   <div class="search_item mx-1 col-lg-5 m-2">
    //   <div>Allowed Flights</div>
    //   <div class="form-group tm-form-element tm-form-element-2 custom-input">
    //     <select class="form-group tm-form-element tm-form-element-2 custom-input nationality_select transfer_flight_type"
    //       name="transfer[${row}][flight_type][${row2}]">
    //       <option value="" selected disabled>Select Flight</option>
    //       <option value="flight1">flight1</option>
    //       <option value="flight2">flight2</option>
    //     </select>
    //   </div>
    // </div>
    //   `);
    // } else {
    //   $(this).closest(".row").find(".transfer_type_cont").html(``);
    // }







  });



  function resortCards(card) {
    $('.' + card).each(function (index) {
        var counter = index + 1;

        $(this).html('#' + counter);
    });
}


});
