from flask import Flask, request

import requests, json
import xmlrpc.client
import http.client
import logging
from newsapi import NewsApiClient
app = Flask(__name__)
import pika, sys, os
import ZODB, ZODB.FileStorage
import persistent
import transaction
import hprose
import requests
import time


class Student(persistent.Persistent):
    studentName = ''
    studentdob = ''
    studentid = ''

    def setStudentName(self, sName):
        self.studentName = sName
    def getStudentName(self):
        return self.studentName

    def setStudentId(self, studentid):
        self.studentid = studentid
    def getStudentId(self):
        return self.studentid

    def setStudentDob(self, studentdob):
        self.studentDob = studentdob
    def getStudentDob(self):
        return self.studentDob


@app.route('/pingrpc')
def pingrpc():
    client = hprose.HttpClient('http://127.0.0.1:8080/')
    return client.ping("World")


@app.route('/')
def first():

    return 'Hello, World!'

@app.route('/publish')
def publish():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        time.sleep(body.count(b'.'))

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_cancel(consumer_tag="")
    channel.start_consuming()


@app.route('/readStudents')
def readstudents():

    storage = ZODB.FileStorage.FileStorage('mydata.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root
    
    output = ''
    output = output + root.s1.getStudentName() + '<br>'
    output = output + root.s1.getStudentId() + '<br>'
    output = output + root.s1.getStudentDob() + '<br>'

    return output
    

@app.route('/insertStudent')
def insertstudent():
    studentid = request.args.get('studentid')
    studentname = request.args.get('studentname')
    studentdob = request.args.get('studentdob')

    storage = ZODB.FileStorage.FileStorage('mydata.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root

    # saving the data
    root.s1 = Student()

    # set the data into the node
    root.s1.setStudentName(studentname)
    root.s1.setStudentId(studentid)
    root.s1.setStudentDob(studentdob)

    # save the changes!
    transaction.commit()
    
    
    logging.info('/insertStudent' + studentid + '-' + studentname + '-' + studentdob) 
    return 'Insert student'

@app.route('/justweather')
def weather():
    
    newsapi = NewsApiClient(api_key='0cb1d586898e4507bbb32e52ad999bae')
    all_articles = newsapi.get_everything(q='weather forecast',
                                      domains='independent.ie',
                                      from_param='2021-04-14',
                                      to='2021-04-25',
                                      language='en',
                                      sort_by='relevancy',
                                      page=1)

    output = ''    

    print(type(all_articles))

    for i in all_articles['articles']:
        print(i)
        output = output + i['title']
    
    return output




@app.route('/updates')
def justupdates_call():
    f = open('updates.txt', 'r')
    x = f.readlines()
    output = '{'

    print(type(x))
    print(x)

    for item in x:
    #   "line1": "item1",
        output = output + '"line": "'+item + '",'
    f.close()

    output = output[:-1]

    output = output + '}'

    return output

@app.route('/getnews')
def get_news():
    newsapi = NewsApiClient(api_key='0cb1d586898e4507bbb32e52ad999bae')

    all_articles = newsapi.get_everything(q='bitcoin',
                                      sources='bbc-news,the-verge',
                                      domains='bbc.co.uk,techcrunch.com',
                                      from_param='2021-03-11',
                                      to='2021-12-12',
                                      language='en',
                                      sort_by='relevancy',
                                      page=1)

    print(type(all_articles))

    output = ''

    for k, v in all_articles.items():
        print(k, v)
        output = output + str(v)
    return output


@app.route('/sendData')
def send_data():
    data = request.args.get('data')

    return 'Sending data to the server:' + str(data)


@app.route('/callClient')
def call_rpc():
    # calling the RPC server
    data = request.args.get('data', type = int)
    output = ''
    with xmlrpc.client.ServerProxy("http://localhost:8001/") as proxy:
        output = output + "temp is : %s" % str(proxy.is_warm(data))
        
    # printed to the browser
    return output

@app.route('/ping')
def ping_call():
    return 'Pong'

@app.route('/manual')
def manual():
    r = requests.get('http://newsapi.org/v2/everything?q=tesla&from=2021-03-18&sortBy=publishedAt&apiKey=0cb1d586898e4507bbb32e52ad999bae')

    print(r.status_code)

    print(r.text)



