$(document).ready(function(){

  // opens and closes submenus with country/state lists in main <nav> when user clicks icon

  var targetSubMenu, notTargetSubMenu;
  var pullDownMenus = $(".submenu");

  // add svg down arrow after menu nav items that contain a submenu
  $(".hasSubmenu > a").after('<svg xmlns="http://www.w3.org/2000/svg" width="400px" height="240px" viewBox="0 0 400 240"><line x1="20" y1="20" x2="210" y2="210" stroke-width="40" /><line x1="380" y1="20" x2="185" y2="210" stroke-width="40" /></svg>');


  // close any open submenus and remove class from svg
  function closeSubmenus() {
    $('.submenu').slideUp(200);
    $('svg').removeClass('open');
  }

  // toggle menus open/close when user clicks arrow
  $(".hasSubmenu > svg").click(function(){
    targetSubMenu = $(this).next(".submenu");

    // if submenu next to arrow is hidden, reveal it and close other submenu
    if (targetSubMenu.is(":hidden")) {
      $('.submenu').not(targetSubMenu).slideUp(50);
      targetSubMenu.slideDown(350);
      $(this).addClass('open');
      $('svg').not($(this)).removeClass('open');
    }
    // else close all submenus
    else {
      closeSubmenus();
    }
  })

  // if user clicks anywhere outside of submenu, close any open submenus
  $(document).click(function(event) { 
    $target = $(event.target);
    if(!$target.closest('.hasSubmenu').length && $('.submenu').is(":visible")) {
      closeSubmenus();
    }        
  });


}); // end document.ready function
