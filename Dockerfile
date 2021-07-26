FROM python:3.7

RUN pip install flask
ENV FLASK_APP /kickup/kickup.py

COPY kickup /kickup

CMD ["python","/kickup/kickup.py"]
