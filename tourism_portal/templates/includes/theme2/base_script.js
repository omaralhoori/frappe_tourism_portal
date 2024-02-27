$('.dropdown-toggle').click(function() {
    var dropdownMenu = $(this).next('.dropdown-menu');
    $(this).parent().toggleClass('show');
    dropdownMenu.toggleClass('show');

});