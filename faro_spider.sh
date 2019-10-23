#!/bin/bash

# Run faro over a recursive list of appropriate filetypes

mkdir -p output
if [ -z "$2" ]
then
   SUFFIX=$(date "+%Y.%m.%d-%H.%M.%S")
else
   SUFFIX=$2
fi

CPU_PARALLEL_USAGE="50%"

echo "filepath,score,person_position_organization,monetary_quantity,signature,personal_email,mobile_phone_number,financial_data,document_id,custom_words,prob_currency,content-type" > output/scan.$SUFFIX.csv
find $1 -type f \( -iname "*.doc" -o -iname "*.docx" -o -iname "*.pptx" -o -iname "*.ppt" -o -iname "*.xls*" -o -iname "*.pdf" -o -iname "*.odt" -o -iname "*.ods" -o -iname "*.odp" -o -iname "*.txt" -o -iname "*.rtf" \)  | parallel -P $CPU_PARALLEL_USAGE python faro_detection.py -i {} --output_entity_file output/scan.$SUFFIX.entity --dump >> output/scan.$SUFFIX.csv

sed -i.bak 's/$/,/' output/scan.$SUFFIX.entity
sed -i.bak '$s/,$//' output/scan.$SUFFIX.entity
sed -i.bak "1i\\
[" output/scan.$SUFFIX.entity
echo "]" >> output/scan.$SUFFIX.entity

rm output/scan.$SUFFIX.entity.bak
