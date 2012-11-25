#!/usr/bin/env python
from datetime import datetime
from pyquery import PyQuery
from requests import session
from time import sleep


BASE_URL = 'https://192.168.0.100/'
REGISTER_URL = BASE_URL + 'register'
LOGIN_URL = BASE_URL + 'auth/login'
QUESTION_URL = BASE_URL + 'play/'
MEMORY_PATH = 'memory.txt'


def browse(session, url, post=False, data={}):
    if post:
        method = session.post
    else:
        method = session.get

    r = method(url, data=data, verify=False)
    return r.content


def get_xsrf_token(response):
    pq = PyQuery(response)
    return pq('input[name=_xsrf]').val()


def login(session, register=False, username='', password=''):
    if not username:
        bot_number = datetime.now().strftime('%H%M%S%f')
        username = 'fisa_bot_' + bot_number
        password = 'paparulo' + bot_number

        r = browse(session, REGISTER_URL)

        register_data = {
            'name': username,
            'email': username + '@gmail.com',
            'username': username,
            'password': password,
            'password_repeat': password,
            '_xsrf': get_xsrf_token(r),
        }
        r = browse(session, REGISTER_URL, post=True, data=register_data)

    r = browse(session, LOGIN_URL)

    login_data = {
        'username': username,
        'password': password,
        '_xsrf': get_xsrf_token(r),
    }
    r = browse(session, LOGIN_URL, post=True, data=login_data)

    return username, password


def get_questions():
    with session() as s:
        login(s, register=True)

        r = browse(s, BASE_URL)
        pq = PyQuery(r)

        questions = []
        for question_div in pq('div.grid-question'):
            link = PyQuery(question_div).parent().attr('href')
            if '/play/' in link:
                questions.append(link.split('/play/')[-1])

        return sorted(questions, key=int)


def get_choices(question):
    with session() as s:
        login(s, register=True)

        r = browse(s, QUESTION_URL + question)
        pq = PyQuery(r)

        choices_div = pq('div.answer-group')
        if choices_div:
            return [PyQuery(choice).attr('value')
                    for choice in PyQuery(choices_div)('input[type=radio]')]
        else:
            return []


def get_score(session):
    r = browse(session, BASE_URL)
    pq = PyQuery(r)
    user_score = int(pq('div.user-score').html().split(':')[1])
    return user_score


def check_correct(question, choice):
    with session() as s:
        login(s, register=True)

        score_before = get_score(s)

        answer_question(s, question, choice)

        score_after = get_score(s)
        if score_after > score_before:
            return True


def answer_question(s, question, choice):
    question_url = QUESTION_URL + question
    r = browse(s, question_url)

    answer_data = {
        'answer': choice,
        '_xsrf': get_xsrf_token(r),
    }
    browse(s, question_url, post=True, data=answer_data)


def get_answers(questions):
    answers = {}
    for question in questions:
        print 'Question:', question
        for choice in get_choices(question):
            print 'checking choice', choice
            if check_correct(question, choice):
                answers[question] = choice
                print 'correct!'
            else:
                print 'wrong'
            sleep(2)
        sleep(2)
    return answers


def answer_many_questions(username, password, answers, register=False):
    with session() as s:
        username, password = login(s,
                                   username=username,
                                   password=password,
                                   register=register)

        for question, choice in answers.items():
            print 'Answering question', question, 'with choice', choice
            answer_question(s, question, choice)

        return username, password


def remember():
    memory = {}
    for pair in open(MEMORY_PATH).read().split(';'):
        question, choice = pair.split(':')
        memory[question] = choice

    return memory


def learn(answers):
    memory = remember()
    memory.update(answers)

    memory_file = open(MEMORY_PATH, 'w')
    memory_file.write(';'.join('%s:%s' % (k,v)
                               for k,v in memory.items()))
    memory_file.close()

