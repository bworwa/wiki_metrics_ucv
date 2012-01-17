
# User defined
from usr.wikimetrics import Wikimetrics, ResolvePendingFailed
from usr.mongo import Mongo

mongo = Mongo()

wikimetrics = Wikimetrics()

article = mongo.get_next_article()

if article:

	try:

		wikimetrics.run(article["url"], article["last_update"])

	except ResolvePendingFailed:

		pass
