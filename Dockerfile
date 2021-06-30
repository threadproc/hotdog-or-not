FROM nvcr.io/nvidia/l4t-tensorflow:r32.5.0-tf2.3-py3

ENV LANG="C.UTF-8"

RUN mkdir -p /app/uploads
RUN pip3 install Flask==2.0.1 Pillow==8.2.0

COPY . /app/

WORKDIR "/app"
CMD ["/usr/local/bin/flask", "run", "--host", "0.0.0.0", "--port", "8080"]