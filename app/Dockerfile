FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    locales \
    && sed -i -e 's/# ja_JP.UTF-8 UTF-8/ja_JP.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

ENV LANG ja_JP.UTF-8
ENV LC_ALL ja_JP.UTF-8

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

CMD ["python", "-m", "src.main", "--wait", "60000"]