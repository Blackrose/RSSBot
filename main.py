import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import HTMLParser

import os.path
import sqlite3

import db_ops
import feedfetcher

import time
import threading
from multiprocessing import Process

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        #category = db_exec("select * from category")
        #self.render("index.html", category_list=category)
        feeds_list = db_ops.db_exec("select * from items")
        self.render("index.html")

class ArticleHandler(tornado.web.RequestHandler):
    def get(self):
        feedid = int(self.get_argument('feedid'))
        feed = db_ops.db_exec("select * from items where itemid=%d" % feedid )
        content = feed[0][6]
        #print content
        self.render("article.html", feed_item=feed, content=content)

class SidebarModule(tornado.web.UIModule):
    def render(self):
        category = db_ops.db_exec("select * from category")
        feeds_list = db_ops.db_exec("select * from feeds")
        return self.render_string("sidebar.html", category_list=category, feeds=feeds_list)

class FeedsModule(tornado.web.UIModule):
    def render(self):
        feeds_list = db_ops.db_exec("select * from feeds")
        return self.render_string("feeds.html", feeds=feeds_list)

class ItemslistModule(tornado.web.UIModule):
    def render(self):
        items_all = db_ops.db_exec("select * from items order by pubdate desc")
        return self.render_string("items_list.html", items_list=items_all)

def run_proc():
    db_ops.db_init()
    feed_urls = db_ops.db_exec("select feedurl from feeds")
    for url in feed_urls:
        print "Updating %s" % url
        fetch = feedfetcher.FeedFetcher(url)
        fetch.parse_items()

def update_items():
    p = Process(target=run_proc, args=())
    p.start()
    p.join()

    global timer
    timer = threading.Timer(200, update_items)
    timer.start()


if __name__ == "__main__":
    db_ops.db_init()
    #timer = threading.Timer(200, update_items)
    #timer.start()
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler),
        (r"/article", ArticleHandler)], 
            template_path=os.path.join(os.path.dirname(__file__), "templates"), 
            static_path=os.path.join(os.path.dirname(__file__), "templates/static"), 
            ui_modules={"sidebar":SidebarModule,
                "feeds":FeedsModule,
                "items_list":ItemslistModule}, debug=True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

