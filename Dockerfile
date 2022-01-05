# FROM python:3.9.9-slim-buster

# RUN apt-get update \
#     && apt-get install libpq-dev gcc git make -y

# WORKDIR /app

# COPY . /app


# # COPY requirements.txt .
# RUN pip install -r requirements.txt

# EXPOSE 80
# # CMD uvicorn main:app --reload
# CMD ["uvicorn", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "80", "students-api.main:app"]


FROM python:3.9.9-slim-buster AS base

FROM base AS build

RUN apt-get update \
    && apt-get install libpq-dev gcc git make -y

WORKDIR /tmp

ENV PATH=/opt/local/bin:$PATH
ENV PIP_PREFIX=/opt/local
ENV PIP_DISABLE_PIP_VERSION_CHECK=1


COPY requirements.txt .
RUN pip install -r requirements.txt


FROM base AS deploy

COPY --from=build /opt/local /opt/local
COPY --from=build /usr/lib/x86_64-linux-gnu/ /lib/x86_64-linux-gnu/ /usr/lib/

WORKDIR /app
COPY . /app

ENV PATH=/opt/local/bin:$PATH \
    PYTHONPATH=/opt/local/lib/python3.9/site-packages:/app/students-api


EXPOSE 80

CMD ["uvicorn", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "80", "students-api.main:app"]

