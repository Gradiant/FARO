# FARO (Document Sensitivity Detector)

<p align="left">
<img src="./img/faro_logo4b.png"/>
</p>

## Table of contents

 * [What is this](#whatisthis)
 * [Install FARO](#installation)
     * [Prerequisites](#prerequisites)
     * [Using a virtual environment in Linux and Mac OS](#virtualenvironment)
     * [Installation of dependencies](#dependencies)
     * [Downloading the models](#modelsdownload) 
 * [Run FARO](#runtheproject)
 * [Run FARO on a single file](#singletest)
 * [Run FARO with Docker](#docker)
 * [Technical Details](#technicaldetails)
     * [What’s in here](#whatisinhere)
     * [FARO entity detector](#faroentitydetectorintro)
     * [Configuring FARO](#configuringfaro)
     * [Input Formats](#inputformats)
     * [Techniques](#techniques)
     * [Known issues](#knownissues)
     

## What is this <a name="whatisthis"></a>

FARO is a tool for detecting sensitive information in documents in an organization. It is oriented to be used by small companies and particulars that want to track their sensitive documents inside their organization but who cannot spend much time and money configuring complex Data Protection tools.


FARO extract sensitivity indicators from documents (e.g. Document IDs, monetary quantities, personal emails) and gives a senstivity score to the document (from low to high) using the frequence and type of the indicators in the document.

Currently all the functionality of this tool is for documents written in Spanish although it can be easily upgraded to cover more languages.


## Install FARO <a name="installation"></a>

The preferred way to use FARO is through its Docker image. Developers and testers can however set up the appropriate environment to run FARO from source code (see next sections).

### FARO with Docker <a name="docker"></a>

FARO can run as a standalone container using Docker. You can build the image for yourself. Soon, we will also make FARO available in Docker Hub.

#### Build FARO image

Provided you have Docker installed and running on your system, do the following to build the FARO image.

Linux and Mac OS

```
./docker_build_faro.sh
```

Windows

```
docker_build_faro.bat
```

#### Run FARO container

To run a FARO container some scripts are provided in the root of the project. You can copy and use those scripts from anywhere else for convenience. The "output" folder will be created under your current directory.

Linux and Mac OS

```
./docker_run_faro.sh <your folder with files>
```

Windows

```
./docker_run_faro.bat <your folder with files>
```

### Install FARO (for developers)

#### Prerequisites <a name="prerequisites"></a>

The mode requires some operative system and libraries in order to work properly

 * Linux or Mac OS (Windows can also execute single file analysis)
 * Java 1.7 or higher
 * virtualenv (not required but highly recommended)
 * GNU parallel (to execute the bash spider scripts in Linux and Mac OS. You can see more information about the tool in the following <a href="https://zenodo.org/record/1146014#.XSXolp9fjCJ" target="GNU parallel">link</a>;
 * git lfs installed. Check [Downloading models](#modelsdownload) for specific instructions for your operative system.

#### Using a virtual environment <a name="virtualenvironment"></a>

It is advisable to use a separate virtual environment. To instantiate a virtual environment with virtualenv.

```
virtualenv -p `which python3` <yourenvname>
```

To activate the virtual environment on your terminal just type:

```
source <yourenvname>/bin/activate
```

#### Dependencies: <a name="dependencies"></a>

The easiest way of getting the system up and running is to install the dependencies this way

```
pip install -r requirements.txt
```

The list of dependencies are the following:

* SpaCy with at least the spanish language model
* numpy
* scipy
* sklearn
* gensim
* sklearn-crfsuite
* fuzzywuzzy
* tika
* gensim
* pyyaml
* pandas

These other dependencies are used for testing:
* mox
* unittest-xml-reporting

### Downloading the models <a name="modelsdownload"></a>

FARO relies on several ML models in order to work. Models are tracked with Git LFS. Installing this tool is the easiest way to download the models.

#### Linux

Download the package in https://git-lfs.github.com/ and follow the installation instructions.

#### Windows

Install "git bash" in Windows (check the windows section in this link https://git-scm.com/downloads) and afterwards visit https://git-lfs.github.com/ and follow the installation instructions.

#### Mac OS

```
brew install git-lfs
git lfs install
```

A `models` folder will be created with all the models inside. If you want to download models manually execute the following command from the root of the project.
```
git lfs pull
```

Check that the paths shown below inside config/es.yml file point to the models.

```
detection:
    nlp_model : es_core_news_sm
    crf_ner_list: models/crf_professions_v1.joblib
    personal_email_detection: models/email_detector.joblib
    target_list: models/legal.txt
    crf_ner_classic: models/crf_classic_step1.joblib,models/crf_classic_step2.joblib,models/crf_classic_step3.joblib,models/crf_classic_step4.joblib,models/crf_classic_step5.joblib
    corp_mail_list: models/corp_mail_list.txt

```

## Run the project (Quick - requires GNU parallel)<a name="runtheproject"></a>

The spiders are scripts to recursively analyse the documents inside a folder, storing the results of the analysis on a file.

### FARO spider

Example of execution (Linux and Mac OS)

```
./faro_spider.sh <your folder with files>
```

Execution on Windows

Currently, processing multiple documents in Windows is only available through dockerized FARO (see below).

The script creates an "output" folder in the root of the project and stores the results of the execution in two files:

 * output/scan.$CURRENT_TIME.csv: is a csv file with the score given to the document and the frequence of indicators in each file.

```
filepath,score,person_position_organization,monetary_quantity,signature,personal_email,mobile_phone_number,financial_data,document_id
data/test/FacturaSencilla.pdf,high,0,0,0,1,0,0,2
data/test/test3.pdf,high,0,0,0,0,0,1,6
data/test/test4.pdf,medium,0,0,0,3,0,0,0

```

* output/scan.$CURRENT_TIME.entity: is a json with the list of indicators (disaggregated) extracted in a file. For example:

```
[
{"datetime": "2019-06-28 13:22:35", "filepath": "/media/hcerezo/7ab36923-d61a-42bf-b119-e1820eb4fa224/phpboe/boe/dias/2019/01/08/pdfs/BOE-B-2019-411.pdf", "entities": {}},
{"filepath": "/media/hcerezo/7ab36923-d61a-42bf-b119-e1820eb4fa224/phpboe/boe/dias/2019/01/08/pdfs/BOE-B-2019-422.pdf", "datetime": "2019-06-28 13:22:37", "entities": {"document_id": {" X4813918H ": 2, " X4658630A ": 1, "  X4658630A,": 1}, "email": {"merpastor@icav.es": 1}}},
{"filepath": "/media/hcerezo/7ab36923-d61a-42bf-b119-e1820eb4fa224/phpboe/boe/dias/2019/01/08/pdfs/BOE-B-2019-392.pdf", "entities": {}, "datetime": "2019-06-28 13:22:48"},
{"entities": {"email": {"soia@csic.es": 1}, "document_id": {" B07411598.": 1}, "monetary_quantity": {"61.305,12 euros": 1, "66.500,47 euros": 1, "0,00 euros": 1}}, "filepath": "/media/hcerezo/7ab36923-d61a-42bf-b119-e1820eb4fa224/phpboe/boe/dias/2019/01/08/pdfs/BOE-B-2019-483.pdf", "datetime": "2019-06-28 13:22:51"},
]
```

## Run FARO on a single file <a name="singletest"></a>

Note: This works for Linux, MAC OS and Windows

### FARO detection module

Two scripts are provided that launch the main functionality of FARO

* FARO detection (the simple way -- only the input document is provided)

```
./faro_detection.py -i <your_file>

```

Two output files are generated with the paths <your_file>.entity and <your_file>.score.

**a) <your_file>.entity**: a json with the list of entities ordered by their type and the number of appearances (output of the entity detector module):

```
{"LOC": {"Pontevedra": 1}, "MONEY": {"1.000 euros": 2}, "PER": {"Betty Corti\u00f1as": 1, "Eva Expósito": 1, "Belén Portela": 1, "Marta Rivadulla": 1, "Miguel Rivas": 1}, "PROF": {"el tutor": 1}, "ORG": {"Centro de Recursos Educativos": 1}}

```

The default behaviour of FARO is to show only the type of entities that directly affects the sensitivity score. In order to show all the entities detected use the parameter "--verbose" at the command line.

**b) <your_file>.score**:  a json with the types of entities and the number this type of entity appears in the text. This json also contains the sensitivy score in the property "score" (it can be "low", "medium" and "high").

```
{"score": "high", "summary": {"monetary_quantity": 1, "person_position": 1, "mobile_phone_number": 1, "personal_email": 1, "credit_account_number": 2}}
```

With --dump the system dumps the information of <your_file>.score to stdout in csv format. E.g. an example of output might be:

```
id_file,score,person_jobposition_organization,monetary_quantity,sign,personal_email,mobile_phone_number,credit_account_number,id_document
data/test/test2.pdf,medium,3,0,1,0,0,0,0

```

* The paths of the output files can be explicitly set in the command line:


```
python faro_detection.py --input_file <your_file> --output_entity_file <path to output> --output_score_file <path to output>
```

There is an additional parameter (--split_lines) that must be used with documents in which every line of the document is a sentence (or paragraph). By default, FARO tries to join lines in the document because in many cases a different line does not imply a different sentence (e.g. in PDFs).


With --dump the system dumps the information of <your_file>.score to stdout in csv format. E.g. an example of output might be:

There is an additional parameter (--split_lines) that must be used with documents in which every line of the document is a sentence (or paragraph). By default, F@RO tries to join lines in the document because in many cases a different line does not imply a different sentence (e.g. in PDFs).

## Technical Details <a name="technicaldetails"></a>

### What’s in here <a name="whatisinhere"></a>

The project contains the following folders:

 * **faro/** : this is the module FARO with the main functionality.
 * **config/**: yaml configuration files go here. There is one yaml file per language (plus one "blank.yaml" to provide basic functionality for non detected languages) and one yaml file with common configurations for all languages "config/commons.yaml"
 * **models/**: this is the folder to place your models. Any other folder is ok whilst the yaml configuration files points to the right locations of the models.
 * **faro_detection.py**: launcher of FARO for standalone operation (testing one file)
 * **faro_spider.sh**: script for bulk processing in Mac OS and Linux
 * **docker_build_faro.sh**: script for building FARO docker image in Linux and Mac OS
 * **docker_build_faro.bat**: script for building FARO docker image in Windows
 * **docker_run_faro.sh**: script for running a FARO container in Linux and Mac OS
 * **docker_run_faro.bat**: script for running a FARO container in Windows


### FARO entity detector <a name="faroentitydetectorintro"></a>

The FARO entity detector performs two steps:

1) Extraction of sensitivity indicators: the indicators are entities and other text elements (e.g. monetary quantities) which likely appear in sensitivity documents.

The list of indicators are the following:

 * **person_position_organization**: this is a group of entities (Person, Job - Position, Organization) that were extracted and linked together from the documents.

 * **monetary_quantity**: money quantity (currently only euros and dollars are supported).

 * **signature**: it outputs the person who signs a document

 * **personal_email**: emails that are not corporative (e.g. not info@ rrhh@ )

 * **mobile_phone_number**: mobile phone numbers (filtering out non mobile ones)

 * **financial_data**: credit cards and IBAN account numbers

 * **document_id**: Spanish NIF and CIF.

The unique counts of these sentences are gathered in a json object and relayed as input to the next step.

2) Scoring the sensitivity of a document: a classification rule is applied (using thresholds) to the indicators extracted in phase 1 to assign a sensitivy score to the document.

The following rules are applied:

* Every sensitivity level sets thresholds for the sentivity indicators. A document must comply with at least one of the thresholds (min and max) in order to get that score.

* If different sensitivity thresholds appear in the document (currently configured to three), the documents levels up the sensitivy score in spite of complying with all the thresholds for the level.

* The "low" score is also assigned to documents where no sensitivity indicator was found


### Configuring FARO <a name="configuringfaro"></a>

It employs a YAML set of files for configuring its functionality (the YAML files are located inside the "config" folder)

* common.yaml: has the common functionality to every language

* <lang code>.yaml: has the specific configuration for a language (currently only spanish is supported: "es" code). It also indicates where the ML Models are located (e.g. by default inside the "models" folder)

#### Configuration of the sensitivity score

Those are a collection of conditions that selects a score following the specification of the configuration file. The levels are configured in the sensitivity_list sorted by their intensity (from less to more sensitive). The sensitivity dict contains the conditions (min, max) ordered by type of entity. The system only needs to fulfill one condition of a certain level in order to flag the document with that level of sensitivity. Furtheremore if multiple KPIs of a certain leve are found in the document (as marked by the sensitivity_multiple_kpis parameter), the system increases their sensitivity level (e.g. from medium to high).

```
sensitivity_list:
    - low
    - medium
    - high


sensitivity_multiple_kpis: 3

sensitivity:
    low:
        person_position:
            min: 1
            max: 5
        monetary_quantity:
            min: 1
            max: 5

        signature:
            min: 0
            max: 0

        personal_email:
            min: 0
            max: 0

        ....

```

* sensitivity_list is the list of different sensitivity scores ordered by intensity.

* sensitivity_multiple_kpis this number indicates the simultaneous number of scores in a level allowed before leveling up the sensitivy score

* sensitivity is a dict with the sensitivity conditions that must be satisfied in order to reach a sensitivity level.


### Input Formats <a name="inputformats"></a>

The FARO application uses Tika for document processing. Therefore all the formats that Tika process can be used as input. Nevertheless, the faro_spider.sh/faro_spider.bat scripts for bulk processing are restricted to the following extensions: .doc, .docx, .pptx, .ppt, .xls, .pdf, .odt, .ods, .odp, .txt and .rtf.

### Running Tests <a name="runningtests"></a>

FARO has several tests to verify the functionality of the system (currently the tests only cover the regular expressions). Tests can be executed with the following command:

```
python test_suite.py
```

### Techniques <a name="techniques"></a>

FARO uses NER (built with CRFs) for extracting classic entities (Person, Organization and Location) and Jobpositions.

Other indicators are extracted with RegExp (document ids, phone and credit card numbers, etc).

Mails are extracted with RegExp. A ML classifier and heuristics are used to distinguish between corporative and personal emails.


### Known Issues <a name="knownissues"></a>

* The full functionality only works with Spanish documents although it is easily expandable with new languages (especially if they are supported with SpaCy, the NLP tool used to process the sentence, documents).

* The system uses SpaCy for parsing and PoS sentence preprocessing. Although the SpaCy provides a trained NER system for classical entities, custom NERs are used for the extraction of classical entities (Person, Organization, Localization) and the Professions/job position.

