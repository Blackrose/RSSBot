# -*- coding: utf-8 -*-
import urllib2
from sgmllib import SGMLParser

import db_ops

class ParserWeb(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.feedurl = ""
        self.feedname = ""
        self.is_title = False
    def start_link(self, attrs):
        if attrs[0][1] == 'alternate' and attrs[1][1] == 'application/rss+xml':
                self.feedurl = attrs[3][1]
    def start_title(self, attrs):
        self.is_title = True
    def handle_data(self, data):
        if self.is_title:
            self.feedname = data
    def end_title(self):
        self.is_title = False
    def get_data(self):
        return self.feedname, self.feedurl

def parser_url(weburl, category_id):
    content = urllib2.urlopen(weburl).read()

    parser = ParserWeb()
    parser.feed(content)
    parser_data = parser.get_data()

    value = (category_id, parser_data[0], weburl, parser_data[1])
    print value
    result = db_ops.db_insert("insert into feeds " + 
            "(category, feedname, sourceurl, feedurl) " + 
            "VALUES(?, ?, ?, ?)", value)
    print result

