FROM python:3.8-alpine3.14

Run pip3 install datetime requests

WORKDIR /TubeHostingAttackNotifier/

COPY . . 

ENTRYPOINT python ./main.py -p $passwd -m $mail -u $url
