FROM python:3.12

COPY requirements.txt /opt/

RUN pip install -r /opt/requirements.txt

COPY app/ /opt/app/

WORKDIR /opt/app

CMD ["python", "engine.py"]
