FROM python:3.7.5-buster as wheels-builder

RUN pip3 install --upgrade pip
RUN pip3 wheel python-Levenshtein==0.12.0 regex==2019.8.19


FROM python:3.7.5-slim-buster

ENV VERSION=1.1.1

# We copy first requirements.txt to build-cache requirements if not changed
COPY requirements.txt /

COPY --from=wheels-builder /python_Levenshtein-0.12.0-cp37-cp37m-linux_x86_64.whl /regex-2019.8.19-cp37-cp37m-linux_x86_64.whl /

RUN mkdir -p /usr/share/man/man1 && \
    pip3 install --upgrade pip && \
    pip3 install /python_Levenshtein-0.12.0-cp37-cp37m-linux_x86_64.whl /regex-2019.8.19-cp37-cp37m-linux_x86_64.whl && \
    pip3 install -r /requirements.txt && \
    apt-get update && apt-get install -y openjdk-11-jre-headless parallel bash wget \
    tesseract-ocr tesseract-ocr-spa && rm -rf /var/lib/apt/lists/* && \
    wget -O /tmp/tika-server.jar https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar

COPY . /opt/faro
WORKDIR /opt/faro


ENTRYPOINT ["./entrypoint.sh"]
