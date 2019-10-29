FROM python:3.7.5-buster as wheels-builder

RUN pip3 install --upgrade pip
RUN pip3 wheel python-Levenshtein==0.12.0 regex==2019.8.19


FROM python:3.7.5-slim-buster

# We copy first requirements.txt to build-cache requirements if not changed
COPY requirements.txt /

COPY --from=wheels-builder /python_Levenshtein-0.12.0-cp37-cp37m-linux_x86_64.whl /regex-2019.8.19-cp37-cp37m-linux_x86_64.whl /

#parallel footprint is ~ 180MB, it install perl and sysstat that depends on python2 ...
ENV JAVA_HOME=/usr/lib/jvm/default-jvm/
RUN mkdir -p /usr/share/man/man1 && echo "deb http://deb.debian.org/debian unstable main" > /etc/apt/sources.list.d/91-unstable.list && \
    apt update && apt install -y openjdk-8-jre-headless wget && rm /etc/apt/sources.list.d/91-unstable.list && rm -rf /var/lib/apt/lists/* && \
    cd /usr/lib/jvm && ln -s java-8-openjdk-amd64 default-jvm && \
    pip3 install --upgrade pip && \
    pip3 install /python_Levenshtein-0.12.0-cp37-cp37m-linux_x86_64.whl /regex-2019.8.19-cp37-cp37m-linux_x86_64.whl && \
    pip3 install -r /requirements.txt && \
    mkdir -p /usr/share/man/man1 &&  apt-get update && apt-get install -y openjdk-11-jre-headless parallel bash wget && rm -rf /var/lib/apt/lists/* && \
    wget -O /tmp/tika-server.jar https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.21/tika-server-1.21.jar && \
    wget -O /tmp/tika-server.jar.md5 https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.21/tika-server-1.21.jar.md5

COPY . /opt/faro
WORKDIR /opt/faro
# Get models from Git LFS
RUN cd /opt/faro/models && \
    wget https://github.com/Gradiant/FARO/raw/master/models/corp_mail_list.txt && \
    wget -O /opt/faro/models/crf_classic_step1.joblib https://github.com/Gradiant/FARO/raw/master/models/crf_classic_step1.joblib && \
    wget -O /opt/faro/models/crf_classic_step2.joblib https://github.com/Gradiant/FARO/raw/master/models/crf_classic_step2.joblib && \
    wget -O /opt/faro/models/crf_classic_step3.joblib https://github.com/Gradiant/FARO/raw/master/models/crf_classic_step3.joblib && \
    wget -O /opt/faro/models/crf_classic_step4.joblib https://github.com/Gradiant/FARO/raw/master/models/crf_classic_step4.joblib && \
    wget -O /opt/faro/models/crf_classic_step5.joblib https://github.com/Gradiant/FARO/raw/master/models/crf_classic_step5.joblib && \
    wget -O /opt/faro/models/crf_professions_v1.joblib https://github.com/Gradiant/FARO/raw/master/models/crf_professions_v1.joblib && \
    wget -O /opt/faro/models/email_detector.joblib https://github.com/Gradiant/FARO/raw/master/models/email_detector.joblib

ENTRYPOINT ["./entrypoint.sh"]
