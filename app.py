import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import google.generativeai as genai
from google.generativeai import types

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli_açar_bura_yaz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# API Setup (Açarını bura əlavə et)
# GOOGLE_API_KEY = "BURA_ÖZ_GEMINI_API_AÇARINI_YAZ"
# genai.configure(api_key=GOOGLE_API_KEY)

db = SQLAlchemy(app)

# --- Modellər ---
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question', backref='subject', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) # 'Easy', 'Medium', 'Hard'
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    answers = db.relationship('Answer', backref='result', lazy=True)
    subject = db.relationship('Subject', backref='results')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    points = db.Column(db.Integer, nullable=False)
    max_points = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    question = db.relationship('Question', backref='answers')

# --- Funksiyalar ---
def get_exam_questions(subject_id):
    try:
        # UNEC stili: 2 Asan, 2 Orta, 1 Çətin
        easy = Question.query.filter_by(subject_id=subject_id, difficulty='Easy').order_by(db.func.random()).limit(2).all()
        medium = Question.query.filter_by(subject_id=subject_id, difficulty='Medium').order_by(db.func.random()).limit(2).all()
        hard = Question.query.filter_by(subject_id=subject_id, difficulty='Hard').order_by(db.func.random()).limit(1).all()
        return easy + medium + hard
    except Exception as e:
        print(f"Error getting exam questions: {e}")
        return []

def ai_grade_answer(question_text, student_answer, image_path=None, api_key=None):
    if not api_key:
        return "API açarı tapılmadı."
    
    import google.generativeai as genai
    import re
    genai.configure(api_key=api_key)
    
    # Remove LaTeX expressions to avoid parsing issues with AI
    clean_question = re.sub(r'\\[(\[].*?\\[)\]]', '[MATH EXPRESSION]', question_text)
    clean_question = re.sub(r'\\\(.*?\\\)', '[MATH EXPRESSION]', clean_question)
    clean_question = re.sub(r'\$\$.*?\$\$', '[MATH EXPRESSION]', clean_question)
    clean_question = re.sub(r'\$.*?\$', '[MATH EXPRESSION]', clean_question)
    
    clean_answer = re.sub(r'\\[(\[].*?\\[)\]]', '[MATH EXPRESSION]', student_answer)
    clean_answer = re.sub(r'\\\(.*?\\\)', '[MATH EXPRESSION]', clean_answer)
    clean_answer = re.sub(r'\$\$.*?\$\$', '[MATH EXPRESSION]', clean_answer)
    clean_answer = re.sub(r'\$.*?\$', '[MATH EXPRESSION]', clean_answer)
    
    prompt = f"""You are a university mathematics professor grading student answers.

QUESTION: {clean_question}

STUDENT ANSWER: {clean_answer}

If there is an image, analyze the handwritten answer in it. The image may contain mathematical formulas, calculations, or graphs.

Grade the answer based on:
- Correctness: Mathematical calculations, formulas, and logic
- Completeness: Are all steps shown?
- Explanation: Is the answer explained?

Grade on a 10-point scale (whole numbers only):
- 10: Perfectly correct
- 7-9: Mostly correct with minor errors
- 4-6: Partially correct with major errors
- 1-3: Minimally correct with many errors
- 0: Completely wrong or no answer

Format your response EXACTLY like this:
Score: [0-10 number]
Feedback: [Brief feedback on what's correct and what's wrong]"""
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if image_path:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
            with open(full_path, 'rb') as f:
                image_data = f.read()
            
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        return f"Xəta baş verdi: {str(e)}"

# --- Rouselər ---
@app.route('/')
def index():
    if 'username' not in session:
        return render_template('index.html', need_username=True)
    if 'api_key' not in session:
        return render_template('index.html', need_api=True, need_username=False)
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects, need_api=False, need_username=False)

@app.route('/set_username', methods=['POST'])
def set_username():
    username = request.form.get('username')
    if username:
        session['username'] = username
    return redirect(url_for('index'))

