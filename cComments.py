import time
import json
import codecs
from socket import timeout, error as SocketError
from ssl import SSLError
from urllib2 import URLError
from httplib import HTTPException
from instagram_private_api import ClientError

import cLogger


def get_live(api, broadcast, record, first_comment_created_at=0):
		comments_collected = comments

		before_count = len(comments_collected)
		try:
			comments_res = api.broadcast_comments(
				broadcast['id'], last_comment_ts=first_comment_created_at)
			comments = comments_res.get('comments', [])
			first_comment_created_at = (
				comments[0]['created_at_utc'] if comments else int(time.time() - 5))

			after_count = len(comments_collected)
			if after_count > before_count:
				# save intermediately to avoid losing comments due to unexpected errors
				broadcast = broadcast.copy()
				broadcast.pop('segments', None)     # save space
				broadcast['comments'] = comments_collected
				with open((record + "_" + str(broadcast['id']) + "_" + str(int(t)) + '.json'), 'w') as outfile:
					json.dump(broadcast, outfile, indent=2)
			comments = comments_collected

		except (SSLError, timeout, URLError, HTTPException, SocketError) as e:
			cLogger.log("Error", "RED")
			# Probably transient network error, ignore and continue
			# self.logger.warning('Comment collection error: %s' % e)
		except ClientError as e:
			if e.code == 500:
				cLogger.log("500" "RED")
				# self.logger.warning('Comment collection ClientError: %d %s' % (e.code, e.error_response))
			elif e.code == 400 and not e.msg:   # 400 error fail but no error message
				cLogger.log("400 no msg" "RED")
				# self.logger.warning('Comment collection ClientError: %d %s' % (e.code, e.error_response))
			else:
				raise e
		finally:
			time.sleep(4)
		return first_comment_created_at