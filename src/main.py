
# User defined

from usr.wikimetrics import Wikimetrics

wikimetrics = Wikimetrics()

article = wikimetrics.get_next_article()

if article:

	wikimetrics.run(article["url"], article["last_update"])

else:

	print "No URLs found, collection 'articles' is empty."
