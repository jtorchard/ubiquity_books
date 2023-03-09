import csv
import os
import uuid
from datetime import datetime
from io import TextIOWrapper
import re

from flask import Blueprint, flash, redirect, render_template, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import boto3
import requests

from books.models import Book
from books.exceptions import S3Error, CSVValidationError
from . import db

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'txt', 'csv'}
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
AWS_ID = os.getenv('AWS_ID')
AWS_KEY = os.getenv('AWS_KEY')


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


def valid_isbn_10(isbn_10):
    return bool(re.match(r'^\d{10}$', isbn_10))


def upload_to_s3(file_to_upload, filename):
    try:
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=AWS_ID,
            aws_secret_access_key=AWS_KEY,
        )

        bucket = s3_resource.Bucket(S3_BUCKET)

        bucket.Object(filename).put(Body=file_to_upload.read())
    except ClientError:
        raise S3Error('Error uploading file to S3')


def notify_endpoint(s3_url):
    response = requests.post(
        'https://postman-echo.com/post',
        data={
            's3_url': s3_url,
        },
    )
    if not response.ok:
        print('Notify endpoint failed. Handle errors')


def handel_csv(file):
    filename = secure_filename(file.filename)
    s3_filename = generate_unique_name(filename)
    csv_file = TextIOWrapper(file, encoding='utf-8')
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    # TODO Sanitise/validate row data in separate function
    for row in csv_reader:
        if not valid_isbn_10(row['uuid']):
            raise CSVValidationError('Field UUID is not valid ISBN 10')
        # Not dealing with multiple authors or other complexities
        # with titles and publisher names due to time constraints
        book = Book(title=row['title'],
                    author=row['author'],
                    date_published=datetime.strptime(row['publish_date'], '%d-%m-%Y'),
                    uuid=row['uuid'],
                    publisher_name=row['publisher_name'],
                    user_id=current_user.id,
                    s3_name=s3_filename,
                    s3_url=f'https://{S3_BUCKET}.{S3_REGION}/{s3_filename}',
                    )
        # TODO could batch/bulk insert here
        db.session.add(book)
        db.session.commit()

    file.seek(0)
    try:
        upload_to_s3(file, s3_filename)
    except S3Error:
        raise

    notify_endpoint(s3_filename)


def generate_unique_name(filename):
    name, ext = filename.split('.')
    return f'{name}_{uuid.uuid4().hex}.{ext}'


@main.route('/')
def index():
    return render_template('index.html')


@login_required
@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            try:
                handel_csv(file)
            except (CSVValidationError, S3Error) as e:
                flash(str(e))
                return redirect(request.url)
    books = Book.query.filter(Book.user_id == current_user.id).all()
    return render_template('profile.html', email=current_user.email, data=books)
