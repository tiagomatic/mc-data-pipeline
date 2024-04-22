FROM chainguard/python:latest-dev

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app.py requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "/app/app.py"]
