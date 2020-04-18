# updatechecker

Builds AWS infrastructure to notify when new versions of various tools get
released. Software currently supported includes:

 - Eclipse IDE for Java Developers
 - jGRASP
 - Finch Python

The function runs daily using a CloudWatch Events timer. It will store the last
known data in an S3 bucket that is created. This is easier than using a real
database. Since it runs only once per day by default, S3's eventual consistency
is likely not an issue.

Subscriptions must be added manually to the topic as Terraform does not support
adding email subscriptions.

## Deploying

Create a file called `env.tfvars` that assigns values for each variable found in
`variables.tf`.

```
cd updatechecker
pip install -t ./ beautifulsoup4 requests click
zip -r9 ../lambda_function_payload.zip .
cd ..
terraform plan -var-file=env.tfvars
terraform apply -var-file=env.tfvars
```
