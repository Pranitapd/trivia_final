import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'Pranita123','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Who is current Prime Minister',
            'answer': 'Narendra Modi',
            'difficulty': '4',
            'category': 1,
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res =  self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_retrieve_questions_failed(self):
        res = self.client().get('/questions?page=100')
        self.assertEqual(res.status_code, 404)

    def test_delete_question(self): 
        # make sure there is a question with this id in the db, otherwise the test will fail.
        res = self.client().delete('/questions/18')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_delete_question_failed(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(res.status_code, 404)
        

    def test_post_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_question(self):
        res = self.client().post('/questions/search',json={'searchTerm':'the'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_searched_question_not_found(self):
        res = self.client().post('/questions/search',json={'searchTerm':'Pranita'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_404_get_questions_by_category(self):
        res = self.client().get('/categories/10/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_quizzes(self):
        res = self.client().post('/quizzes',json={"previous_questions":[10,11,12],"quiz_category":{'id':1,'type':'Science'}})
        data = json.loads(res.data)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()