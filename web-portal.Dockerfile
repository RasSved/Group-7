# Stage 1 - Install dependencies and run health check
FROM python:3.11.8

WORKDIR /app

RUN pip install Flask

RUN pip install pymongo

RUN pip install werkzeug

RUN pip install flask_wtf

COPY . .

CMD ["./startApp.sh"]