# aws-practice

## Lambda

### Lambda Features

#### Ephemeral Storage

No access to a filesystem or memory persistence (e.g. on-instance Redis)
so you cannot store data or the `result` of an operation *locally*.

#### Use an AWS Datastore Service

The lack of *local* persistence on Lambda is resolved by having
low-latency access to AWS S3 and *other* AWS Datastores e.g:
[ElastiCache](https://aws.amazon.com/elasticache/) (in-memory cache),
[DynamoDB](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html) (NoSQL ssd-based database),
[RDS](https://aws.amazon.com/rds/) (*relational database*),
however there's an
important (and potentially *expensive*) catch: PUT/POST/GET requests to all
AWS data stores are **NOT** Free! While per-run costs on Lambda are tiny, if you GET and PUT
something to S3 on each execution cycle you could rack up the bill!


### Creating simple Lambda function in Python

#### Unique Identifire

##### Prerequisites

Install awscli for command line AWS
    brew install awscli

Install jq for command line javascript parsing
    brew install jq
    
