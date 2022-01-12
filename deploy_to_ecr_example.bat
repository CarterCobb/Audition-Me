@echo off

@REM Notes:
@REM *Replace all of the items in angle brackets and all caps character with your information.*
@REM e.g. `<AWS REGION>` becomes `us-west-1`
@REM 
@REM To run the script (easy way), find the file in the file explorer and double click it.

echo ***BUILD, TAG, and PUSH LAMBDA IMAGES TO ECR***
echo . 
echo ---------BUILD PHASE---------

echo .
echo Building auth image . . .
call cd auth
call docker build -t <IMAGE NAME>:<VERSION> -f Dockerfile
call cd ..
echo .

echo Building login image . . .
call cd login
call docker build -t <IMAGE NAME>:<VERSION> -f Dockerfile
call cd ..
echo .

echo Building performance image . . .
call cd performance
call docker build -t <IMAGE NAME>:<VERSION> -f Dockerfile
call cd ..
echo .

echo Building user image . . .
call cd user
call docker build -t <IMAGE NAME>:<VERSION> -f Dockerfile
call cd ..
echo .

echo ---------LOGIN PHASE---------
echo . 
call aws ecr get-login-password --region <AWS REGION> | docker login --username AWS --password-stdin <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com
echo .

echo ---------TAG PHASE---------

echo .
echo Applying tag to auth . . .
call docker tag <IMAGE NAME>:<VERSION> <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo Applying tag to login . . .
call docker tag <IMAGE NAME>:<VERSION> <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo Applying tag to performance . . .
call docker tag <IMAGE NAME>:<VERSION> <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo Applying tag to user . . .
call docker tag <IMAGE NAME>:<VERSION> <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo ---------PUSH PHASE---------

echo .
echo Puching auth to ECR . . .
call docker push <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo Puching login to ECR . . .
call docker push <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo Puching performance to ECR . . .
call docker push <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo Puching user to ECR . . .
call docker push <AWS ACCOUNT ID>.dkr.ecr.<AWS REGION>.amazonaws.com/<IMAGE NAME>:<VERSION>
echo .

echo ---------COMPLETED---------
pause