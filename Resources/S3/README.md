
# Project Description:

1. A user uploads an object to the source bucket in Amazon S3 (object-created event).

2. Amazon S3 detects the object-created event.

3. Amazon S3 publishes the s3:ObjectCreated:* event to AWS Lambda by invoking the Lambda function and passing event data as a function parameter.

4. AWS Lambda executes the Lambda function by assuming the execution role that you specified at the time you created the Lambda function.

5. From the event data it receives, the Lambda function knows the source bucket name and object key name. The Lambda function reads the object and creates a thumbnail using graphics libraries, and saves it to the target bucket.

## Step 1

Create two buckets (source and sourceresized bucket) and upload a sample .jpg object (Test.jpg) in the source bucket.

  - The target bucket name must be source followed by resized, where source is the name of the bucket you want to use for the source. For example, mybucket and mybucketresized.
  - In the source bucket, upload a .jpg object, Test.jpg
  

