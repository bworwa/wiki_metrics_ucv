
# User defined
from usr.wikimetrics import Wikimetrics
from usr.mongo import Mongo

mongo = Mongo()

wikimetrics = Wikimetrics()

article = mongo.get_next_article()

if article:

	wikimetrics.run(article["url"], article["last_update"])

else:

	print "No URLs found, collection 'articles' is empty."
