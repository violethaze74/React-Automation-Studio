FROM python:3.9.0a3-buster

# Install python dependencies
WORKDIR /usr/src/app

COPY mongoSetup/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY mongoSetup/initDBData /usr/src/app/initDBData
COPY mongoSetup/*.py ./
CMD ["python","main.py"]