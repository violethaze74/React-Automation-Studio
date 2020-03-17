FROM python:3.7.5



ADD ./adsServer/requirements.txt /adsServer/requirements.txt
WORKDIR /adsServer

RUN pip install -r requirements.txt




ADD ./adsServer /adsServer

WORKDIR /adsServer


ENV adsServerBASEURL=http://127.0.0.1
ENV adsServerPORT=5002
ENV REACT_APP_PyEpicsServerNamespace=adsServer
ENV REACT_APP_EnableLogin=false

ENV EPICS_CA_ADDR_LIST="0.0.0.0:8001"
ENV PYEPICS_LIBCA=/epics/base/lib/linux-x86_64/libca.so

ENV PATH="/epics/base/bin/linux-x86_64/:${PATH}"
#RUN echo $PATH
RUN echo $adsServerBASEURL
RUN echo $adsServerPORT
RUN echo $REACT_APP_PyEpicsServerNamespace

#RUN ls /epics/base/lib/linux-x86_64/


RUN mkdir /build
VOLUME /adsServer/userAuthentication/users



CMD python adsServer.py
EXPOSE  5002 48898
