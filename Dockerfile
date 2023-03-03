FROM python:3.10-slim
RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential
RUN set -xe
ENV PATH="/root/.local/bin:$PATH"
WORKDIR app
COPY . .
RUN pip install -r requirements.txt
RUN chmod 755 ./run.sh
RUN chmod +x ./run.sh
ENTRYPOINT ["./run.sh"]
CMD [""]