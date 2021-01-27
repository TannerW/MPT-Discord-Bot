FROM python:3

ADD MPT.py /

RUN pip install discord.py
RUN pip install python-dotenv

CMD [ "python", "./MPT.py" ]
