# Serverless Image Processing Pipeline
## A Capstone Project using AWS S3, Lambda, Step Functions, and API Gateway

### Overview

This repository contains my implementation of the Serverless Image Processing Capstone Project, which required building an automated pipeline to resize images using fully managed AWS services.
According to the assignment description, the application must:

* Accept original images uploaded to an S3 bucket

* Trigger a Lambda function that resizes the image

* Store the resized output in a second S3 bucket

* Orchestrate the workflow with Step Functions (including a Choice, Success, and Fail state)

* Provide an API Gateway endpoint that externally triggers the state machine

* This README contains instructions to deploy, test, and verify the full pipeline.

### High-Level Architecture
```

                         +-----------------------------+
                         |         API Gateway         |
                         |     POST /process-image     |
                         +--------------+--------------+
                                        |
                                        v
                           +---------------------------+
                           |      Step Functions       |
                           |  ResizeImageStateMachine  |
                           | Choice → Task → Success   |
                           +--------------+------------+
                                          |
                                          v
                             +-------------------------+
                             |     Lambda Function     |
                             |  ImageResizeFunction    |
                             +------------+------------+
                                          |
         +--------------------------------+--------------------------------+
         |                                                                 |
         v                                                                 v
+---------------------------+                                 +----------------------------+
|       S3 Input Bucket     |                                 |       S3 Output Bucket     |
|  chels-original-images    |                                 |   chels-resized-images     |
|          /input/          |                                 |          /output/          |
+---------------------------+                                 +----------------------------+

                         +-----------------------------------+
                         |         CloudWatch Logs           |
                         |  Lambda Logs + StepFn Logs        |
                         +-----------------------------------+
```

### Prerequisites

You will need:

* An AWS Account

* Pillow Layer:

    Tip: Use Cloudshell to download a Pillow Layer

    Ensure to use the SAME python runtime as your Lambda Function (Here I used Python 3.9) as Pillow (Python) is deployed via a Lambda Layer

* Two Amazon S3 buckets:

    Example:

    * chels-original-images → contains an input/ folder

    * chels-resized-images → contains an output/ folder

* A Lambda-compatible image processing library:

* IAM Permissions:

    Lambda → S3 read/write

* Step Functions → Lambda invoke

* API Gateway → Step Functions StartExecution

* AWS CLI or Console

* Postman (for API testing)

### Project Components

1. S3 Buckets

S3 bucket for original images with a folder inside called input

    chels-original-images/input/ — receives original images

Inside this input folder is where you will place your test .jpg image

    chels-original-images/input/test.jpg

S3 bucket for resized images with a folder inside called output

    chels-resized-images/output/ — stores resized images


2. Lambda Function

* Triggered when a new image is received or via Step Functions

* Uses Pillow from a Lambda Layer

* Resizes images to thumbnail size

* Saves resized output to second S3 bucket

3. Step Funtions Workflow

* Task state → Invoke Lambda

* Choice state → Check if resize succeeded

* Success state → Image processed

* Fail state → Error path

4. API Gateway - Step Functions Integration

* This is implemented using an AWS Service integration (Step Functions StartExecution)

*  Final Invoke URL:

*  https://s8vwce6r90.execute-api.us-east-1.amazonaws.com/prod/process-image

### Deployement Instructions

Step 1 - Create S3 Buckets

![S3 Buckets](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/S3BucketDashboard.png?raw=true)

Create two S3 buckets, one for your original image and another for the resized image. Since your original image will be the input we will place an input folder inside that bucket and our test .jpg image inside that folder.

![S3 Bucket 1 Input](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/S3OriginalImageInput.png?raw=true)

![S3 Bucket 1 with test image](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/S3OriginalImageInputTestImage.png?raw=true)

* Bucket 1: chels-original-images/input/ -> chels-original-images/input/test.jpg

The second bucket will be for you resized image and we will place an output folder inside that bucket for the results.

![S3 Bucket 2 Output](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/S3ResizedImageOutput.png?raw=true)

* Bucket 2: chels-resized-images/output/


Step 2 - Craete Lambda Function

1. Runtime: Python 3.9 (ensure it matches Pillow layer)

2. Upload image-processing code

3. Add Lambda Layer containing Pillow

![Lambda Function](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/ImageResizeFunction.png?raw=true)

![Layer](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/Layers.png?raw=true)

4. Assign IAM Role:

![Lambda IAM Role](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/LambdaExecutionRole.png?raw=true)

![Lambda IAM Role Policy](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/LambdaExecutionRoleS3Permissions.png?raw=true)

*  s3:GetObject from original bucket

*  s3:PutObject to resized bucket


Step 3 - Build Step Functions State Machine

* Include: Task → Choice → Success/Fail

![State Machine](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/StatemachineVisualWorkFlow.png?raw=true)

* Use your Lambda ARN in the Task state.

Example:

* arn:aws:states:us-east-1:273354628455:stateMachine:ResizeImageStateMachine


Step 4 - Create API Gateway Endpoint

1. REST API → Create Resource /process-image

2. Create POST method

3. Integration Type: AWS Service

4. Service: StepFunctions

5. Action: StartExecution

6. Credentials: Execution role

![Gateway Endpoint](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/ResourcesPage.png?raw=true)

7. Add a Mapping Template:

```json

{
  "input": "$util.escapeJavaScript($input.json('$'))",
  "stateMachineArn": "YOUR_STATE_MACHINE_ARN"
}

```
![Mapping Template](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/IntegrationRequestMappingTemplate.png?raw=true)

8. Deploy Stage: prod

Step 5 - Test the Pipeline

Use the API Gateway Test Console

test:
```json
{}
```

You should expect:

{"executionArn":"...", "startDate":...}

Use HTTP Post on Postman

Paste the invoke URL

![Stage Screen Invoke URL](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/DeployedStagePage.png?raw=true)

Example:

POST -> https://s8vwce6r90.execute-api.us-east-1.amazonaws.com/prod/process-image -> Body -> Raw -> json

test:
```json
{}
```
Expected Result:

```json
{
    "executionArn": "arn:aws:states:us-east-1:273354628455:execution:ResizeImageStateMachine:2bd556f4-4008-4e0b-bc6b-83f5192e08e4",
    "startDate": 1.763664454447E9
}
```
![Postman Result](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/PostmanTestSuccess.png?raw=true)

Finally:

1. Upload an image to chels-original-images/input/

![Original](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/OriginalImage.png?raw=true)

2. Verify results in chels-resized-images/output/

![Results](https://github.com/chlsk/CCMP200CapstoneProject/blob/main/images/ResizedImage.png?raw=true)

If the resized image is there CONGRATS you've made a serverless image processing pipeline!!

### Documentation and References

[Building a Serverless Image Processor with Python and AWS Lambda](https://heuristictechnopark.com/blog/building-serverless-image-processing-python-aws-lambda)

[AWS Lambda Layers (Python)](https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html)

[AWS API Gateway Step Functions Integration Guide](https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-api-gateway.html)