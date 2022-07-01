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

load_dotenv()


app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATES_AUTO_RELOAD'] = True
files=r'D:\chronicles\files'
app.config['UPLOAD_FOLDER']=files
ALLOWED_EXTENSIONS = {'pdf'}
laparams = pdfminer.layout.LAParams()
setattr(laparams, 'all_texts', True)
AWSAccessKeyId=os.getenv("AWSAccessKeyId")
AWSSecretKey=os.getenv("AWSSecretKey")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET', 'POST'])
def home():
    shutil.rmtree(files)
    os.makedirs(files)
    if request.method=='POST':
        f=request.files['myfile']
        if f.filename=='':
            flash("Please select the file",category='error')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename=secure_filename(f.filename)
            full_filename=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            f.save(full_filename)
            if not read_pdf(full_filename):
                return "Dir is empty"

            return 'file uploaded successfully'
        else:
            flash("Please select only pdf file",category='error')
            return redirect(request.url) 
    return render_template("home_page.html")

def read_pdf(full_filename):
    if len(files)==0:
        return False
    else:
        buff_file=open(os.path.join(app.config['UPLOAD_FOLDER'],"buff_file.txt"),"w")
        for page in extract_text_by_page(full_filename):
            buff_file.write(page)
        buff_file.close()
        upload_to_s3()
        return True



def extract_text_by_page(pdf_path): 

    with open(pdf_path, 'rb') as fh: 
        
        for page in PDFPage.get_pages(fh, 
                                    caching=True, 
                                    check_extractable=True): 
            
            resource_manager = PDFResourceManager() 
            fake_file_handle = io.StringIO() 
            
            converter = TextConverter(resource_manager, 
                                    fake_file_handle) 
            
            page_interpreter = PDFPageInterpreter(resource_manager, 
                                                converter) 
            
            page_interpreter.process_page(page) 
            text = fake_file_handle.getvalue() 
            
            yield text 
            
            # close open handles 
            converter.close() 
            fake_file_handle.close() 


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
        s3_client.upload_file(os.path.join(app.config['UPLOAD_FOLDER'],"buff_file.txt"), 'keyrank-bucket', 'buff_file')
        print("Upload Successful")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
        


if __name__ == '__main__':
    app.run(debug = True)

