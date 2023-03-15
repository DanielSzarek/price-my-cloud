FROM python:3.10.7-slim as base-python

ENV PATH=/venv/bin:$PATH \
    VIRTUAL_ENV=/venv
RUN apt update \
  && apt install -y git graphviz


FROM base-python as builder

RUN apt install -y python3-pip python3-dev build-essential libxml2-dev libxslt-dev libffi-dev \
  && apt autoremove -y

RUN python -m venv /venv

RUN pip install --upgrade pip==22.2.2
RUN pip install poetry==1.1.13
RUN poetry config virtualenvs.create false

COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install -n -vvv


FROM base-python as runtime
COPY --from=builder /venv /venv

COPY . /src
WORKDIR /src/src

EXPOSE 8080

CMD python ./manage.py runserver_plus 0.0.0.0:8080 --settings=dsm.settings
