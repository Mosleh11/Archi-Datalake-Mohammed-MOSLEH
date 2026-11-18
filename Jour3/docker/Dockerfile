# Environnement Jour 3 : Python + PySpark + Jupyter (mode local, pas de cluster)
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-21-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
RUN pip install --no-cache-dir pyspark pyarrow nbformat nbconvert ipykernel
WORKDIR /work
