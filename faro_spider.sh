#!/bin/bash
mkdir -p output

# Run tika server externally

# Check if we have the tika server jar, if not download it
TIKA_SERVER_JAR=/tmp/tika-server.jar

if [ ! -f $TIKA_SERVER_JAR ]; then
   	wget -O $TIKA_SERVER_JAR https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar
fi

# Default faro tika config file
FARO_TIKA_CONFIG="$PWD/config/base-tika-config.xml"
# Check if FARO_DISABLE_OCR is set on the current shell, if so disable OCR execution
if [ ! -z "$FARO_DISABLE_OCR" ]; then
	echo "found FARO_DISABLE_OCR environment variable: disabling OCR parsing"
	FARO_TIKA_CONFIG="$PWD/config/disable-ocr-tika-config.xml"
fi

# Set envvar for all processes started from current shell
export TIKA_CONFIG="$FARO_TIKA_CONFIG"

# restart tika server to allow new configuration and clean RAM
nc -z 0.0.0.0 9998 2>/dev/null
if [ $? -eq 0 ]; then
	ps -ef | grep tika-server.jar | grep -v grep | awk '{print $2}' | xargs kill
fi

java -Dlog4j.configuration=file:config/log4j.properties -jar $TIKA_SERVER_JAR -h 0.0.0.0 &
# Allow tika some uptime to finish initialization
sleep 5

if [ -z "$2" ]
then
   SUFFIX=$(date "+%Y.%m.%d-%H.%M.%S")
else
   SUFFIX=$2
fi

CPU_PARALLEL_USAGE="50%"

echo "filepath,score,person_position_organization,monetary_quantity,signature,personal_email,mobile_phone_number,financial_data,document_id,custom_words,meta:content-type,meta:author,meta:pages,meta:lang,meta:date,meta:filesize,meta:ocr" > output/scan.$SUFFIX.csv

# Run faro over a recursive list of appropriate filetypes
find "$1" -type f \( ! -regex '.*/\..*' \) | parallel -P $CPU_PARALLEL_USAGE python faro_detection.py -i {} --output_entity_file output/scan.$SUFFIX.entity --dump >> output/scan.$SUFFIX.csv
