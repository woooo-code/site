import requests, boto3, json, urllib.request, os
from bs4 import BeautifulSoup

r = requests.get("https://unsplash.com/search/photos/portraits")
data = r.text
soup = BeautifulSoup(data, "lxml")

f = open('profile_images.txt', 'w')

num = 0

# connect to amazon s3
S3_BUCKET = os.environ.get('S3_BUCKET')
REGION = os.environ.get('REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

s3 = boto3.client('s3', "us-west-1", \
				aws_access_key_id=AWS_ACCESS_KEY_ID, \
				aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

for page in range(1, 26):
	url="https://unsplash.com/napi/search/photos?query=portraits&xp=&per_page=20&page=" + str(page)
	results = json.loads(requests.get(url).content.decode('utf-8'))
	for result in results['results']:
		url = result['urls']['raw']
		path = "app/static/img/seed_images/"
		filename = "seed-" + str(num) + ".jpg"
		urllib.request.urlretrieve(url, path + filename)
		s3.upload_file( path + filename , S3_BUCKET, filename, ExtraArgs={'ACL':'public-read', 'ContentType':'image/jpg'})
		f.write("https://" + REGION + ".amazonaws.com/" + S3_BUCKET + "/" + filename + "\n")
		num += 1

## reuploading compressed files
# for image in range(500):
# 	path = "app/static/img/seed_images/"
# 	filename = "seed-" + str(num) + ".jpg"
# 	s3.upload_file( path + filename , S3_BUCKET, filename, ExtraArgs={'ACL':'public-read', 'ContentType':'image/jpg'})
# 	num += 1