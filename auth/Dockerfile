FROM public.ecr.aws/lambda/python:3.8

COPY auth.py ${LAMBDA_TASK_ROOT}

CMD ["auth.lambda_handler"]