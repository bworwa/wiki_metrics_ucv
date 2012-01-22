
# User defined
from usr.wikimetrics import Wikimetrics, ResolvePendingFailed
from usr.mongo import Mongo
from usr.priority import Priority
from usr.urls import Urls

#priority = Priority()
#priority.run()

#urls = Urls()
#urls.add_url(None)

"""
mongo = Mongo()

wikimetrics = Wikimetrics()

article = mongo.get_next_article()

if article:

	try:

		wikimetrics.run(article["url"], article["last_update"])

	except ResolvePendingFailed:

		pass
"""
