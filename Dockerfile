FROM python:latest

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY test/test_requirements.txt ./test/
RUN pip install --no-cache-dir -r test/test_requirements.txt

COPY . .
EXPOSE 5000
CMD ["python", "run.py"]