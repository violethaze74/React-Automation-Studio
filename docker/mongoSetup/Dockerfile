FROM python:3.9.0a3-buster

# Install python dependencies
WORKDIR /usr/src/app

COPY alarmHandlerServer/src/python/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY alarmHandlerServer/src/python/mongoSetup/initDBData /usr/src/app/initDBData
COPY alarmHandlerServer/src/python/mongoSetup/*.py ./
CMD ["python","main.py"]