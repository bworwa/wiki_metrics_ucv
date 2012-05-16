<div id="all_articles" class="round_corners drop_shadow centered">
    <?php if(!empty($articles)): ?>
        <ul>
            <?php foreach ($articles as $article): ?>
                <li>
                    <a href="<?php echo $base_url; ?>index.php/metrics?url=<?php echo $article["url"]; ?>">
                        <?php echo $article["title"]; ?>
                    </a>
                    (<span class="bold"><?php echo $article["host"]; ?></span>)
                </li>
            <?php endforeach; ?>
        </ul>
    <?php else: ?>
        <div class="information">There are no articles yet. Try again later</div>
    <?php endif; ?>
</div>
<script> var base_url = "<?php echo $base_url; ?>"; </script>
<script src="https://www.google.com/jsapi"></script>
<script src="<?php echo $base_url; ?>public/js/common.js"></script>