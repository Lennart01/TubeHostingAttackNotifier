FROM debian:latest
RUN apt-get update &&\
    apt-get install python3-pip -y

Run pip3 install datetime requests

RUN mkdir -p /TubeHostingAttackNotifier/
ADD main.py /TubeHostingAttackNotifier/.


CMD ["python3 /TubeHostingAttackNotifier/main.py -p $passwd -m $mail -u $url"]
ENTRYPOINT ["/bin/bash", "-c"]