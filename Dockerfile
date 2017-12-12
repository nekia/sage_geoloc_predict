FROM mxnet/python:latest 
WORKDIR /app 
COPY *.py /app/ 
COPY grids.txt /app/ 
COPY models /app/models 
COPY mediaeval2016_test /app/
RUN pip install -U numpy flask scikit-image 
ENTRYPOINT ["python", "app.py"] 
EXPOSE 8080
