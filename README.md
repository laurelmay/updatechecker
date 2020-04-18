# updatechecker

Builds AWS infrastructure to notify when new versions of jGRASP or Eclipse's
Java IDE get release.

The function runs daily using a CloudWatch Events timer. It will store the last
known data in an S3 bucket that is created. This is easier than using a real
database. Since it runs only once per day by default, S3's eventual consistency
is likely not an issue.

Subscriptions must be added manually to the topic as Terraform does not support
adding email subscriptions.