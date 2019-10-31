import json
import boto3
import io
import zipfile
import mimetypes


def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic(
        'arn:aws:sns:us-east-1:996890886400:deployPortfolioTopic')

    s3 = boto3.resource('s3')

    portfolio_bucket = s3.Bucket('portfolio.joshneves.info')
    build_bucket = s3.Bucket('portfoliobuild.joshneves.info')

    portfolio_zip = io.BytesIO()
    build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

    with zipfile.ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            portfolio_bucket.upload_fileobj(
                obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

    return {
        'statusCode': 200,
        'body': json.dumps(topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed Successfully."))
    }
