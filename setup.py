from setuptools import setup, find_packages


setup(name="faro",
      version='1.2.0',
      description="FARO core module",
      url='https://github.com/Gradiant/FARO',
      author='Héctor Cerezo',
      license='Copyright 2021 GRADIANT. All rights reserved.',
      packages=find_packages(),
      install_requires=[
          'fuzzywuzzy==0.17.0',
          'gensim==3.7.3',
          'langdetect==1.0.7',
          'mox==0.5.3',
          'murmurhash==1.0.2',
          'numpy==1.16.4',
          'pandas==0.24.2',
          'python-Levenshtein==0.12.1',
          'PyYAML==5.1.1',
          'scikit-learn==0.21.2',
          'sklearn-crfsuite==0.3.6',
          'python-dateutil==2.8.0',
          'tika==1.23',
          'unittest-xml-reporting==2.5.1',
          'luhn==0.2.0',
          'python-stdnum==1.11',
          'joblib==0.13.2',
          'regex==2019.8.19',
          'scipy==1.3.1',
          'spacy==2.1.4',
          'typer==0.3.2',
          'Flask==1.1.2',
          'flask-restful==0.3.8',
          'flask-cors==3.0.10',
          'es_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-2.1.0/es_core_news_sm-2.1.0.tar.gz'
      ],
      dependency_links=[],
      zip_safe=False)


