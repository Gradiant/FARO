FARO (Document Sensitivity Detector)
------------------------------------

![FARO LOGO](img/faro_logo4b.png)

## Table of contents

* [What is this](#what-is-this)
* [What's in here?](#whats-in-here)
* [Run FARO with Docker](#run-faro-with-docker)
* [Run FARO on host machine](#run-faro-on-host-machine)
    * [Prerequisites](#prerequisites)
    * [Virtual environment](#virtualenvironment)
    * [Dependencies](#dependencies)
    * [NER models](#ner-models)
    * [FARO Spider](#faro-spider)
    * [Single File Detection](#single-file-detection)
* [Technical Details](#technicaldetails)
    * [FARO entity detector](#faro-entity-detector)
    * [Configuration](#configuration)
    * [Supported Input File Formats](#supported-input-file-formats)
    * [Techniques](#techniques)
    * [Testing](#testing)
    * [Install Git-LFS](#install-git-lfs)
    * [FARO detection additional arguments](#faro-detection-additional-arguments)
    * [Known issues](#knownissues)
* [Contributors](#contributors)


## What is this

FARO is a tool for detecting sensitive information in documents in an organization. It is oriented to be used by small companies and particulars that want to track their sensitive documents inside their organization but who cannot spend much time and money configuring complex Data Protection tools.


FARO extract sensitivity indicators from documents (e.g. Document IDs, monetary quantities, personal emails) and gives a senstivity score to the document (from low to high) using the frequence and type of the indicators in the document.

Currently all the functionality of this tool is for documents written in Spanish although it can be easily upgraded to cover more languages.

This tool is developed by [TEGRA R&D Cybersecurity Center](#contributors).

## What’s in here?

The project contains the following folders:

 * `faro/` : this is FARO module with the main functionality.
 * `config/`: yaml configuration files go here. There is one yaml file per language (plus one `nolanguage.yaml` to provide basic functionality for non detected languages) and one yaml file with common configurations for all languages `config/commons.yaml`.
 * `models/`: this is the folder to place your models.
 * `faro_detection.py`: launcher of FARO for standalone operation over a single file.
 * `faro_spider.sh`: script for bulk processing.
 * `docker_build_faro.sh`: script for building FARO docker image in Linux and Mac OS.
 * `docker_build_faro.bat`: script for building FARO docker image in Windows.
 * `docker_run_faro.sh`: script for running a FARO container in Linux and Mac OS.
 * `docker_run_faro.bat`: script for running a FARO container in Windows.
 * `log4j.properties`: tweak tika server logging to avoid excesive verbosity, mainly coming from PDFBox.
 * `CHANGELOG`: FARO changelog.

## Run FARO with Docker

FARO can run as a standalone container using Docker. You can build the image for yourself. Soon, we will also make FARO available in DockerHub.

### Build FARO image

Provided you have Docker installed and running on your system, do the following to build the FARO image.

Linux and Mac OS

```
./docker_build_faro.sh
```

Windows

```
docker_build_faro.bat
```

### Run FARO container

To run a FARO container some scripts are provided in the root of the project. You can copy and use those scripts from anywhere else for convenience. The "output" folder will be created under your current directory.

Linux and Mac OS

```
./docker_run_faro.sh <your folder with files>
```

Windows

```
./docker_run_faro.bat <your folder with files>
```

### Results

FARO creates an "output" folder inside the current folder and stores the results of the execution in two files:

 * `output/scan.$CURRENT_TIME.csv`: is a csv file with the score given to the document and the frequence of indicators in each file.

```
filepath,score,person_position_organization,monetary_quantity,signature,personal_email,mobile_phone_number,financial_data,document_id,custom_words,content-type
/Users/test/code/FARO/data/quick_test_data/con espacio/20190912-FS2019-0177717-36155797G.pdf,high,0,3,0,0,0,0,1,2,application/pdf
/Users/test/code/FARO/data/quick_test_data/Factura_NRU_23092019_2104054_0_1_001.pdf,high,0,0,0,0,0,0,1,4,application/pdf
/Users/test/code/FARO/data/quick_test_data/Factura_273496_Plancha.pdf,high,0,6,0,0,1,0,2,4,application/pdf
/Users/test/code/FARO/data/quick_test_data/20190912-FS2019-0177717-36155797G.pdf,high,0,3,0,0,0,0,1,2,application/pdf
/Users/test/code/FARO/data/quick_test_data/informe_tecnico_FARO.rtf,high,0,3,0,2,0,0,3,6,application/rtf
```

* `output/scan.$CURRENT_TIME.entity`: is a json with the list of indicators (disaggregated) extracted in a file. For example:

```
{"filepath": "/Users/test/code/FARO/data/quick_test_data/con espacio/20190912-FS2019-0177717-36155797G.pdf", "entities": {"document_id": {"A-28046316": 1}, "custom_words": {"factura": 1, "total": 1}, "monetary_quantity": {"3,06": 1, "0,64": 1, "3,70": 1}}, "datetime": "2019-11-05 12:52:55", "Content-Type": "application/pdf"}
{"filepath": "/Users/test/code/FARO/data/quick_test_data/Factura_NRU_23092019_2104054_0_1_001.pdf", "entities": {"custom_words": {"facturar": 3, "total": 1}, "prob_currency": {"12,0021": 1, "12,00": 1, "9,92": 1, "3,9921": 1, "3,99": 1, "3,30": 1, "15,99": 1, "13,21": 1, "1.106.166": 1, "1,00": 1, "99,00": 1}, "document_id": {"A-60195278": 1}}, "datetime": "2019-11-05 12:52:59", "Content-Type": "application/pdf"}
{"filepath": "/Users/test/code/FARO/data/quick_test_data/Factura_273496_Plancha.pdf", "entities": {"document_id": {"B95662888": 1, "53048482V": 1}, "mobile_phone_number": {"680217067 ": 1}, "custom_words": {"factura": 1, "facturar": 1, "total": 1, "importe": 1}, "monetary_quantity": {"156,20": 2, "2,84": 1, "0,00": 1, "159,04": 1, "32,80": 2, "191,84": 1}, "prob_currency": {"1,00": 3, "189,00": 1}}, "datetime": "2019-11-05 12:53:03", "Content-Type": "application/pdf"}
{"filepath": "/Users/test/code/FARO/data/quick_test_data/20190912-FS2019-0177717-36155797G.pdf", "entities": {"document_id": {"A-28046316": 1}, "custom_words": {"factura": 1, "total": 1}, "monetary_quantity": {"3,06": 1, "0,64": 1, "3,70": 1}}, "datetime": "2019-11-05 12:53:07", "Content-Type": "application/pdf"}
{"filepath": "/Users/test/code/FARO/data/quick_test_data/informe_tecnico_FARO.rtf", "entities": {"custom_words": {"confidencial": 1, "contrato": 1, "cr\u00e9dito": 2, "facturar": 1, "total": 1}, "email": {"merpastor@icav.es": 1, "soia@csic.es": 1}, "document_id": {"X4813918H": 1, "X4658630A": 2, "B07411598": 1}, "monetary_quantity": {"61.305,12": 1, "66.500,47": 1, "0,00": 1}}, "datetime": "2019-11-05 12:56:12", "Content-Type": "application/rtf"}
```

## Run FARO On Host Machine

**NOTE: ONLY LINUX AND MAC OS X**

### Prerequisites

The mode requires some operative system and libraries in order to work properly

 * Linux or Mac OS
 * Java 1.7 or higher
 * virtualenv (not required but highly recommended)
 * GNU parallel (to speed up our spider script. You can see more information about the tool [here](https://www.jduck.net/blog/2014/09/30/gnu-paralell/)
 * [git lfs](https://git-lfs.github.com/) installed.

### Virtual Environment

It is advisable to use a separate virtual environment. To instantiate a virtual environment with virtualenv.

```
virtualenv -p `which python3` <yourenvname>
```

To activate the virtual environment on your terminal just type:

```
source <yourenvname>/bin/activate
```

### Dependencies

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

### NER models

FARO relies on several ML models in order to work.

```
detection:
    nlp_model : es_core_news_sm
    crf_ner_list: models/crf_professions_v1.joblib
    personal_email_detection: models/email_detector.joblib
    target_list: models/legal.txt
    crf_ner_classic: models/crf_classic_step1.joblib,models/crf_classic_step2.joblib,models/crf_classic_step3.joblib,models/crf_classic_step4.joblib,models/crf_classic_step5.joblib
    corp_mail_list: models/corp_mail_list.txt

```

In our repository we are handling models through Git LFS due to their size. If you have [git-lfs](https://git-lfs.github.com/) installed you should automatically have the models downloaded when you first clone our repo.

If you want to download models manually execute the following command from the root of the project.
```
git lfs pull
```

Check that the paths shown below inside config/es.yml file point to the models.

### FARO spider

Our spider is a script to recursively analyse the documents inside a folder, storing the results of the analysis on a file.

```
./faro_spider.sh <your folder with files>
```

### Single file detection

You can execute faro detection over a single file by using our `faro_detection.py` script

```
./faro_detection.py -i <your_file>

```

Two output files are generated with the paths <your_file>.entity and <your_file>.score.

a) `<your_file>.entity`: a json with the list of entities ordered by their type and the number of appearances (output of the entity detector module):

```
{"LOC": {"Pontevedra": 1}, "MONEY": {"1.000 euros": 2}, "PER": {"Betty Corti\u00f1as": 1, "Eva Expósito": 1, "Belén Portela": 1, "Marta Rivadulla": 1, "Miguel Rivas": 1}, "PROF": {"el tutor": 1}, "ORG": {"Centro de Recursos Educativos": 1}}

```

b) `<your_file>.score`:  a json with the types of entities and the number this type of entity appears in the text. This json also contains the sensitivy score in the property "score" (it can be "low", "medium" and "high").

```
{"score": "high", "summary": {"monetary_quantity": 1, "person_position": 1, "mobile_phone_number": 1, "personal_email": 1, "credit_account_number": 2}}
```

For information about additional arguments that can be passed to our detection script, take a look [here](#faro-detection-additional-arguments).

## Technical Details

### FARO entity detector

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

### Configuration

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

### Supported Input File Formats

The FARO application uses Tika for document processing. Therefore all the formats that Tika process can be used as input. Nevertheless, the faro_spider.sh/faro_spider.bat scripts for bulk processing are restricted to the following extensions: .doc, .docx, .pptx, .ppt, .xls, .pdf, .odt, .ods, .odp, .txt and .rtf.

### Techniques

FARO uses NER (built with CRFs) for extracting classic entities (Person, Organization and Location) and Jobpositions.

Other indicators are extracted with RegExp (document ids, phone and credit card numbers, etc).

Mails are extracted with RegExp. A ML classifier and heuristics are used to distinguish between corporative and personal emails.

### Testing

FARO has several tests to verify the functionality of the system (currently the tests only cover the regular expressions). Tests can be executed with the following command:

```
python test_suite.py
```

### Faro Detection Additional Arguments

`--dump`: the system dumps the information of <your_file>.score to stdout in csv format. E.g. an example of output might be:

```
id_file,score,person_jobposition_organization,monetary_quantity,sign,personal_email,mobile_phone_number,credit_account_number,id_document
data/test/test2.pdf,medium,3,0,1,0,0,0,0

```

The paths of the output files can be explicitly set in the command line using `--output_entity_file` and `--output_score_file`

```
python faro_detection.py --input_file <your_file> --output_entity_file <path to output> --output_score_file <path to output>
```

The default behaviour of our detection script is to show only the type of entities that directly affects the sensitivity score. In order to show all the entities detected use the parameter `--verbose` at the command line.

There is an additional parameter (`--split_lines`) that must be used with documents in which every line of the document is a sentence (or paragraph). By default, FARO tries to join lines in the document because in many cases a different line does not imply a different sentence (e.g. in PDFs).

### Install Git-lfs

Follow the instructions to install git-lfs (GIT Large File Storage) depending on

#### Linux

Download the package in https://git-lfs.github.com/ and follow the installation instructions.

#### Windows

Install "git bash" in Windows (check the windows section in this link https://git-scm.com/downloads) and afterwards visit https://git-lfs.github.com/ and follow the installation instructions.

#### Mac OS

```
brew install git-lfs
git lfs install
```

A `models` folder will be created with all the models inside.

### Known Issues <a name="knownissues"></a>

* The full functionality only works with Spanish documents although it is easily expandable with new languages (especially if they are supported with SpaCy, the NLP tool used to process the sentence, documents).

* The system uses SpaCy for parsing and PoS sentence preprocessing. Although the SpaCy provides a trained NER system for classical entities, custom NERs are used for the extraction of classical entities (Person, Organization, Localization) and the Professions/job position.

## Contributors

TEGRA is an R&D Cybersecurity Center based in Galicia (Spain). It is a joint effort from Telefónica, a leading international telecommunications company, through ElevenPaths, its global cybersecurity unit, and Gradiant, an ICT R&D center with more than 100 professionals working in areas like connectivity, security and intelligence, to create innovative products and services inside cybersecurity.

TEGRA's work is focused on two areas within the cybersecurity landscape: Data Security and Security Analytics. We are committed to creating state-of-the-art technologies that can nurture and thus provide differentiating value to our products.

See the [CONTRIBUTORS](CONTRIBUTORS) file.