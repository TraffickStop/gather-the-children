FROM public.ecr.aws/lambda/python:3.8

RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm -o chrome-download.rpm
RUN yum install chrome-download.rpm -y
RUN rm chrome-download.rpm

RUN yum install unzip -y

RUN curl https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip -o chromedriver.zip
RUN unzip chromedriver.zip
RUN rm -rf chromedriver.zip 

COPY . .

RUN pip install -r requirements.txt

CMD ["app.handler"]