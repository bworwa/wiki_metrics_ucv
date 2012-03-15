<div id="article_information" class="round_corners drop_shadow centered">
    <div id="tabs" class="drop_shadow text-shadow">
        <ul>
            <li data-metric="revisions" class="selected opaque metric_information" title="Number of article revisions per month">Revisions</li>
            <li data-metric="size" class="translucid metric_information" title="Size of the article per month">Size</li>
            <li data-metric="users" class="translucid metric_information" title="Information about the users involved with the article">Users</li>
        </ul>
    </div>
    <div>
        <div class="section">
            Article:<h1 id="article_title"><?php echo $article_title; ?></h1>
            <span id="article_url">
                (<a href="<?php echo $article_url; ?>" target="_blank">article's history</a>)
            </span>
        </div>
        <div class="section">
            Host:<h2 id="article_host"><?php echo $article_host; ?></h2>
        </div>
        <div class="section">
            <span class="float_left">Chart type:</span>
            <ul id="chart_types">
                <li id="line_chart" class="float_left selected opaque round_corners" title="Lines"></li>
                <li id="column_chart" class="float_left translucid round_corners" title="Columns"></li>
                <li id="bar_chart" class="float_left translucid round_corners" title="Bars"></li>
            </ul>
        </div>
        <div id="chart"></div>
    </div>
</div>
<script> var base_url = "<?php echo $base_url; ?>"; </script>
<script src="https://www.google.com/jsapi"></script>
<script src="<?php echo $base_url; ?>public/js/common.js"></script>
<script>
    var revisions;

    var chart;
    var chart_options = {
        chartArea: { left: 60, top: 30 },
        animation: { duration: 1000, easing: "in" },
        height: 400,
        fontSize: 14,
        pointSize: 5
    }
    var chart_type = "LineChart";
    
    google.load("visualization", "1", { packages : ["corechart"] });
    google.setOnLoadCallback(init_data);
    
    function init_data()
    {
        revisions = new google.visualization.DataTable();
        revisions.addColumn("string", "Date");
        revisions.addColumn("number", "Total revisions");
        revisions.addColumn("number", "Minor revisions");
        
        size = new google.visualization.DataTable();
        size.addColumn("string", "Date");
        size.addColumn("number", "Max. size (Bytes)");
        size.addColumn("number", "Min. size (Bytes)");
        size.addColumn("number", "Avg. size (Bytes)");
        
        users = new google.visualization.DataTable();
        users.addColumn("string", "Name");
        users.addColumn("number", "Total revisions");

        <?php
            if (!empty($metrics["date_related_metrics"]))
                foreach ($metrics["date_related_metrics"] as $date_key => $metric):
        ?>
                    revisions.addRows([["<?php echo $metric["date"]; ?>", <?php echo $metric["total_revisions"]; ?>, <?php echo $metric["minor_revisions"]; ?>]]);
                    size.addRows([["<?php echo $metric["date"]; ?>", <?php echo $metric["min_size"]; ?>, <?php echo $metric["max_size"]; ?>, <?php echo $metric["avg_size"]; ?>]]);
        <?php   endforeach; ?>
            
        <?php
             if (!empty($metrics["users_related_metrics"]))
                foreach($metrics["users_related_metrics"] as $user => $revisions): ?>
            users.addRows([["<?php echo $user; ?>", <?php echo $revisions; ?>]]);
        <?php   endforeach; ?>
            
        init_elements();
    }

    function init_elements()
    {
        $("#tabs > ul > li").click(function()
        {
            var metric = $(this).data("metric");
            
            if(!$(this).hasClass("selected"))
            {
                $(this).removeClass("unselected translucid").addClass("selected opaque");
                $(this).siblings().removeClass("selected opaque").addClass("unselected translucid");
            }
            
            window["draw_" + metric + "_chart"]();
        });
        
        $("#line_chart").click(function()
        {
            chart_type = "LineChart";
            
            if(!$(this).hasClass("selected"))
            {
                $(this).removeClass("translucid").addClass("selected opaque");
                $(this).siblings().removeClass("selected opaque").addClass("translucid");
            }
            
            $("#tabs .selected").click();
        });
        
        $("#column_chart").click(function()
        {
            chart_type = "ColumnChart";
            
            if(!$(this).hasClass("selected"))
            {
                $(this).removeClass("translucid").addClass("selected opaque");
                $(this).siblings().removeClass("selected opaque").addClass("translucid");
            }
            
            $("#tabs .selected").click();
        });
        
        $("#bar_chart").click(function()
        {
            chart_type = "BarChart";
            
            if(!$(this).hasClass("selected"))
            {
                $(this).removeClass("translucid").addClass("selected opaque");
                $(this).siblings().removeClass("selected opaque").addClass("translucid");
            }
            
            $("#tabs .selected").click();
        });
              
        draw_revisions_chart();
    }
			
    function draw_revisions_chart()
    {      
        chart = new window["google"]["visualization"][chart_type](document.getElementById("chart"));
        
        resolve_chart_size(revisions.getNumberOfRows());
        
        chart.draw(revisions, chart_options);
    }
    
    function draw_size_chart()
    {      
        chart = new window["google"]["visualization"][chart_type](document.getElementById("chart"));
        
        resolve_chart_size(size.getNumberOfRows());

        chart.draw(size, chart_options);
    }
    
    function draw_users_chart()
    {      
        chart = new window["google"]["visualization"][chart_type](document.getElementById("chart"));
        
        resolve_chart_size(users.getNumberOfRows());

        chart.draw(users, chart_options);
    }
    
    function resolve_chart_size(number_of_rows)
    {
        if(chart_type == "BarChart")
        {
            chart_options.height = number_of_rows * 100;
            chart_options.chartArea.height = chart_options.height;
            
            chart_options.width = "80%";
            chart_options.chartArea.width = chart_options.width;
            
            chart_options.legend = { position: "right" };
            
            $("#chart").css("overflow-x", "hidden").css("overflow-y", "scroll");
        }
        else
        {
            chart_options.width = number_of_rows * 100;
            chart_options.chartArea.width = chart_options.width;
            
            chart_options.height = "80%";
            chart_options.chartArea.height = chart_options.height;
            
            chart_options.legend = { position: "in" };
            
            $("#chart").css("overflow-x", "scroll").css("overflow-y", "hidden");
        }
    }
</script>