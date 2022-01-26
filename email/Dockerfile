FROM public.ecr.aws/lambda/python:3.8

COPY email_lambda.py ${LAMBDA_TASK_ROOT}

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["email_lambda.lambda_handler"]