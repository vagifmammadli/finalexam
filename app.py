"""
UNEC Exam Simulator - Flask Application
An AI-powered exam system with automatic grading using Google Gemini API
"""

import os
import random
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from markupsafe import Markup
import google.generativeai as genai
from PIL import Image

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli_açar_bura_yaz')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)


# ============================================================================
# TEMPLATE FILTERS
# ============================================================================

@app.template_filter('safe_no_comments')
def safe_no_comments(text):
    """
    Escape HTML comment sequences to prevent parsing errors
    while preserving other HTML content
    """
    if not text:
        return ''
    text = str(text).replace('<!--', '&lt;!--').replace('-->', '--&gt;')
    return Markup(text)


# ============================================================================
# DATABASE MODELS
# ============================================================================

class Subject(db.Model):
    """Subject/Course model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question', backref='subject', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('Result', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'


class Question(db.Model):
    """Question model with difficulty levels"""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # 'Easy', 'Medium', 'Hard'
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    answers = db.relationship('Answer', backref='question', lazy=True)

    def __repr__(self):
        return f'<Question {self.id}: {self.difficulty}>'


class Result(db.Model):
    """Exam result model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    exam_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    answers = db.relationship('Answer', backref='result', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Result {self.username}: {self.total_score}>'


class Answer(db.Model):
    """Individual answer model"""
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    points = db.Column(db.Integer, nullable=False, default=0)
    max_points = db.Column(db.Integer, nullable=False, default=10)
    feedback = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Answer {self.points}/{self.max_points}>'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_exam_questions(subject_id):
    """
    Get exam questions in UNEC format: 2 Easy, 2 Medium, 1 Hard
    Returns questions ordered by difficulty: Easy first, then Medium, then Hard
    """
    try:
        easy_all = Question.query.filter_by(subject_id=subject_id, difficulty='Easy').all()
        medium_all = Question.query.filter_by(subject_id=subject_id, difficulty='Medium').all()
        hard_all = Question.query.filter_by(subject_id=subject_id, difficulty='Hard').all()
        
        random.shuffle(easy_all)
        random.shuffle(medium_all)
        random.shuffle(hard_all)
        
        easy = easy_all[:2]
        medium = medium_all[:2]
        hard = hard_all[:1]
        
        questions = easy + medium + hard
        # Questions ordered by difficulty: Easy first, then Medium, then Hard
        
        return questions
    except Exception as e:
        app.logger.error(f"Error getting exam questions: {e}")
        return []


def clean_for_ai(text):
    """
    Clean LaTeX and text for AI processing
    Converts LaTeX delimiters to $$ format and removes backslashes
    """
    if not text:
        return ""
    
    # Convert LaTeX delimiters to $$
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)  # \(...\) -> $...$
    text = re.sub(r'\\\[(.*?)\\\]', r'$\1$', text)  # \[...\] -> $...$
    
    # Remove all backslashes
    text = re.sub(r'\\', '', text)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def ai_grade_answer(question_text, student_answer, image_path=None, api_key=None):
    """
    Grade student answer using Google Gemini AI
    Returns formatted feedback with score and comments
    """
    if not api_key:
        return "Xal: 0\nRəy: API açarı tapılmadı."
    
    try:
        clean_question = clean_for_ai(question_text)
        clean_answer = clean_for_ai(student_answer)
        
        # Detailed grading prompt
        prompt = f"""
Grade this mathematics answer based on the following criteria:

Question: {clean_question}

Student Answer: {clean_answer}

Grading Criteria:
1. Mathematical Correctness (40%): Is the math accurate and correct?
2. Completeness (30%): Does the answer fully address the question?
3. Logical Reasoning (20%): Is the reasoning sound and well-structured?
4. Clarity of Explanation (10%): Is the answer clearly expressed?

Provide a score from 0-10 and brief feedback.

Format your response as:
Score: X/10
Feedback: [brief explanation]
"""
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if image_path:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
            if os.path.exists(full_path):
                try:
                    image = Image.open(full_path)
                    response = model.generate_content([prompt, image])
                except Exception as img_error:
                    app.logger.error(f"Error processing image: {img_error}")
                    response = model.generate_content(prompt)
            else:
                response = model.generate_content(prompt)
        else:
            response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        
        # Extract score (0-10)
        score_match = re.search(r'Score:\s*(\d+)/10', response_text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 5
        score = max(0, min(10, score))  # Ensure score is between 0-10
        
        # Extract feedback
        feedback_match = re.search(r'Feedback:\s*(.+)', response_text, re.IGNORECASE | re.DOTALL)
        feedback = feedback_match.group(1).strip() if feedback_match else response_text
        
        return f"Xal: {score}\nRəy: {feedback}"
        
    except Exception as e:
        app.logger.error(f"Error in AI grading: {e}")
        return f"Xal: 5\nRəy: Cavab qiymətləndirilə bilmədi: {str(e)}"


def calculate_max_points(difficulty):
    """Calculate maximum points based on difficulty level"""
    points_map = {'Easy': 5, 'Medium': 10, 'Hard': 20}
    return points_map.get(difficulty, 10)


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main index page - shows username/API setup or subject selection"""
    if 'username' not in session:
        return render_template('index.html', need_username=True)
    
    if 'api_key' not in session:
        return render_template('index.html', need_api=True, need_username=False)
    
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects, need_api=False, need_username=False)


@app.route('/set_username', methods=['POST'])
def set_username():
    """Set username in session"""
    username = request.form.get('username', '').strip()
    if username:
        session['username'] = username
        flash('İstifadəçi adı uğurla təyin edildi!', 'success')
    else:
        flash('İstifadəçi adı boş ola bilməz!', 'error')
    return redirect(url_for('index'))


@app.route('/set_api', methods=['POST'])
def set_api():
    """Set and validate Gemini API key"""
    api_key = request.form.get('api_key', '').strip()
    if not api_key:
        flash('API açarı daxil edilməyib!', 'error')
        return redirect(url_for('index'))
    
    try:
        # Test the API key validity
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello")
        
        # If we get here without exception, key is valid
        session['api_key'] = api_key
        flash('API açarı uğurla təyin edildi!', 'success')
    except Exception as e:
        app.logger.error(f"Invalid API key: {e}")
        flash(f'Yanlış API açarı: {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/exam/<int:subject_id>', methods=['GET', 'POST'])
def exam(subject_id):
    """Exam page - display questions or process exam submission"""
    if 'username' not in session or 'api_key' not in session:
        flash('İmtahana başlamaq üçün istifadəçi adı və API açarı lazımdır!', 'error')
        return redirect(url_for('index'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'GET':
        try:
            questions = get_exam_questions(subject_id)
            if len(questions) < 5:
                flash('Bazada kifayət qədər sual yoxdur! Zəhmət olmasa əvvəlcə sualları əlavə edin.', 'error')
                return redirect(url_for('index'))
            
            return render_template('exam.html', questions=questions, subject_id=subject_id, subject_name=subject.name)
        except Exception as e:
            app.logger.error(f"Error in exam GET: {e}")
            flash(f'Xəta baş verdi: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    # POST - Process exam submission
    try:
        results = []
        total_score = 0
        
        # Create result entry
        result = Result(
            username=session['username'],
            subject_id=subject_id,
            total_score=0
        )
        db.session.add(result)
        db.session.flush()  # Get result.id
        
        # Process answers
        question_ids = request.form.getlist('question_id')
        
        for q_id in question_ids:
            try:
                q_id = int(q_id)
                answer_text = request.form.get(f'answer_{q_id}', '')
                question = Question.query.get(q_id)
                
                if not question:
                    continue
                
                # Handle file upload
                filename = None
                file = request.files.get(f'file_{q_id}')
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    if filename:
                        # Add timestamp to avoid collisions
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        filename = timestamp + filename
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # AI grading
                ai_feedback = ai_grade_answer(
                    question.text,
                    answer_text,
                    filename,
                    session['api_key']
                )
                
                # Calculate points
                max_points = calculate_max_points(question.difficulty)
                points = 0
                
                try:
                    for line in ai_feedback.split('\n'):
                        if line.startswith('Xal:'):
                            score = int(line.split(':')[1].strip())
                            points = int((score / 10) * max_points)
                            break
                except (ValueError, IndexError, AttributeError) as e:
                    app.logger.error(f"Error parsing points: {e}")
                    points = 0
                
                total_score += points
                
                # Save answer
                answer = Answer(
                    result_id=result.id,
                    question_id=q_id,
                    answer_text=answer_text,
                    image_path=filename,
                    points=points,
                    max_points=max_points,
                    feedback=ai_feedback
                )
                db.session.add(answer)
                
                results.append({
                    'question': question.text,
                    'student_answer': answer_text,
                    'feedback': ai_feedback,
                    'image': filename,
                    'points': points,
                    'max_points': max_points,
                    'difficulty': question.difficulty
                })
            except Exception as e:
                app.logger.error(f"Error processing answer for question {q_id}: {e}")
                continue
        
        # Update total score
        result.total_score = total_score
        db.session.commit()
        
        return render_template('result.html', results=results, total_score=total_score)
        
    except Exception as e:
        app.logger.error(f"Error in exam POST: {e}")
        db.session.rollback()
        flash(f'İmtahan zamanı xəta baş verdi: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/history')
def history():
    """Display user's exam history"""
    if 'username' not in session:
        flash('Tarixçəyə baxmaq üçün giriş edin!', 'error')
        return redirect(url_for('index'))
    
    results = Result.query.options(
        joinedload(Result.subject),
        joinedload(Result.answers).joinedload(Answer.question)
    ).filter_by(username=session['username']).order_by(Result.exam_date.desc()).all()
    
    return render_template('history.html', results=results)


@app.route('/dashboard')
def dashboard():
    """Display dashboard with all exam statistics"""
    if 'username' not in session:
        flash('Dashboard-a baxmaq üçün giriş edin!', 'error')
        return redirect(url_for('index'))
    
    all_results = Result.query.options(joinedload(Result.subject)).order_by(Result.exam_date.desc()).all()
    
    # Calculate statistics
    total_users = len(set(r.username for r in all_results))
    total_exams = len(all_results)
    avg_score = sum(r.total_score for r in all_results) / total_exams if total_exams > 0 else 0
    
    return render_template('dashboard.html', 
                         results=all_results,
                         total_users=total_users,
                         total_exams=total_exams,
                         avg_score=avg_score)


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_database():
    """Initialize database with default subjects"""
    with app.app_context():
        db.create_all()
        
        # Add default subjects if they don't exist
        if not Subject.query.first():
            subjects = [
                Subject(name="Kompüter Arxitekturası"),
                Subject(name="Kompüter Mühəndisliyinin Əsasları"),
                Subject(name="Riyazi Analiz")
            ]
            db.session.add_all(subjects)
            db.session.commit()
            app.logger.info("Default subjects created")


if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)