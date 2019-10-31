#!/bin/bash

PREFIX=$(echo $2 | sed -e 's/\\/\\\\/g; s/\//\\\//g; s/&/\\\&/g')
SUFFIX=$(date "+%Y.%m.%d-%H.%M.%S")

./faro_spider.sh $1 $SUFFIX

if [[ -z "$3" || "$3" != "win" ]]
then
	# UNIX
   	sed -i.bak "s|input|$PREFIX|" output/scan.$SUFFIX.csv
   	sed -i.bak "s|input|$PREFIX|" output/scan.$SUFFIX.entity
else
	# Windows
   	sed -i.bak "s|input|$PREFIX| ; s|/|\\\\|g ; s|,application\\\\|,application\/| ; s|,text\\\\|,text\/|" output/scan.$SUFFIX.csv
   	sed -i.bak "s|input|$PREFIX| ; s|/|\\\\|g ; s|,application\\\\|,application\/|" output/scan.$SUFFIX.entity
fi

rm output/scan.$SUFFIX.csv.bak
rm output/scan.$SUFFIX.entity.bak
