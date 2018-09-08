import boto3
from botocore.client import Config
import StringIO
import zipfile

def lambda_handler(event, context):
    
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:344267670530:DeployPortfolioTopic')
    
    location = {
        "bucketName": 'portfoliobuild.lawrencepdavisjr.com',
        "objectKey": 'portfoliobuild.zip'
    }
    try: 
        job = event.get("CodePipeline.job")
        
        if job: 
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild": 
                    location = artifact["location"]["s3Location"]
                    
                    
        print "Building portfolio from "  + str(location)

        s3 = boto3.resource('s3')
        
        portfolio_bucket = s3.Bucket('portfolio.lawrencepdavisjr.com')
        build_bucket = s3.Bucket(location["bucketName"])
        
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm) 
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        
        print "Job Done!"
        topic.publish(Subject="Portfolio Deployed!", Message="Portfolio Deployed Sucessfully!")
        if job: 
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    
    except: 
        topic.publish(Subject="Portfolio Failed Deployment!", Message="The Portfolio Deployment Failed!")
        raise
  
    return 'Hello From Lambda'
    
    
