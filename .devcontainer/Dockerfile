FROM python

ENV PYTHONPATH "${PYTHONPATH}:/workspaces:/workspaces/KisTest"

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
    && apt-get -y install git \
	&& rm -rf /var/lib/apt/lists/*

RUN git config --system core.ignorecase false; \
 	git config --system core.autocrlf true; 

RUN python -m pip install --upgrade pip \
    && pip install \
	numpy pandas \
	ipykernel ipywidgets \
	pandas_datareader finance-datareader pykrx

CMD [ "/bin/bash" ]