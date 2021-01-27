# Reddit-listener.py
#
# A script to listen to comments or submissions on Reddit and export them
# as JSON objects and save them to S3 using filenames that are easily streamed.
#
# Author: Rusty Conover <rusty@conover.me>
# Copyright 2021 Rusty Conover
#
# MIT Licensed.
#
import praw
import json
import uuid
import time
import boto3
import zlib
import datetime
import argparse

parser = argparse.ArgumentParser(description='Listen to Reddit and save the comments or submissions to S3')
parser.add_argument('--subreddit', type=str,
                    required=True,
                    help='The subreddit to listen to')
parser.add_argument('--flush-interval', type=int, default=60*5,
                    help='The maximum number of seconds between uploads to S3')
parser.add_argument('--flush-size', type=int, default=1024*1024*4,
                    help='The maximum number of bytes before triggering a flush to S3')
parser.add_argument('--s3-bucket', type=str,
                    required=True,
                    help='The name of the S3 bucket where to store the captured data')
parser.add_argument('--client-id', type=str,
                    required=True,
                    help='The Reddit API client id')
parser.add_argument('--client-secret', type=str,
                    required=True,
                    help='The Reddit API client secret')
parser.add_argument('--mode', choices=["comments", "submissions"],
                    help='The type of post to save')
args = parser.parse_args()

print(args)
# Fill these in from the environment.
reddit = praw.Reddit(
    client_id=args.client_id,
    client_secret=args.client_secret,
     user_agent="reddit-recorder/1.0"
)

# Either comments or submissions
mode = "comments"

def get_s3_key():
    global args
    return "{}-{}-{}-{}".format(args.subreddit, args.mode, datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S'), uuid.uuid4())

time_of_last_flush = time.time()
comments = []
length = 0

def write_to_s3_if_needed():
    global comments, time_of_last_flush, length
    if length > args.flush_size or (time.time() - time_of_last_flush > args.flush_interval):
        big = zlib.compress(b"\n".join(comments))
        time_of_last_flush = time.time()

        s3_client = boto3.client('s3')
        key_name = "{}.gz".format(get_s3_key())
        s3_client.put_object(
            Key=key_name,
            Bucket=args.s3_bucket,
            Body=big,
            ContentEncoding="gzip",
        )
        print("Did upload of: ", key_name)
        comments = []
        length = 0

if args.mode == 'comments':
    for comment in reddit.subreddit(args.subreddit).stream.comments():
        serialized = json.dumps({
            "type": "comment",
            "id": comment.id,
            "created_utc": comment.created_utc,
            "link_id": comment.link_id,
            "parent_id": comment.parent_id,
            'author': comment.author.id,
            'author_is_mod': comment.author.is_mod,
            'author_created_utc': comment.author.created_utc,
            "score": comment.score,
            "body": comment.body
        }, ensure_ascii=False).encode('utf8')
        length += len(serialized)
        comments.append(serialized)
        print(length)
        write_to_s3_if_needed()
elif args.mode == 'submissions':
    for submission in reddit.subreddit(args.subreddit).stream.submissions():
        serialized = json.dumps({
            "type": "submission",
            "id": submission.id,
            'title': submission.title,
            'url': submission.url,
            'selftext': submission.selftext,
            'selftext_html': submission.selftext_html,
            "created_utc": submission.created_utc,
            'author': submission.author.id,
            'author_is_mod': submission.author.is_mod,
            'author_created_utc': submission.author.created_utc,
            "score": submission.score,
        }, ensure_ascii=False).encode('utf8')
        length += len(serialized)
        comments.append(serialized)
        print(length)
        write_to_s3_if_needed()
else:
    print("Unknown mode for processing (choose comments or submissions)")


