from flask import Flask, flash,render_template,request,redirect
from pathy import Bucket
from spacy import load
from werkzeug.utils import secure_filename
import os 
import shutil
import io 
import pdfminer
from pdfminer.converter import TextConverter 
from pdfminer.pdfinterp import PDFPageInterpreter 
from pdfminer.pdfinterp import PDFResourceManager 
from pdfminer.pdfpage import PDFPage 
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os 
import json 

load_dotenv()


app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATES_AUTO_RELOAD'] = True
files=r'D:\chronicles\files'
app.config['UPLOAD_FOLDER']=files

AWSAccessKeyId=os.getenv("AWSAccessKeyId")
AWSSecretKey=os.getenv("AWSSecretKey")


@app.route('/',methods=['GET', 'POST'])
def home():
    shutil.rmtree(files)
    os.makedirs(files)
    if request.method=='POST':
        text=request.form['textarea']
        print(text)
        if text=='':
            flash("Please enter the text",category='error')
            return redirect(request.url)
        else:
            dicts={
                "body":text
            }
            json_object = json.dumps(dicts, indent = 4)
            with open(os.path.join(app.config['UPLOAD_FOLDER'],"buff_file.json"),"w") as outfile:
                outfile.write(json_object)
            upload_to_s3()
            return 'Successfull'           
    return render_template("home_page.html") 



def upload_to_s3():
    s3_client = boto3.client('s3', aws_access_key_id=AWSAccessKeyId,
                      aws_secret_access_key=AWSSecretKey)
    s3_resource=boto3.resource('s3', aws_access_key_id=AWSAccessKeyId,
                      aws_secret_access_key=AWSSecretKey)
    
    try:
        # code to delete s3 objects
        bucket=s3_resource.Bucket('keyrank-bucket')
        bucket.objects.delete()

        #code to upload a file to s3 object
        s3_client.upload_file(os.path.join(app.config['UPLOAD_FOLDER'],"buff_file.json"), 'keyrank-bucket', 'buff_file.json')
        print("Upload Successful")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
        


if __name__ == '__main__':
    app.run(debug = True)

