import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    def paginate(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page -1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

    def get_current_categories(all_questions):
        categories= []
        for ques in all_questions:
            if ques.category not in categories:
               categories.append(ques.category)
        return categories

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin','*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    def get_category_list():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type
        return categories


    @app.route('/categories')
    def get_categories():
        return jsonify({
            'success': True,
            'categories':get_category_list(),
            'total_categories':len(Category.query.all())
        })

   
    @app.route('/questions')
    def get_questions():
        all_questions = Question.query.all()
        current_questions = paginate(request,all_questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
        'success'  : True,
        'questions':current_questions,
        'total_questions':len(all_questions),
        'categories':get_category_list(),
        'current_category':get_current_categories(all_questions)
        })

    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def delete_question(question_id):
        que = Question.query.filter_by(id=question_id).first()

        if not que:
            abort(404)
        que.delete()
        
        all_questions = Question.query.order_by(Question.id).all()
        current_question = paginate(request,all_questions)

        return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions':len(Question.query.all()),
            'categories':get_category_list(),
            'current_category':get_current_categories(all_questions)
        })
  
    @app.route('/questions',methods=['POST'])
    def add_question():
        try:
            head = request.get_json()
            new_question = head['question']
            new_answer = head['answer']
            new_category = head['category']
            new_difficulty = head['difficulty']

            if ((new_question == '') or (new_answer == '') or (new_difficulty == '') or (new_category == '')):
                abort(422)

            que = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
            que.insert()

            return jsonify({
                'success': True
            })
        except:
            abort(405)
  

    @app.route('/questions/search',methods=['POST',"GET"])
    def search_questions():
        try:
            head = request.get_json()
            search_term = head['searchTerm']
            print(search_term)
            searched_question = Question.query.filter(Question.question.ilike("%{}%".format(search_term))).all()

            questions = paginate(request,searched_question)

            return jsonify({
                'success':True,
                'questions': questions,
                'total_questions':len(Question.query.all()),
                'current_category':get_current_categories(searched_question)  
            })
        except:
            abort(404)


    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            selected_cat_que = Question.query.filter(Question.category == str(category_id))
            current_questions = paginate(request,selected_cat_que)
            current_category = Category.query.get(category_id)
            return jsonify({
                'success':True,
                'questions':current_questions,
                'total_questions':len(Question.query.all()),
                'current_category':current_category.type
            })
        except:
            abort(404)

    @app.route('/quizzes',methods=['POST','GET'])
    def get_random_questions():
        head = request.get_json()
        previous_questions = head['previous_questions']
        quiz_category = head['quiz_category']['id']

        all_questions = Question.query.filter(Question.category == quiz_category).all()

        all_question_ids=[]
        visited=[]
        for a in all_questions:
            all_question_ids.append(a.id)

        if previous_questions is None:
            random_question_id = random.choice(all_question_ids)
            return jsonify({
                'success':True,
                'question':(Question.query.get(random_question_id)).format()
            })
        else:
            while(1):
                random_id = random.choice(all_question_ids)
                if (random_id in previous_questions) and (random_id not in visited):
                    visited.append(random_id)
                elif random_id not in previous_questions:
                    return jsonify({
                        'success':True,
                        'question':(Question.query.get(random_id)).format()
                    })
                elif len(visited) == len(previous_questions):
                    return jsonify({
                        'success':True,
                        'question':False
                    })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        })
    return app

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success":False,
            "error":405,
            "message":"method not found"
        })

    
