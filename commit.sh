#!/bin/bash

# First we remove all the backup files

find . -name "*.*~" -exec rm -f '{}' +

# Then the pyc files

find . -name "*.pyc" -exec rm -f '{}' +

# Then the /logs directory

rm -r logs

# Then that pesky README.html~ file

rm README.html~

# And then we proceed to commit

git init
touch *
git add *
git commit -m "autocommit [`date`]"
git remote add origin git@github.com:bworwa/wiki_metrics_ucv.git
git push -u origin master

exit 0

