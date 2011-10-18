#!/bin/bash

#First we remove all the backup files
find . -name "*.*~" -exec rm -f '{}' +

#Then the pyc files
find . -name "*.pyc" -exec rm -f '{}' +

#And finally the /logs directory

rm -r logs

#And then we proceed to commit
git init
touch *
git add *
git commit -m "autocommit [`date`]"
git push origin master

exit 0

