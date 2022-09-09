FROM python:3.8.14


ADD ./adminDbInit adminDbInit
WORKDIR /adminDbInit

RUN pip install -r requirements.txt



ENTRYPOINT ["python"]

CMD ["-u","initDB.py"]

EXPOSE 27017
