#!/bin/bash
mkdir -p output

# Run tika server externally

# Check if we have the tika server jar, if not download it
TIKA_SERVER_JAR=/tmp/tika-server.jar
if [ ! -f $TIKA_SERVER_JAR ]; then
   	wget -O $TIKA_SERVER_JAR https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.21/tika-server-1.21.jar
fi

# Check if tika is running locally already
nc -z 0.0.0.0 9998 2>/dev/null
if [ $? -ne 0 ]
then
	java -jar $TIKA_SERVER_JAR -h 0.0.0.0 &
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
find $1 -type f \( -iname "*.doc" -o -iname "*.docx" -o -iname "*.pptx" -o -iname "*.ppt" -o -iname "*.xls*" -o -iname "*.pdf" -o -iname "*.odt" -o -iname "*.ods" -o -iname "*.odp" -o -iname "*.txt" -o -iname "*.rtf" \)  | parallel -P $CPU_PARALLEL_USAGE python faro_detection.py -i {} --output_entity_file output/scan.$SUFFIX.entity --dump >> output/scan.$SUFFIX.csv

sed -i.bak 's/$/,/' output/scan.$SUFFIX.entity
sed -i.bak '$s/,$//' output/scan.$SUFFIX.entity
sed -i.bak "1i\\
[" output/scan.$SUFFIX.entity
echo "]" >> output/scan.$SUFFIX.entity

rm output/scan.$SUFFIX.entity.bak
