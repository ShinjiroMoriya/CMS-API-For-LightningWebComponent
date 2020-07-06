import os
import cloudinary
from os.path import join, dirname
from cloudinary import uploader
from cloudinary.api import delete_resources
from urllib.parse import urlparse
from quip import QuipClient, get_html
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import bleach

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DOCS_FLAG = os.environ.get('DOCS_FLAG') == 'True'

config = {
    'title': "CSG API for LWC",
    'redoc_url': '/'
}

if DOCS_FLAG is False:
    config.update({
        'docs_url': None,
        'redoc_url': None,
    })

app = FastAPI(**config)

salesforce_url = os.environ.get('SALESFORCE_URL')
if salesforce_url is not None:
    origins = salesforce_url.split(',')
else:
    origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class Image(BaseModel):
    public_id: str


cloudinary_parse_url = urlparse(os.environ.get('CLOUDINARY_URL'))

cloudinary.config(
    cloud_name=cloudinary_parse_url.hostname,
    api_key=cloudinary_parse_url.username,
    api_secret=cloudinary_parse_url.password,
)


@app.post('/api/upload')
def api_upload(upload_file: UploadFile = File(...)):
    res = uploader.upload(file=upload_file.file)
    res.update({
        'cloudinary_url': f'https://res.cloudinary.com/{cloudinary_parse_url.hostname}'
    })
    return res


@app.post('/api/delete')
def api_delete(public_id: str = Form(...)):
    res = delete_resources(public_ids=[public_id])
    return res


@app.get('/api/quip')
def api_quip(quip_id: str):
    quip = QuipClient()
    thread = quip.get_thread(quip_id)
    html = get_html(thread)
    return {
        'html': html,
        'word': bleach.clean(html, strip=True, tags=['*']).replace('\n', '')
    }
