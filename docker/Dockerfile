#FROM nkeetha/splatam:v1
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive

# Set default user and group arguments that can be overwritten with input args
ARG UNAME=testuser
ARG UID=1000
ARG GID=1000

RUN mkdir -p /ws
WORKDIR /ws

RUN apt-get update -y \
    && apt-get install software-properties-common -y \
    && add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update -y && apt-get install -y \
        python3.10 
RUN apt-get update -y && apt-get install -y \
        python3.10-dev 
RUN apt-get update -y && apt-get install -y \
        python3.10-venv 
RUN apt-get update -y && apt-get install -y \
        git
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
RUN ldconfig

# Create user
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME
USER $UNAME

CMD ["/bin/bash"]

