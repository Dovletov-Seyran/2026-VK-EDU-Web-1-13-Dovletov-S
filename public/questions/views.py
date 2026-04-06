from django.shortcuts import render
from .utils import paginate


def index(request):
    questions = [
        {'id': i, 'title': f'Question {i}', 'text': f'Text of question {i}'}
        for i in range(1, 20)
    ]
    page = paginate(questions, request)
    return render(request, "questions/index.html", {'page': page})

def question(request, question_id):
    question = {'id': question_id, 'title': f'Question {question_id}', 'text': 'Some text'}
    answers = [{'id': i, 'text': f'Answer {i}'} for i in range(1, 5)]
    return render(request, "questions/question.html", {'question': question, 'answers': answers})

def tag(request, tag_name):
    questions = [
        {'id': i, 'title': f'Question about {tag_name} #{i}', 'text': f'Text {i}'}
        for i in range(1, 20)
    ]
    page = paginate(questions, request)
    return render(request, "questions/tag.html", {'page': page, 'tag': tag_name})

def hot(request):
    questions = [
        {'id': i, 'title': f'Hot Question {i}', 'text': f'Text of hot question {i}'}
        for i in range(1, 20)
    ]
    page = paginate(questions, request)
    return render(request, "questions/hot.html", {'page': page})

def ask(request):
    return render(request, "questions/ask.html")
