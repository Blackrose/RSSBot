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

            #print entry
            title = entry.title
            print title
            url = entry.link
            snippet = entry.get('summary', entry.get('description'))
            content = entry.get('content', entry.get('description'))
            publish_date = to_time(entry.get('published_parsed', entry.get('updated_parsed')))
            guid = hashlib.md5((title + url).encode('utf-8')).hexdigest()
            
            if(isinstance(content, list)):
                content = content[0]['value']
            if(isinstance(snippet, list)):
                snippet = snippet[0]['value']

            result = db_ops.db_exec("select feedid from feeds where feedurl='%s'" % self.feedurl)
            if(result):
                print "found the feedid %d" % result[0][0]
                self.feedid = result[0][0]
            else:
                print "This is new feedurl, need add to feeds table"
           
            print "select itemid from items where title=%s" % title
            result = db_ops.db_exec("select itemid from items where url='%s'" % url)
            print result
            if(len(result) == 0):
                value = (self.feedid, url, publish_date, title, snippet, content, False, False, guid)
                result = db_ops.db_insert("insert into items " + 
                        "(feedid, url, pubdate, title, snippet, content, readed, star, guid) " + 
                        "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", value)
                print "adding to sqlite"
            else:
                print "the article has already added!"


def to_time(time_tuple):
    return time.strftime('%Y-%m-%d %H:%M:%S', time_tuple)


if __name__ == "__main__":
    db_ops.db_init()
    feed_urls = db_ops.db_exec("select feedurl from feeds")
    for url in feed_urls:
        print url
        #fetch = FeedFetcher("http://www.36kr.com/feed")
        fetch = FeedFetcher(url[0])
        fetch.parse_items()
