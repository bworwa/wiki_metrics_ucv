		
		<div id="article_information" class="round_corners drop_shadow centered">
			<div id="tabs" class="drop_shadow text-shadow">
				<ul>
					<li data-metric="revisions" class="selected opaque">Revisions</li>
				</ul>
			</div>
			<div id="revisions">
				<div>
					Article:<h1 id="article_title"><?php echo $article_title; ?></h1>
					<span id="article_url">
						(<a href="<?php echo $article_url; ?>" target="_blank"><?php echo $article_title; ?></a>)
					</span>
				</div>
				<div id="chart"></div>
			</div>
		</div>
		<script src="https://www.google.com/jsapi"></script>
		<script>
			google.load("visualization", "1", {packages:["corechart"]});
			google.load("jquery", "1.6.4");
			google.setOnLoadCallback(init);

			function init()
			{
				$("#url").focus(function()
				{
					$(this).parent().removeClass("translucid").addClass("opaque");
				}).blur(function()
				{
					$(this).parent().removeClass("opaque").addClass("translucid");
				});

				$("li", "#tabs").click(function()
				{
					$(this).removeClass("unselected translucid").addClass("selected opaque");
					$(this).siblings().removeClass("selected opaque").addClass("unselected translucid");
					
					var metric = $(this).attr("data-metric");
					
					$("#article_information > div:not(:first)").each(function()
					{
						if($(this).attr("id") == metric)
						{
							$(this).removeClass("hidden");
						}
						else
							if(!$(this).hasClass("hidden"))
								$(this).addClass("hidden");
					});
				});

				drawChart();
			}
			
			function drawChart()
			{
				var time;
				var data = new google.visualization.DataTable();
				data.addColumn("date", "Date");
				data.addColumn("number", "Revisions");

				<?php
					if(!empty($revisions_count))
						foreach($revisions_count as $count):
				?>

					data.addRows([[new Date(<?php echo $count["date"]; ?> * 1000), <?php echo $count["revisions"]; ?>]]);
				
				<?php endforeach; ?>

				var chart = new google.visualization.LineChart(document.getElementById("chart"));
				chart.draw(
					data,
					{ chartArea:
						{ width: "90%", height: "80%" },
						legend: "none",
						pointSize: 5,
						titlePosition: "none",
						height: 400
					}
				);
			}
		</script>
