FROM alpine:edge
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && \ 
    apk add --no-cache make automake gcc g++ subversion python3-dev bash parallel openjdk8-jre python3 openblas openblas-dev musl-dev
   
RUN pip3 install cython numpy==1.16.4

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN mkdir -p /opt/faro
COPY . /opt/faro
WORKDIR /opt/faro
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN wget -O /tmp/tika-server.jar https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.21/tika-server-1.21.jar
RUN wget -O /tmp/tika-server.jar.md5 https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.21/tika-server-1.21.jar.md5
RUN touch /root/.bashrc \
   && echo "java -jar /tmp/tika-server.jar -h 0.0.0.0 &" >> /root/.bashrc
RUN chmod +x faro_docker.sh && chmod +x faro_spider.sh
ENTRYPOINT ["bash", "faro_docker.sh"]
