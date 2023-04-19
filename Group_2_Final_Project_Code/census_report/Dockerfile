FROM python:3.9-alpine
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["-m", "flask", "--app", "census_report", "run", "--host=0.0.0.0", "--port=5050"]