@app.route('/set_api', methods=['POST'])
def set_api():
    api_key = request.form.get('api_key')
    if api_key:
        # Test the API key validity
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # Make a simple test call to verify the key
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content("Hello")
            # If we get here without exception, key is valid
            session['api_key'] = api_key
            flash("API key is valid and saved!", "success")
        except Exception as e:
            flash(f"Invalid API key: {str(e)}", "error")
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/exam/<int:subject_id>', methods=['GET', 'POST'])
def exam(subject_id):
    if 'username' not in session or 'api_key' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        try:
            questions = get_exam_questions(subject_id)
            if len(questions) < 5:
                return "Bazada kifayət qədər sual yoxdur! Zəhmət olmasa əvvəlcə sualları əlavə edin."
            
            return render_template('exam.html', questions=questions, subject_id=subject_id)
        except Exception as e:
            return f"Xəta baş verdi: {str(e)}"
    
    if request.method == 'POST':
        results = []
        total_score = 0
        
        # Create result entry
        result = Result(username=session['username'], subject_id=subject_id, total_score=0)
        db.session.add(result)
        db.session.commit()
        
        # Formalardan gələn cavabları yığırıq
        question_ids = request.form.getlist('question_id')
        
        for q_id in question_ids:
            answer_text = request.form.get(f'answer_{q_id}')
            question = Question.query.get(q_id)
            
            # Şəkil yükləmə hissəsi
            file = request.files.get(f'file_{q_id}')
            filename = None
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # AI Yoxlaması
            ai_feedback = ai_grade_answer(question.text, answer_text, filename, session['api_key'])
            
            # Parse points from AI feedback
            points = 0
            try:
                for line in ai_feedback.split('\n'):
                    if line.startswith('Xal:'):
                        score = int(line.split(':')[1].strip())
                        max_points = 5 if question.difficulty == 'Easy' else 10 if question.difficulty == 'Medium' else 20
                        points = int((score / 10) * max_points)
                        break
            except:
                points = 0
            
            total_score += points
            
            # Save answer
            answer = Answer(result_id=result.id, question_id=q_id, answer_text=answer_text, 
                          image_path=filename, points=points, 
                          max_points=5 if question.difficulty == 'Easy' else 10 if question.difficulty == 'Medium' else 20,
                          feedback=ai_feedback)
            db.session.add(answer)
            
            results.append({
                'question': question.text,
                'student_answer': answer_text,
                'feedback': ai_feedback,
                'image': filename,
                'points': points,
                'max_points': 5 if question.difficulty == 'Easy' else 10 if question.difficulty == 'Medium' else 20
            })

        # Update total score
        result.total_score = total_score
        db.session.commit()

        return render_template('result.html', results=results, total_score=total_score)

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('index'))
    results = Result.query.options(
        joinedload(Result.subject),
        joinedload(Result.answers).joinedload(Answer.question)
    ).filter_by(username=session['username']).order_by(Result.exam_date.desc()).all()
    return render_template('history.html', results=results)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    # Get all results for dashboard
    all_results = Result.query.options(joinedload(Result.subject)).order_by(Result.exam_date.desc()).all()
    
    # Calculate stats
    total_users = len(set(r.username for r in all_results))
    total_exams = len(all_results)
    avg_score = sum(r.total_score for r in all_results) / total_exams if total_exams > 0 else 0
    
    return render_template('dashboard.html', results=all_results, 
                         total_users=total_users, total_exams=total_exams, avg_score=avg_score)

# Bazanı yaratmaq üçün (ilk işə salanda bir dəfə)
with app.app_context():
    db.create_all()
    # Test üçün fənləri əlavə edirik (əgər yoxdursa)
    if not Subject.query.first():
        s1 = Subject(name="Kompüter Arxitekturası")
        s2 = Subject(name="Kompüter Mühəndisliyinin Əsasları")
        s3 = Subject(name="Riyazi Analiz")
        db.session.add_all([s1, s2, s3])
        db.session.commit()
    
    # Sualları əlavə et (əgər yoxdursa)
    if not Question.query.first():
        try:
            # Riyazi Analiz sualları
            math_subject = Subject.query.filter_by(name="Riyazi Analiz").first()
            if math_subject:
                # Asan suallar
                easy_questions = [
                    (r"1. Prove the equality \(A \cap B = B \cap A\) (Theoretical)", "Easy"),
                    (r"2. Prove that a non-empty set of numbers that is bounded above has an upper bound. (Theoretical)", "Easy"),
                    (r"3. Prove that a non-empty numerical set bounded below has a lower bound. (Theoretical)", "Easy"),
                    (r"4. If \(\{x\}\) is a set of numbers and \(\{-x\}\) is the set of negatives, prove \(\inf\{-x\} = -\sup\{x\}\).", "Easy"),
                    (r"5. Find the domain of \(f(x)=7\cot(\pi x)+\arcsin(18^{x})\)", "Easy"),
                ]
                
                for text, difficulty in easy_questions:
                    q = Question(text=text, difficulty=difficulty, subject_id=math_subject.id)
                    db.session.add(q)
                
                # Orta suallar
                medium_questions = [
                    (r"24. Prove necessary and sufficient condition for differentiability ($f'(x_0)$ exists and is finite). (Theoretical)", "Medium"),
                    (r"25. Prove the Product Rule: $(uv)^{\prime}=u^{\prime}v+uv^{\prime}$. (Theoretical)", "Medium"),
                    (r"26. Differential of a function and its geometric meaning ($dy=f'(x)dx$). (Theoretical)", "Medium"),
                ]
                
                for text, difficulty in medium_questions:
                    q = Question(text=text, difficulty=difficulty, subject_id=math_subject.id)
                    db.session.add(q)
                
                # Çətin suallar
                hard_questions = [
                    (r"50. Prove the Fundamental Theorem of Calculus. (Theoretical)", "Hard"),
                ]
                
                for text, difficulty in hard_questions:
                    q = Question(text=text, difficulty=difficulty, subject_id=math_subject.id)
                    db.session.add(q)
                
                db.session.commit()
                print("Questions seeded successfully")
        except Exception as e:
            print(f"Error seeding questions: {e}")
            db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True)