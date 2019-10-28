FROM python:3

RUN pip3 install redis
RUN pip3 install pymongo

COPY mongo_cached_echo.py /
EXPOSE 65432

ENTRYPOINT ["python", "mongo_cached_echo.py"]