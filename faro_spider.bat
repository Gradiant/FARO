
REM Run faro over a recursive list of appropriate filetypes

@ECHO off
MKDIR output

SETLOCAL ENABLEDELAYEDEXPANSION
if [%2]==[] (
	SET SUFFIX=%DATE:~6,4%.%DATE:~3,2%.%DATE:~0,2%-%TIME:~0,2%.%TIME:~3,2%.%TIME:~6,2%
	SET SUFFIX=!SUFFIX: =0!
) ELSE (
	SET SUFFIX=%2
)

ECHO filepath,score,person_position_organization,monetary_quantity,signature,personal_email,mobile_phone_number,financial_data,document_id > output\scan.%SUFFIX%.csv

FOR /F "delims=" %%G IN ('dir %1\*.doc %1\*.docx %1\*.ppt %1\*.pptx %1\*.xls %1\*.xlsx %1\*.pdf %1\*.odt %1\*.ods %1\*.odp %1\*.txt %1\*.rtf /b/s') DO (
	SET /A CTR=0
	FOR /F "delims=" %%i IN ('python faro_detection.py -i "%%G" --output_entity_file output\scan.%SUFFIX%.ent --dump') DO (
		IF !CTR! EQU 0 (SET /P "=%%i" <nul >> output\scan.%SUFFIX%.csv & SET /A CTR=1)
	)
)

SET /A CTR=0
ECHO [> output\scan.%SUFFIX%.entity
FOR /F "tokens=*" %%A IN (output\scan.%SUFFIX%.ent) DO (
	IF !CTR! EQU 1 (ECHO ,>> output\scan.%SUFFIX%.entity & SET /P "=%%A" <nul >> output\scan.%SUFFIX%.entity) ELSE (SET /P "=%%A" <nul >> output\scan.%SUFFIX%.entity) & SET /A CTR=1)
)
ECHO:>> output\scan.%SUFFIX%.entity & SET /P "=]" <nul >> output\scan.%SUFFIX%.entity
DEL output\scan.%SUFFIX%.ent
ENDLOCAL
