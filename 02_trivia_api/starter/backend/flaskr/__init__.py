from importlib import resources
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category
import random

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={"*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
      "Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS"
    )
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_gategories():
    categories = Category.query.order_by(Category.id).all()
    categories_format = {}
    for category in categories:
      categories_format[category.id] = category.type

    return jsonify({
        'success': True,
        'categories': categories_format
        })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    page = request.args.get('page', 1, type=int)
    pagination = Question.query.paginate(page, per_page=QUESTIONS_PER_PAGE, error_out=False)
    questions = pagination.items
    questions = [question.format() for question in questions]

    categories = Category.query.order_by(Category.id).all()
    categories_format = {}
    for category in categories:
      categories_format[category.id] = category.type    
    current_category = request.form.get('category')

    if len(questions) == 0:
      abort(404)
    
    return jsonify({
      "success": True,
      "questions": questions,
      "totalQuestions": pagination.total,
      "currentCategory": current_category,
      "categories": categories_format
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        "success": True
      })

    except:
      abort(422)
      
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
 
    new_question = body.get("question", None)
    new_answer = body.get("answer", None)
    new_difficulty = body.get("difficulty", None)
    new_category = body.get("category", None)
    new_search = body.get("searchTerm", None)

    try:
      if new_search is None:
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()

        return jsonify({ 
          "success": True
        })
      else:
        return search_question()

    except:
        abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def search_question():
    body = request.get_json()

    search = body.get("searchTerm", None)

    try:
      if search is not None:
        #questions = Question.query.filter(
          #Question.question.ilike(f'%{search}%')).all()
        page = request.args.get('page', 1, type=int)
        pagination = Question.query.filter(
          Question.question.ilike(f'%{search}%')).paginate(page, per_page=QUESTIONS_PER_PAGE, error_out=False)
        questions = pagination.items
        questions = [question.format() for question in questions]

        return jsonify({
          "success": True,
          "questions": questions
        })

    except:
      abort(422) 
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def category_questions(category_id):
    try:
      category = Category.query.get(category_id)
      if category is None:
        abort(422)
    
      page = request.args.get('page', 1, type=int)
      pagination = Question.query.filter_by(category=category_id).paginate(page, per_page=QUESTIONS_PER_PAGE, error_out=False)
      questions = pagination.items
      questions = [question.format() for question in questions]

      return jsonify({
        "success": True,
        "questions": questions
      })
    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()

    try:
      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)['id']

      current_category = Category.query.get(quiz_category)
      
      if current_category is None:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).filter(Question.category == quiz_category).all()

      format_questions = [question.format() for question in questions]
      random_question = None
      if len(format_questions) > 0:
        random_question = random.choice(format_questions)

      return jsonify({
        "success": True,
        "question": random_question
      })

    except:
      abort(422)
    

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return(
      jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
      }), 404
    )

  @app.errorhandler(422)
  def unprocessable(error):
    return(
      jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
      }), 422
    )

  @app.errorhandler(400)
  def bad_request(error):
    return(
      jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
      }), 400
    )

  @app.errorhandler(500)
  def internal_server(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
    }), 500
  
  return app

    