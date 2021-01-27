# Reddit Listener

Listen to a subreddit's comments and submissions, serialize them to JSON
and write them to S3 periodically based on either a time or size limit.

## Requirements

Python 3, a Reddit approved API key and secret.

## Usage

```
usage: listener.py [-h] --subreddit SUBREDDIT [--flush-interval FLUSH_INTERVAL] [--flush-size FLUSH_SIZE] --s3-bucket S3_BUCKET --client-id CLIENT_ID --client-secret CLIENT_SECRET
                   [--mode {comments,submissions}]

Listen to Reddit and save the comments or submissions to S3

optional arguments:
  -h, --help            show this help message and exit
  --subreddit SUBREDDIT
                        The subreddit to listen to
  --flush-interval FLUSH_INTERVAL
                        The maximum number of seconds between uploads to S3
  --flush-size FLUSH_SIZE
                        The maximum number of bytes before triggering a flush to S3
  --s3-bucket S3_BUCKET
                        The name of the S3 bucket where to store the captured data
  --client-id CLIENT_ID
                        The Reddit API client id
  --client-secret CLIENT_SECRET
                        The Reddit API client secret
  --mode {comments,submissions}
                        The type of post to save
```