
  $(document).ready(function () {


    new ZlataLoader({
      id: 'loader',
      imgSrc: "images/plane.png",
      mode: 'single',
      lineWidth: 4
  });



    $(function() {
			$('[data-toggle="tooltip"]').tooltip()
		});




    $(".count").prop("disabled", true);

    var roomsMax =[3,2];
    var selectedRooms = [0,0];


	$(".tour_select").each(function () {
		var price =$(this).find("option:selected").data("price");
        $(this).data('prev', price);
    });
	
	
	$(".transfer_select").each(function () {
		var price =$(this).find("option:selected").data("price");
        $(this).data('prev', price);
    });

	
	$(document).on("click", ".plus", function () {
		var max=roomsMax[$(this).closest(".offers_grid").data("room")-1];
		var selected=selectedRooms[$(this).closest(".offers_grid").data("room")-1];
      if (selected < max) {
        $(this)
          .parent()
          .find(".count")
          .val(parseInt($(this).parent().find(".count").val()) + 1);
        $(this).parent().find(".count").removeClass("zero");

        if (
          $(this).parent().find(".count").val() >
          $(this).parent().find(".count").data("max")
        ) {
          $(this)
            .closest(".row")
            .find(".availability")
            .html(
              '<button type="button" class="btn btn-light askForAvailbity" data-id="'+$(this).data("room")+'" data-quant="'+selected+'">Ask For Availability<span></span><span></span><span></span></button>'
            );

            $("#total").hide();
            $("#total_tour").hide();
            $("#total_transfer").hide();
        }
      

        $("#total").html(
          parseInt($("#total").text()) +
            $(this).parent().find(".count").data("price")
        );
        selected++;

        if (selected === max) {
        //   $(".zero").parent().find(".plus, .minus").addClass("text-secondary");
		$('[data-room="'+$(this).closest(".offers_grid").data("room")+'"] .zero').parent().find(".plus, .minus").addClass("text-secondary");

        }
		selectedRooms[$(this).closest(".offers_grid").data("room")-1]=selected;
		console.log(selected);
		console.log(max);
      }
    });

    $(document).on("click", ".minus", function () {
		var max=roomsMax[$(this).closest(".offers_grid").data("room")-1];
		var selected=selectedRooms[$(this).closest(".offers_grid").data("room")-1];

      var countInput = $(this).parent().find(".count");
      if (countInput.val() > 0) {
        countInput.val(parseInt(countInput.val()) - 1);
        if (
          $(this).parent().find(".count").val() <=
          $(this).parent().find(".count").data("max")
        ) {
          $(this).closest(".row").find(".availability").html("");
            $("#total").show();
            $("#total_tour").show();
            $("#total_transfer").show();
          
        }
        console.log(parseInt($("#total").text()));
        console.log($(this).parent().find(".count").data("price"));
        $("#total").html(
          parseInt($("#total").text()) -
            $(this).parent().find(".count").data("price")
        );

        selected--;

        if (countInput.val() == 0) {
          $(this).parent().find(".count").addClass("zero");
        }
      }

      if (selected < max) {
        // $(".zero").parent().find(".plus, .minus").removeClass("text-secondary");
		$('[data-room="'+$(this).closest(".offers_grid").data("room")+'"] .zero').parent().find(".plus, .minus").removeClass("text-secondary");

      }
	  selectedRooms[$(this).closest(".offers_grid").data("room")-1]=selected;

    });
  $(document).on("click", ".see_details", function () {
    console.log($(this).find("i").hasClass("fa-chevron-down"));

    if ($(this).find("i").hasClass("fa-chevron-down")) {
      $(this).find("i").removeClass("fa-chevron-down");
      $(this).find("i").addClass("fa-chevron-up");
    } else {
      $(this).find("i").removeClass("fa-chevron-up");
      $(this).find("i").addClass("fa-chevron-down");
    }

    $(this).closest(".offers_item").find(".details").toggleClass("d-none");
  });

  $(document).on("change", ".tour_select", function () {
    var prev = $(this).data("prev");
    console.log("Previous Value:", prev);

    var currentVal = parseFloat($(this).find("option:selected").data("price"));
    var totalVal = parseFloat($("#total").text());
    var totalTourVal = parseFloat($("#total_tour").text());

    totalVal = totalVal - prev + currentVal;
    totalTourVal = totalTourVal - prev + currentVal;

	$("#total").html(totalVal);
	$("#total_tour").html(totalTourVal);

	$(this).data("prev",currentVal);

$(this).parent().find(".tour_select_price").html(currentVal+'$');

});


$(document).on("change", ".transfer_select", function () {
    var prev = $(this).data("prev");
    console.log("Previous Value:", prev);

    var currentVal = parseFloat($(this).find("option:selected").data("price"));
    var totalVal = parseFloat($("#total").text());
    var totalTransferVal = parseFloat($("#total_transfer").text());

    totalVal = totalVal - prev + currentVal;
    totalTransferVal = totalTransferVal - prev + currentVal;

	$("#total").html(totalVal);
	$("#total_transfer").html(totalTransferVal);

	$(this).data("prev",currentVal);

$(this).parent().find(".transfer_select_price").html(currentVal+'$');

});


  $('#result_form').submit(function () {
    var total = roomsMax.reduce(function (accumulator, currentValue) {
        return accumulator + currentValue;
    }, 0);

    var total_selected = selectedRooms.reduce(function (accumulator, currentValue) {
        return accumulator + currentValue;
    }, 0);

    if (total > total_selected) {
        event.preventDefault(); // prevent the default form submission
        $("#loader").addClass('d-none');
        toastr.error('Please fill all rooms', 'Error', {
          positionClass: 'toast-bottom-left',
          timeOut: 2000
      });
      $("#confirmationModal").modal('hide');

    }

    else{
      $("#loader").removeClass('d-none');
      $("#confirmationModal").modal('hide');


      setTimeout(() => {
      $("#loader").addClass('d-none');
    
      toastr.success('Sent Successfully', 'Success', {
        positionClass: 'toast-top-right',
        timeOut: 2000
    });
    return false;
      }, 2000);
    return false;

    }
    return false;

    // No else block here; the form will be submitted if conditions are met
});





// function to call ask for availability:
$(document).on("click", ".askForAvailbity", function () {

  console.log('Please');


  // var id = $(this).data("id");
  // var quant = $(this).data("quant");
  //  $.ajax({
  //     url : "http://.......",
  //     type: "Post",  
  //     data:{'id':id,'quant':quant,},
  //     success:function(data){
        toastr.success('Sent Successfully', 'Success', {
          positionClass: 'toast-top-right',
          timeOut: 2000
      });
      // }

// });

});






// fUNCTION TO CAHNGE TRANSFER,tOUR MODAL CONTETN ACCORDING TO THE CLICKE BUTTON FROM API

// $('.TransferModal').click(function(){

//   var id = $(this).data("id");
//    $.ajax({
//       url : "http://.......",
//       type: "Post",  
//       data:{'id':id},
//       success:function(data){
//         $('#TransferModalTitle').html(data.title);
//         $('#TransferModalTitle').html(data.subTitle);
//         data.forEach(element => {
//         $('#TransferModalTitle').html(
//           `<div class="row">
//           <div class="col-md-4">
//             <div class="tour_info_image w-100 ">
//               <img class="d-block w-100" src="${element.img}">
//             </div>
//           </div>

//           <div class="col-md-8">
//             <h4>${element.title}</h4>
//             ${element.description}
//           </div>
//         </div>`
//         );
          
//         });
//       }


// });


  
// });

});


