google.load("jquery", "1.6.4");
google.setOnLoadCallback(init);

function init()
{
    var url_form = $("#url_form");
    var url_input = $("#url");    
    
    var suggestions_div = $("#suggestions");
    resize_suggestions_div();
    
    var typing_timer;
    var done_typing_interval = 700;

    function show_suggestions_div()
    {
        suggestions_div.show();
    }

    function hide_suggestions_div()
    {
        suggestions_div.hide();
    }
        
    function clear_suggestions_div()
    {
        suggestions_div.html("");
    }
    
    function resize_suggestions_div()
    {
        suggestions_div.css("left", url_input.position().left);
        suggestions_div.css("width", parseInt(url_input.outerWidth()) + parseInt(url_input.css("padding-left")) - parseInt(url_input.css("padding-right"))- 4);
    }
    
    function get_articles_suggestions()
    {
        clear_suggestions_div();
        
        $.getJSON(
            base_url + "index.php/ajax/get_article_suggestion",
            {
                query: url_input.val()
            },
            function(suggestions)
            {
                if(suggestions.length > 0)
                {                    
                    $.each(suggestions, function(key, suggestion)
                    {
                        suggestions_div.append(
                            $("<div class=\"suggestion\" data-url=\"" + suggestion.url + "\">" + suggestion.title + " (<span class=\"bold\">" + suggestion.host + "</span>)" + "</div>")
                        );
                    });

                    url_form.append(suggestions_div);

                    show_suggestions_div();
                }
                else
                {
                    hide_suggestions_div();
                }
            }
        );
    }
    
    url_input.focus(function()
    {
        $(this).parent().removeClass("translucid").addClass("opaque");            
    }).blur(function()
    {
        $(this).parent().removeClass("opaque").addClass("translucid");            
    }).keyup(function(event)
    {
        clearTimeout(typing_timer);
        
        if (event.keyCode == 27)
        {
            hide_suggestions_div();
            
            event.stopPropagation();
        }
        else if(url_input.val().length > 0)
        {
            typing_timer = setTimeout(get_articles_suggestions, done_typing_interval);
        }
        else
        {
            hide_suggestions_div();
        }
    });
    
    $("div .suggestion").live("click", function()
    {
        url_input.val($(this).data("url"));
        
        hide_suggestions_div();
    });
    
    $(document).click(hide_suggestions_div);
    
    $(window).resize(resize_suggestions_div);
}