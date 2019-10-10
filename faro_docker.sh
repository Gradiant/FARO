#!/bin/bash

SUFFIX=$(date "+%Y.%m.%d-%H.%M.%S")

./faro_spider.sh $1 $SUFFIX

sed -i.bak 's|input/||' output/scan.$SUFFIX.csv
sed -i.bak 's|input/||' output/scan.$SUFFIX.entity

rm output/scan.$SUFFIX.csv.bak
rm output/scan.$SUFFIX.entity.bak
