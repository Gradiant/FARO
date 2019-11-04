FROM python:3.7.5-buster as wheels-builder

RUN pip3 install --upgrade pip
RUN pip3 wheel python-Levenshtein==0.12.0 regex==2019.8.19


FROM python:3.7.5-slim-buster

ENV VERSION=1.0.1

# We copy first requirements.txt to build-cache requirements if not changed
COPY requirements.txt /

COPY --from=wheels-builder /python_Levenshtein-0.12.0-cp37-cp37m-linux_x86_64.whl /regex-2019.8.19-cp37-cp37m-linux_x86_64.whl /

ENV JAVA_HOME=/usr/lib/jvm/default-jvm/
RUN mkdir -p /usr/share/man/man1 && echo "deb http://deb.debian.org/debian unstable main" > /etc/apt/sources.list.d/91-unstable.list && \
    apt-get update && apt-get install -y openjdk-8-jre-headless && rm /etc/apt/sources.list.d/91-unstable.list && rm -rf /var/lib/apt/lists/* && \
    cd /usr/lib/jvm && ln -s java-8-openjdk-amd64 default-jvm && \
    pip3 install --upgrade pip && \
    pip3 install /python_Levenshtein-0.12.0-cp37-cp37m-linux_x86_64.whl /regex-2019.8.19-cp37-cp37m-linux_x86_64.whl && \
    pip3 install -r /requirements.txt && \
    apt-get update && apt-get install -y parallel bash wget && rm -rf /var/lib/apt/lists/* && \
    wget -O /tmp/tika-server.jar https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.21/tika-server-1.21.jar
COPY . /opt/faro
WORKDIR /opt/faro


ENTRYPOINT ["./entrypoint.sh"]
