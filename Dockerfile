FROM python:3

ADD MPT.py /
ADD plotImage.png /

RUN pip install discord.py
RUN pip install python-dotenv
RUN pip install redis
RUN pip install datetime
RUN pip install dateutil
RUN pip install pytz
RUN pip install matplotlib
RUN pip install numpy
RUN pip install pandas

CMD [ "python", "./MPT.py" ]
