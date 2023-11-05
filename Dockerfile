FROM python:3.8

WORKDIR /safe-roads

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py"]