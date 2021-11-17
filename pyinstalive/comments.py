import time
import codecs
from . import helpers
from . import logger
from . import globals
from . import api

class Comments:
    def __init__(self):
        self.comments = []
        self.comments_last_ts = 0

    def retrieve_comments(self):
        current_comments = self.comments
        before_count = len(self.comments)
        comments_response = api.get_comments()
        new_comments = comments_response.get("comments", [])
        for i, comment in enumerate(new_comments):
            elapsed = int(time.time()) - int(globals.download.timestamp)
            new_comments[i].update({"total_elapsed": elapsed})
        self.comments_last_ts = (new_comments[0]['created_at_utc'] if new_comments else int(time.time()))
        current_comments.extend(new_comments)
        after_count = len(self.comments)
        if after_count > before_count:
            globals.download.livestream_object['comments'] = current_comments
        self.comments = current_comments

    def generate_log(self):
        try:
            if self.comments:
                logger.info("Saving {} comment{} to text file.".format(len(self.comments), "s" if len(self.comments) > 1 else ""))
            else:
                logger.warn("There are no available comments to save.")
                return
            comments_timeline = {}
            for c in self.comments:
                if 'offset' in c:
                    for k in list(c.get('comment')):
                        c[k] = c.get('comment', {}).get(k)
                    c['created_at_utc'] = c.get('offset')
                created_at_utc = str(2 * (c.get('created_at_utc') // 2))
                comment_list = comments_timeline.get(created_at_utc) or []
                comment_list.append(c)
                comments_timeline[created_at_utc] = comment_list

            if comments_timeline:
                comment_errors = 0
                total_comments = 0
                timestamps = sorted(list(comments_timeline))
                comments = []
                for tc in timestamps:
                    t = comments_timeline[tc]

                    comments_log = ''
                    for c in t:
                        try:
                            comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(c.get("total_elapsed"))), '{}: {}'.format(c.get('user', {}).get('username'),c.get('text')))
                        except Exception:
                            comment_errors += 1
                            try:
                                comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(c.get("total_elapsed"))), '{}: {}'.format(c.get('user', {}).get('username'),c.get('text').encode('ascii', 'ignore')))
                            except Exception:
                                pass
                        total_comments += 1
                    comments.append(comments_log)

                with codecs.open(globals.download.data_comments_path, 'w', 'utf-8-sig') as log_outfile:
                    log_outfile.write(''.join(comments))
                if len(self.comments) == 1:
                    logger.info("Successfully saved 1 comment to text file.")
                elif len(self.comments) > 1:
                    if comment_errors:
                        logger.warn("Successfully saved {:s} comments to text file with {:s} errors.".format(str(total_comments), str(comment_errors)))
                    else:
                        logger.info("Successfully saved {:s} comments to text file.".format(str(total_comments)))
        except Exception as e:
            logger.error("Could not save comments: {:s}".format(str(e)))