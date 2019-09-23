#!/bin/bash

# Run faro over a recursive list of appropriate filetypes

mkdir -p output
CURRENT_TIME=$(date "+%Y.%m.%d-%H.%M.%S")
CPU_PARALLEL_USAGE="50%"

echo "filepath,score,person_position_organization,monetary_quantity,signature,personal_email,mobile_phone_number,financial_data,document_id,custom_words,content-type" > output/scan.$CURRENT_TIME.csv

find $1 -type f \( -iname "*.doc" -o -iname "*.docx" -o -iname "*.pptx" -o -iname "*.ppt" -o -iname "*.xls*" -o -iname "*.pdf" -o -iname "*.odt" -o -iname "*.ods" -o -iname "*.odp" -o -iname "*.txt" -o -iname "*.rtf" \)  | parallel -P $CPU_PARALLEL_USAGE python faro_detection.py -i {} --output_entity_file output/scan.$CURRENT_TIME.entity --dump >> output/scan.$CURRENT_TIME.csv

sed -i.bak 's/$/,/' output/scan.$CURRENT_TIME.entity
sed -i.bak '$s/,$//' output/scan.$CURRENT_TIME.entity
sed -i.bak "1i\\
[" output/scan.$CURRENT_TIME.entity
echo "]" >> output/scan.$CURRENT_TIME.entity

# Clean output
rm output/scan.$CURRENT_TIME.entity.bak
