import feedparser
import db_ops
import time
import hashlib

class FeedFetcher:
    def __init__(self, feed_url):
        self.feedurl = feed_url
        self.result = feedparser.parse(feed_url)
        self.category_name = "unknow"
        self.category_id = 2
        self.feedid = 0

    def parse_items(self):
        query_str = "select itemid from items where title=%s"
        for entry in self.result.entries:

            weburl = self.result.feed.id
            title = entry.title
            print title
            url = entry.link
            snippet = entry.get('summary')
            content = entry.get('content')
            publish_date = to_time(entry.get('published_parsed', entry.get('updated_parsed')))
            guid = hashlib.md5((title + url).encode('utf-8')).hexdigest()

            result = db_ops.db_exec("select feedid from feeds where sourceurl='%s'" % weburl)
            if(result):
                self.feedid = result[0][0]
            
            result = db_ops.db_exec("select itemid from items where title='%s'" % title)
            if(not result):
                value = (self.feedid, url, publish_date, title, snippet, content[0]['value'], False, False, guid)
                result = db_ops.db_insert("insert into items " + 
                        "(feedid, url, pubdate, title, snippet, content, readed, star, guid) " + 
                        "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", value)
                print result
            


def to_time(time_tuple):
    return time.strftime('%Y-%m-%d %H:%M:%S', time_tuple)


if __name__ == "__main__":
    db_ops.db_init()
    fetch = FeedFetcher("http://blog.devtang.com/atom.xml")
    fetch.parse_items()
