# Audition Me - An AWS Lambda Project

Built by Carter J. Cobb

## ⚠️ This project is under developmet

Current code will break and is not recommended to be run.

## Details

This project uses Python and Docker to build AWS lambda functions. Requirements this project satifies are as follows:

### Description

During this lab you will build a cloud hosted application to connect performers (actors, singers, comedians, etc.) with performances. This system will also allow casing directors to find performers for their productions.

### Business Requirements

- A performance has a title, director, casting director, list of live performance dates, a cast of available characters, and a venue.
  - For filmed/recorded productions the venue is the address of the studio.
  - For live performances the venue is the place at which the performance will take place on the performance dates.
  - For the purposes of this project, you may assume that all performance dates take place at the same venue (no tours).
- Directors, casting directors, performers, etc. all have names, email addresses, and phone numbers.
- Performers also have a list of performances in which they have participated in the past as well as a list (which can be empty) of performances in which they are currently participating.
- Users of the application are either performers seeking a role or directors/casting directors seeking talent.
- Each user must authenticate to the system and then will have access to only to the functionality appropriate for their role.
- Directors/Casting directors may:
  - Post a performance to the system. This allows performers to see/search for the performance and sign up to audition for it.
  - Delete a performance from the system.
  - Cast a performer, who has auditioned, in a performance owned by the director/casting director.
- Performers may:
  - Search performances
  - Sign up to audition for a performance
  - Receive notifications (via either email or text - developer's choice) of the status of their audition.
- Directors/Casing directors should receive an email whenever a performer signs up for an audition.
- Performers who are cast in a performance should receive email notification of their casting when the Director/Casting director updates the system to indicated they have been cast.
- Performers who have signed up for an audition should receive an email reminder of their audition at 7pm on the evening before the audition. You must consider that performers and auditions may not all be in the same time zones.

### Technical Requirements

- Your entire system, except for your user interface (the view) must reside in the AWS cloud.  Any exceptions to this rule must be approved in advance by the instructor.
- At least some of your functionality must exist in the form of AWS lambda functions [example](https://aws.amazon.com/lambda/).
- You may, if you choose, also use an EC2 instance to house some of your code, but you MUST remain in the free tier and incur no charges.
- At least some of your public API functionality must flow through the AWS API Gateway, but you MUST remain in the free tier and incur no charges [example](https://aws.amazon.com/api-gateway/pricing/).
- At least some of your data storage must you AWS DynamoDB.  However, you must remain in the free tier and incur no charges [example](https://aws.amazon.com/dynamodb/).
- Your authentication/authorization must be done using either AWS Cognito User pools or AWS lambda authorizer lambdas.
- All email notification sending should be done via a single service (lambda).
- Sending of audition reminder emails should use AWS SQS.  One message should be published for each audition reminder (may include multiple recipients).  A SQS consumer should retrieve the message and send the email.

### Requirements To Start

- Python installed [download link](https://www.python.org/downloads/)
- Docker insalled [download link](https://www.docker.com/products/docker-desktop)
- AWS CLI installed and configured [download & turtorial](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)

### Recommended But Not Required Items

- Postman installed [download link](https://www.postman.com/downloads/)

## Pre Run ⚠️

- Most of the python scripts will require environment variables. Due to the unfinished nature of the project, this stage cannot be accurately listed.

## Run ⚠️

- Under development but the scripts can still be ran and tested

## Test ⚠️

- During developmet, python scripts will have simple tests noted with `# TESTING`

## Additional Details

This was built as an assignment for a college class at Neumont College of Computer Science. Please do not use any part of this project in any way that would be considered plagiarism.
