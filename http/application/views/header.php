<!DOCTYPE HTML>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<link rel="stylesheet" type="text/css" href="<?php echo $base_url; ?>public/css/themes/default/default.css" media="screen">
		<?php if(!empty($article_title)): ?>
			<title><?php echo $article_title; ?></title>
		<?php else: ?>
			<title><?php echo $welcome_title; ?></title>
		<?php endif; ?>
	</head>
	<body>
		<div id="url_form" class="centered">
			<form action="<?php echo $base_url; ?>index.php/metrics" method="GET" class="translucid">
				<input id="url" name="url" type="url" class="round_corners drop_shadow" required>
				<input id="url_submit" type="submit" value="View metrics" class="round_corners drop_shadow">
			</form>		
		</div>
