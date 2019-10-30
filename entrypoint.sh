#!/bin/bash

PREFFIX=$(echo $2 | sed -e 's/\\/\\\\/g; s/\//\\\//g; s/&/\\\&/g')
SUFFIX=$(date "+%Y.%m.%d-%H.%M.%S")

nohup java -jar /tmp/tika-server.jar -h 0.0.0.0 > /dev/null 2>&1 &

./faro_spider.sh $1 $SUFFIX

if [ -z "$3" ]
then
   sed -i.bak "s|input|$PREFFIX|" output/scan.$SUFFIX.csv
   sed -i.bak "s|input|$PREFFIX|" output/scan.$SUFFIX.entity
else
   sed -i.bak "s|input|$PREFFIX| ; s|/|\\\\|g ; s|,application\\\\|,application\/| ; s|,text\\\\|,text\/|" output/scan.$SUFFIX.csv
   sed -i.bak "s|input|$PREFFIX| ; s|/|\\\\|g ; s|,application\\\\|,application\/|" output/scan.$SUFFIX.entity
fi

rm output/scan.$SUFFIX.csv.bak
rm output/scan.$SUFFIX.entity.bak
