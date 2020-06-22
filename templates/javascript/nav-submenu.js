$(document).ready(function(){
  // opens and closes submenus with country/state lists in main <nav> when user clicks icon;
  // opens filtered search results list when search input has focus and contains text

  var targetSubMenu, searchText, regionName;

  // add svg down arrow after menu nav items that contain a submenu
  $('.hasSubmenu > a').after(
    '<svg viewBox="0 0 400 240" stroke-width="40"><line x1="20" y1="20" x2="210" y2="210" /><line x1="380" y1="20" x2="185" y2="210" /></svg>'
  );

  // create submenu container, add label (for input element), and
  // insert it in main page nav after other li.submenu elements
  $('<li class="hasSubmenu searchWidget"></li>')
    .append('<label title="search for a country or state"></label>')
    .append('<output><ul class="submenu" hidden></ul></output>')
    .appendTo('body > header > div > nav > ul, body > footer > nav > ul');

  // append svg search icon and input element to label
  $('.hasSubmenu > label')
    .append('<svg viewBox="0 0 250 450"><title>search</title><g stroke-width="30"><circle cx="130" cy="120" r="100" /><line x1="130" y1="220" x2="130" y2="270" /></g><g stroke-width="43"><line x1="130" y1="273" x2="130" y2="370" /><line x1="130" y1="330" x2="130" y2="425" stroke-linecap="round" /></g></svg>')
    .append('<input type="search" size="14">');

  // add all region page links to output ul search results
  $('.regions > li').clone().appendTo('output > ul.submenu');
  // TODO improve clone, maybe clone entire ul element then flatten instead of cloning each li element


  $(".hasSubmenu > svg").click(function(){
    // toggle menus open/close when user clicks arrow
    targetSubMenu = $(this).next(".submenu");

    if (targetSubMenu.is(":hidden")) {
      // if submenu next to arrow is hidden, close other submenus and then reveal this one
      closeSubmenus();
      targetSubMenu.slideDown(300);
      $(this).addClass('open');
    }
    else {
      // else close all submenus
      closeSubmenus();
    }
  })


  // if user clicks anywhere outside of submenu, close any open submenus
  $(document).click(function(event) {
    $target = $(event.target);
    if(!$target.closest('.hasSubmenu').length && $('.submenu').is(":visible")) {
      closeSubmenus(200);
    }
  });


  $('.hasSubmenu > label > input').focus(function(){
    // on search input focus (e.g. when user clicks inside it)
    // close other submenu popovers, and open filtered ul.searchResutls
    // if there are characters in the input
    closeSubmenus();
    if ($.trim(this.value)) {
      $(this).parent('label').next('output').children('.submenu').slideDown(300);
    }
  });


  $('.hasSubmenu > label > input').on('input', function(){
    // on input to search form, show filtered li elements matching
    // any text entered, or hide output ul if field is empty

    searchText = $.trim(this.value).toLowerCase();

    if (searchText) {
      // filter search results based on text entered in input
      $(this).parent('label').next('output').children('.submenu').children('li').each(function(){
        regionName = $(this).text().toLowerCase();
        (regionName.indexOf(searchText) >= 0) ? $(this).show() : $(this).hide();
      });
      // show search results output ul.submenu
      if ($(this).parent('label').next('output').children('.submenu').is(':hidden')) {
        $(this).parent('label').next('output').children('.submenu').slideDown(300);
      }
    }
    else {
      // input is empty, so hide search results output ul.submenu
      $('output > .submenu').hide();
    }
  });


  function closeSubmenus(slideTime = 50) {
    // close any open submenus and remove 'open' class from svg
    $('.submenu').slideUp(slideTime);
    $('svg').removeClass();
  }


  // reset page before navigating away, so that if user
  // presses back button on browser, submenus will be closed
  window.onbeforeunload = function(){
    closeSubmenus(1);
  }

}); // end document.ready function
