FROM python:3.9.6

COPY . /app

RUN pip install -r /app/requirements.txt

ENV MYSQL_HOST=database-project-pwr.mysql.database.azure.com
ENV MYSQL_USER=project0admindb
ENV MYSQL_PASSWORD=dzbany&p0rcelanyDB*k0l
ENV MYSQL_DB=dbp2

CMD ["python", "/app/app.py"]