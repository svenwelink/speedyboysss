FROM python:3.14

WORKDIR /app

COPY getData.py .

RUN pip install requests pandas

CMD ["python", "-u", "getData.py"]
