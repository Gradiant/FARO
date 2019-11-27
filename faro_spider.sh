#!/bin/bash
mkdir -p output

# Run tika server externally

# Check if we have the tika server jar, if not download it
TIKA_SERVER_JAR=/tmp/tika-server.jar

if [ ! -f $TIKA_SERVER_JAR ]; then
   	wget -O $TIKA_SERVER_JAR https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar
fi

# Get rid of tika server initialization warnings
TIKA_SERVER_CONFIG=/tmp/tika-config.xml
if [ ! -f $TIKA_SERVER_CONFIG ]; then
	echo -e "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<properties>\n<service-loader initializableProblemHandler=\"ignore\"/>\n</properties>" > /tmp/tika-config.xml
fi
# Set envvar for all processes started from current shell
export TIKA_CONFIG="/tmp/tika-config.xml"

# Check if tika is running locally already
nc -z 0.0.0.0 9998 2>/dev/null
if [ $? -ne 0 ]
then
	java -Dlog4j.configuration=file:log4j.properties -jar $TIKA_SERVER_JAR -h 0.0.0.0 &
	# Allow tika some uptime to finish initialization
	sleep 5
fi

if [ -z "$2" ]
then
   SUFFIX=$(date "+%Y.%m.%d-%H.%M.%S")
else
   SUFFIX=$2
fi

CPU_PARALLEL_USAGE="50%"

echo "filepath,score,person_position_organization,monetary_quantity,signature,personal_email,mobile_phone_number,financial_data,document_id,custom_words,content-type" > output/scan.$SUFFIX.csv
# Run faro over a recursive list of appropriate filetypes
find "$1" -type f \( ! -regex '.*/\..*' \) | parallel -P $CPU_PARALLEL_USAGE python faro_detection.py -i {} --output_entity_file output/scan.$SUFFIX.entity --dump >> output/scan.$SUFFIX.csv
