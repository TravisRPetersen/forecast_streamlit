FROM python:3.7-slim
EXPOSE 8501
COPY requirements.txt /
COPY . /app
WORKDIR /app

RUN pip3 install -r /requirements.txt
RUN rm /requirements.txt

CMD [ "streamlit", "run", "app/forecast.py" ]
