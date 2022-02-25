FROM python:3.7.12

ENV workdir /app
ENV PYTHONPATH ${workdir}:${PYTHONPATH}

WORKDIR ${workdir}
COPY . ${workdir}

RUN pip3 --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install -r requirements.txt

CMD [ "python", "./main/intra_exchange/manager/arbitrag_manager.py" ]