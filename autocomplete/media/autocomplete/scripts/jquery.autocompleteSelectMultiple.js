/*
This is to be used with the Incuna AutocompleteSelectMultiple Django widget.
*/

(function($){

    $.fn.autocompleteSelectMultiple = function (options) {

        function split( val ) {
            return val.split( /,\s*/ );
        }

        function extractLast( term ) {
            return split( term ).pop();
        }

        // hide the select box from showing
        $('.autocompleteSelectMultiple').siblings('select.autocompleteselectmultiple').hide();

        // setup click so anywhere in the box is clicked, it will focus the text input
        $('.autocompleteSelectMultiple').click(function () {
            $(this).find('input.search_input').focus();
        });

        return this.each(function () {

            var target = jQuery(this);
            var search_input = target.find('input.search_input');

            search_input.bind( "keydown", function( event ) {
                if ( event.keyCode === $.ui.keyCode.TAB &&
                        $( this ).data( "autocomplete" ).menu.active ) {
                    event.preventDefault();
                }
            })
            .autocomplete({
                'minLength': 0,
                'source': function( request, response ) {

                    var ajax_url = options.url+"?ct="+options.content_type;
                    if (options.search_fields) {
                        ajax_url += "&sf="+options.search_fields;
                    }

                    $.getJSON(ajax_url, {
                        term: extractLast( request.term )
                    }, response );

                },
                'search': function() {
                    // custom minLength
                    var term = extractLast( this.value );
                    if ( term.length < 2 ) {
                        return false;
                    }
                },
                'focus': function() {
                    // prevent value inserted on focus
                    return false;
                },
                'select': function( event, ui ) {

                    var ac_element = $('.autocompleteSelectMultiple');
                    var ac_datainput = ac_element.siblings('select.autocompleteselectmultiple');

                    // if the option doesn't already exist then add it...
                    if (ac_datainput.find('option[value='+ui.item.value+']').length == 0) {
                        ac_datainput.append("<option value='"+ui.item.value+"' selected='selected'>"+ui.item.label+"</option>");
                        ac_element.find('ul li:last').before("<li id='id_ac_selected_"+ui.item.value+"' class='selected'><span class='selected'>"+ui.item.label+"<a class='delete' href='#'>Delete</a></span></li>");
                        ac_element.find('li#id_ac_selected_'+ui.item.value+' a.delete').click(function () {

                            ac_datainput.find('option[value='+ui.item.value+']').remove();

                            $(this).closest('li').fadeOut(300, function () {
                                $(this).remove();
                                ac_element.find("input.search_input" ).focus();
                            });

                            return false;
                        });
                    }

                    // clear it regardless if it's present or not already
                    this.value = "";

                    return false;
                }
            });

        });
    };

})(jQuery);