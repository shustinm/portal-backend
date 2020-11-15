FROM python:3.9

RUN mkdir /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

COPY portal portal

CMD ["python", "portal/app.py"]
