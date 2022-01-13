FROM public.ecr.aws/lambda/python:3.8

COPY email.py ${LAMBDA_TASK_ROOT}

CMD ["email.lambda_handler"]