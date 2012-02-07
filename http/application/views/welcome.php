		<div id="recent_searchs" class="centered round_corners">
			My recent searches: <?php if(!empty($recently_searched_articles)) echo $recently_searched_articles; else echo "none"; ?>
		</div>
		<div id="view_all_articles" class="centered">
			<a href="<?php echo $base_url; ?>index.php/welcome/view_all_articles">View all available articles</a>
		</div>	
		<script src="https://www.google.com/jsapi"></script>
		<script>
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
			}				
		</script>
