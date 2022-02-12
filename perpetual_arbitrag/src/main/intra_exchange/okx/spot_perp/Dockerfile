FROM python:3.7.12

ENV workdir /app
ENV PYTHONPATH ${workdir}:${PYTHONPATH}

WORKDIR ${workdir}
COPY . ${workdir}

RUN pip3 --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install -r requirements.txt
RUN pip3 install git+https://github.com/JKOK005/Open-API-SDK-V5.git#subdirectory=okx-python-sdk-api-v5
# RUN pip3 install https://github.com/coinrising/okex-api-v5/archive/master.zip

CMD [ "python", "./main/intra_exchange/okx/spot_perp/main.py" ]