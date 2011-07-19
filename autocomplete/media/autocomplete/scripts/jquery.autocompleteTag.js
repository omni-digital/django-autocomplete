/*
This is to be used with the Incuna autocompleteTag Django widget.
*/
(function($){
    $.fn.autocompleteTag = function (options) {

        var defaults = {
            'uiBoxSelector': 'autocompleteTag',
            'uiInputSelector': 'search_input'
        }
        
        var settings = $.extend({}, defaults, options);

        function extractLast( term ) {
            return term.split(/,\s*/).pop();
        }

        function trim( strText ) { 
            // this will get rid of leading spaces 
            while (strText.substring(0,1) == ' ') 
                strText = strText.substring(1, strText.length);

            // this will get rid of trailing spaces 
            while (strText.substring(strText.length-1,strText.length) == ' ')
                strText = strText.substring(0, strText.length-1);

           return strText;
        }

        function characterTyped( strText ) {
            return strText.charAt(strText.length-1);
        }


        return this.each(function () {

            // hide the select box from showing
            $(this).hide();

            var target = $(this);
            var uiBox = $('<div>').addClass(settings.uiBoxSelector).append($('<ul>').append($('<li>', { 'class': 'input' }))).insertAfter(target);
            var search_input = $('<input>').addClass(settings.uiInputSelector).attr({'type': 'text', 'name': "search_input", 'class': "ui-autocomplete-input" }).appendTo(uiBox.find('ul li:first'));

            function addDataElement( title ) {
                
                if ($.grep( uiBox.find('ul li span.text:contains('+title+')'), function ( el, i ) { return $(el).text() == title }).length) {
                    // item already included 
                    return false;
                }

                $('<li>', { 'class': 'tag' }).append(
                    $('<span>', { 'class': 'tag' }).append(
                        $('<span>', { 'class': 'text', 'text': title }), 
                        $('<a>', { 
                            'class': 'delete', 
                            'href': '#', 
                            'text': 'Delete', 
                            'click': function () {

                                $(this).closest('li').fadeOut(300, function () {
                                    $(this).remove();
                                    search_input.focus();
                                    updateSubmitInput();
                                });
x
                                return false;
                            }
                        }))).insertBefore(uiBox.find('ul li:last'));

                //uiBox.find('ul li:last').before(liSelected);

            }

            function updateSubmitInput() {
                
                var text = "";
                
                var i = 0;
                uiBox.find('ul li.tag').each(function () {
                    text += $(this).find('span.text').text() + ',';
                    i++;
                });
                
                target.val(text);
            }
           
            // set the data elements 
            if (target.val()) {
                var tags = [];
                // split current data by commas?
                if (target.val().indexOf(',') > 0) {
                    tags = target.val().split(',');
                } else {
                    tags = [target.val()];

                }

                for (i=0; i<tags.length; i++) {
                    // trim whitespace and douple quotes (")
                    addDataElement(tags[i].replace(/^(\s|")+|("|\s)+$/g, ''));
                }
                updateSubmitInput();
            }

            // setup click so anywhere in the box is clicked, it will focus the text input
            uiBox.click(function () {
                search_input.focus();
            });

            search_input.bind( "keydown", function( event ) {
                
                var search_input_value = $(this).val();
                
                if ( event.keyCode === $.ui.keyCode.TAB &&
                        $( this ).data( "autocomplete" ).menu.active ) {
                    event.preventDefault();
                }
            })
            .bind("keyup", function (event) {
                
                var search_input_value = $(this).val();
                var autocomplete_ul = uiBox.find('ul');

                // if user pressed backspace and there is no text, then put the last selected tag into a delete state
                if ( event.keyCode === $.ui.keyCode.BACKSPACE && search_input_value == "") {
                    
                    // the last tag is in delete state, so go ahead and delete it
                    if (autocomplete_ul.find('li.tag:last').hasClass('delete')) {
                        autocomplete_ul.find('li.tag:last').remove();
                        updateSubmitInput();
                    }
                    // the last tag is not in a delete state, so add the class
                    else {
                        autocomplete_ul.find('li.tag:last').addClass('delete');
                    }
                }
                
                // we need to check that if the last selected is in a delete state, but the user carrys on typing, then take the delete back off
                if ( event.keyCode != $.ui.keyCode.BACKSPACE ) {
                    if (autocomplete_ul.find('li.tag:last').hasClass('delete')) {
                       autocomplete_ul.find('li.tag.delete:last').removeClass('delete');
                    }
                }
                
                // user enters a comma? then it's a tag!
                if (search_input_value.indexOf(",") > 0) {
                    addDataElement(search_input_value.substring(0, search_input_value.length-1)); // add data element (without the last character which would be a comma)
                    updateSubmitInput();
                    search_input.val(''); //clear the input now
                }

                // user enters a single quote?
                else if (characterTyped(search_input_value) == "'" && trim(search_input_value).length > 1) {
                
                    // // trim any white space
                    var tag = trim($(this).val());
                    // 
                    // //check if there is a quote at the beginning too?
                    if (tag.charAt(0) == "'") {
                        // this is a full tag!
                        addDataElement(tag);
                        updateSubmitInput();
                        search_input.val(''); //clear the input now
                    }
                
                }

                // user enters a double quote?
                else if (characterTyped(search_input_value) == '"' && trim(search_input_value).length > 1) {
                
                    // // trim any white space
                    var tag = trim($(this).val());
                    // 
                    // //check if there is a quote at the beginning too?
                    if (tag.charAt(0) == '"') {
                        // this is a full tag!
                        addDataElement(tag);
                        updateSubmitInput();
                        search_input.val(''); //clear the input now
                    }
                
                }

            })
            .autocomplete({
                'minLength': 0,
                //'source': ['boom', 'sauce', 'funk', '"la la"'],
                'source': function( request, response ) {
                
                    var ajax_url = options.url+"?ct="+options.content_type;
                    if (options.search_fields) {
                        ajax_url += "&sf="+options.search_fields;
                    }
                    
                    $.getJSON(ajax_url, {
                        term: extractLast( request.term )
                    }, response );
                }, 
                'focus': function() {
                    // prevent value inserted on focus
                    return false;
                },
                'select': function( event, ui ) {
                    
                    // add tag data element
                    addDataElement(ui.item.label);

                    // update input that will be submitted
                    updateSubmitInput();

                    // clear it regardless if it's present or not already
                    this.value = "";

                    return false;
                }
            });

        });
    };

})(jQuery);
