# Data Engineering take home assessment.

Provided Target table's schema is:
* user_id : varchar(128)
* device_type : varchar(32)
* masked_ip : varchar(256)
* maked_device_id : varchar(256)
* locale : varchar(32)
* app_version : integer (read from SQS as a version i.e. 2.3.0, 0.2.6 or 0.96 so just take first num)  
* create_date : date
    
## **Steps to Run the code**
1. Ensure you have Docker running local instances of PostgreSQL and AWS SQS by using the necessary Docker images. [PostgreSQL](https://hub.docker.com/r/fetchdocker/data-takehome-postgres?) and [AWS SQS](https://hub.docker.com/r/fetchdocker/data-takehome-localstack?) 
2. You will need Python, AWS SDK for Python boto3, and PostgreSQL adapter psycopg2.
3. Start the containers by running `docker-compose up` and allow some time for them to initialize. Then execute `python3 hashedPII.py` in the terminal.
4. Wait for atleast 20 seconds to make sure all AWS SQS messages are processed.
5. After execution, the PostgreSQL database should have masked values for device_id and ip while other fields remain unchanged from AWS SQS data.
6. The terminal output will display a query of the PostgreSQL database, showing the schema at the top with each row in parentheses.

## **Questions to be answered**

1. How would you deploy this application to production?
   * Monitoring and Logging: Implement comprehensive monitoring and logging using AWS CloudWatch for application performance and CloudTrail for tracking API calls and changes. This ensures you can quickly detect and respond to issues.  
   * Infrastructure as Code (IaC): Use Terraform or AWS CloudFormation to define and manage the infrastructure. This ensures reproducibility, version control, and easy updates to the infrastructure.  
   * Continuous Integration/Continuous Deployment (CI/CD): Set up a CI/CD pipeline using tools like Jenkins, GitHub Actions, or AWS CodePipeline. This will automate testing, building, and deployment of the application, ensuring quick and reliable updates.  

2. What other components would you want to add to make this production ready?
   * Unit and Integration Testing: Develop robust unit and integration tests to ensure code quality and reliability. Utilize testing frameworks like pytest for Python.
   * Secrets Management: Use AWS Secrets Manager or AWS Parameter Store to securely manage and access sensitive information like database credentials and API keys.
   * Security Enhancements: Ensure data encryption both in transit and at rest. Apply the principle of least privilege using IAM roles and policies to restrict access to sensitive data.  
   * Data Validation and Quality Checks: Implement data validation checks on the incoming SQS messages to ensure data integrity before processing.  

3. How can this application scale with a growing dataset?
   * Auto-Scaling: Implement auto-scaling for both the application servers and the database using AWS Auto Scaling groups for EC2 instances and read replicas for RDS.  
   * Load Balancing: Use AWS Elastic Load Balancer to distribute incoming traffic across multiple instances, ensuring no single instance is overwhelmed.  
   * Message Processing Parallelism: Increase the number of consumers processing messages from the SQS queue to handle higher message volumes concurrently.  
   * Database Optimization: Optimize the database by using indexing, partitioning, and potentially sharding to improve performance and scalability.  

4. How can PII be recovered later on?
   * Encrypted Storage: Store the original PII in an encrypted database using AWS KMS to manage encryption keys. Only authorized users can decrypt and access the PII.
   * Hashing with Salt: Use salted hashing for masking PII and store the salt securely. This allows reversible hashing when needed.
   * Access Control: Implement strict access controls and auditing using AWS IAM to ensure only authorized personnel can access or decrypt the PII.  
   * Secure Backup: Regularly backup the encrypted PII data and store it in a secure, access-controlled environment, ensuring recoverability in case of data loss.

5. What are the assumptions you made?
   * Data Quality from SQS: Assumed that the data received from AWS SQS is complete, well-formed, and does not contain errors or inconsistencies.
   * Stable Infrastructure: Assumed that the Docker and localstack infrastructure, along with PostgreSQL, will perform reliably under expected load conditions.
   * Reasonable Data Volume: Assumed that the incoming data volume and message frequency are within manageable limits for the chosen architecture.  
   * Security Compliance: Assumed that the implemented security measures, including encryption and access controls, meet industry standards and compliance requirements.

