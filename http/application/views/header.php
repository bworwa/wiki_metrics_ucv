<!DOCTYPE HTML>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="stylesheet" type="text/css" href="<?php echo $base_url; ?>public/css/themes/default/default.css" media="screen">
        <title><?php echo $page_title; ?></title>
    </head>
    <body>
        <div id="logo">
            <a href="<?php echo $base_url; ?>">
                <div style="width: 100%; height: 100%;"></div>
            </a>
        </div>
        <div id="url_form" class="centered">
            <form action="<?php echo $base_url; ?>index.php/metrics" method="GET" class="translucid">
                <input id="url" name="url" type="url" class="round_corners drop_shadow" autocomplete="off" required>
                <input id="url_submit" type="submit" value="View metrics" class="round_corners drop_shadow">
            </form>
            <div id="suggestions" class="round_corners drop_shadow"></div>
        </div>
        <div id="recent_searchs" class="centered round_corners drop_shadow">
            My recent searches: <?php echo $recent_searches; ?>
        </div>