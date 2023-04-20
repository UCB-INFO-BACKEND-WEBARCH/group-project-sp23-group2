FROM python:3.9-alpine
COPY . /app
WORKDIR /app
RUN apk add g++ postgresql-dev cargo gcc python3-dev libffi-dev musl-dev zlib-dev jpeg-dev
RUN pip install -r requirements.txt
ENTRYPOINT ["celery"]
CMD ["-A", "job_tasks.celery_app", "worker"]