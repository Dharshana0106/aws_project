from flask import Flask, render_template, request, redirect, url_for, flash, session
import boto3
import uuid
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = 'cinemapulse-2026-movies-aws'

# AWS Configuration 
REGION = 'us-east-1' 

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# DynamoDB Tables (Create these tables manually in AWS Console)
users_table = dynamodb.Table('CinemaPulseUsers')
movies_table = dynamodb.Table('CinemaPulseMovies')
feedbacks_table = dynamodb.Table('CinemaPulseFeedbacks')

# SNS Topic ARN - Replace with your actual ARN
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:604665149129:cinemapulse_topic' 

def send_notification(subject, message):
    """Send SNS notification for user actions"""
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"✅ SNS Notification sent: {subject}")
    except ClientError as e:
        print(f"❌ SNS Error: {e}")

def init_dynamodb():
    """Initialize DynamoDB with sample data"""
    try:
        # Create sample movies (12 HOTTEST 2026 MOVIES 🔥)
        movies = [
            {
                'id': str(uuid.uuid4()),
                'title': 'Parashakthi',
                'description': "Sivakarthikeyan's historical action epic about brothers clashing during Tamil Nadu's 1965 Anti-Hindi protests, directed by Sudha Kongara.",
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Lara',
                'description': 'Ashok Kumar hunts a mysterious killer amid corruption—pure detective noir suspense.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Eleven',
                'description': 'Skilled officer tackles brutal serial killings with psychological twists.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Kaantha',
                'description': '1950s Madras mystery blending social drama and hidden crimes.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Stephen',
                'description': "Psychiatrist unravels a killer's mind in a chilling evaluation gone wrong.",
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Show Time',
                'description': 'Naveen Chandra in a tense crime unraveling full of betrayals.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Vikram',
                'description': 'Kamal Haasan as a brooding cop in gritty action-noir, echoing Batman\'s intensity.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Blackmail',
                'description': 'GV Prakash in a drama-thriller of deceit and dark secrets.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Maargan',
                'description': "Vijay Antony's crime-mystery with supernatural detective edges.",
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Ace',
                'description': 'Vijay Sethupathi as a crime-busting anti-hero in high-stakes action-noir.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Narivettai',
                'description': 'Tovino Thomas in a revenge-fueled crime probe.',
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Indra',
                'description': "Vasanth Ravi's suspenseful pursuit through betrayal webs.",
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Sleepwalker',
                'description': "Psychological thriller about a mother caught in grief and blurred reality after her daughters loss.",
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': '28 Years Later: The Bone Temple',
                'description': "A post-apocalyptic survival horror sequel that follows humanity struggle to survive decades after a devastating global outbreak.",
                'average_rating': 0.0,
                'total_reviews': 0
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Return to Silent Hill',
                'description': "Horror film based on the classic video game franchise Silent Hill with atmospheric thrills.",
                'average_rating': 0.0,
                'total_reviews': 0  
            }]
        
        # Check if movies exist, if not create them
        movies_scan = movies_table.scan()
        if len(movies_scan.get('Items', [])) == 0:
            with movies_table.batch_writer() as batch:
                for movie in movies:
                    batch.put_item(Item=movie)
            print("✅ 12 HOT 2026 MOVIES LOADED TO DYNAMODB!")
        
        # Create sample users
        sample_users = [
            {'id': 'admin-1', 'username': 'Admin', 'email': 'admin@cinemapulse.com', 'password': 'admin123', 'user_type': 'admin'},
            {'id': 'user-1', 'username': 'User', 'email': 'user@cinemapulse.com', 'password': 'user123', 'user_type': 'user'}
        ]
        
        for user in sample_users:
            try:
                users_table.put_item(Item=user)
            except ClientError:
                pass  # User might already exist
        
        print("👤 ADMIN: admin@cinemapulse.com / admin123")
        print("👤 USER: user@cinemapulse.com / user123")
        
    except Exception as e:
        print(f"❌ Init error: {e}")

def update_movie_stats(movie_id):
    """Update movie average rating and review count"""
    try:
        # Get all feedbacks for this movie
        feedbacks = feedbacks_table.scan(
            FilterExpression=Key('movie_id').eq(movie_id)
        )
        
        ratings = [item['rating'] for item in feedbacks.get('Items', [])]
        total_reviews = len(ratings)
        average_rating = round(sum(ratings) / total_reviews, 1) if ratings else 0.0
        
        # Update movie stats
        movies_table.update_item(
            Key={'id': movie_id},
            UpdateExpression='SET average_rating = :avg, total_reviews = :count',
            ExpressionAttributeValues={
                ':avg': average_rating,
                ':count': total_reviews
            }
        )
    except Exception as e:
        print(f"❌ Update stats error: {e}")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        
        response = users_table.get_item(Key={'email': email})
        
        if ('Item' in response and 
            response['Item']['password'] == password):
            user = response['Item']
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            flash(f'✅ Welcome {user["username"]}!')
            
            send_notification("User Login", f"User {user['username']} logged in")
            return redirect(url_for('about'))
        
        flash('❌ Invalid credentials!')
    
    return render_template('login.html')

@app.route('/about')
def about():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/home')
def home():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    
    # Fetch all movies from DynamoDB
    response = movies_table.scan()
    movies = response.get('Items', [])
    
    return render_template('home.html', movies=movies)

@app.route('/feedback/<movie_id>', methods=['GET', 'POST'])
def feedback(movie_id):
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    
    # Get movie details
    movie_response = movies_table.get_item(Key={'id': movie_id})
    movie = movie_response.get('Item')
    
    if request.method == 'POST':
        feedback_id = str(uuid.uuid4())
        
        feedback_data = {
            'id': feedback_id,
            'username': request.form['username'],
            'email': request.form['email'],
            'movie_id': movie_id,
            'rating': int(request.form['rating']),
            'comments': request.form['comments'],
            'created_at': datetime.now().isoformat()
        }
        
        feedbacks_table.put_item(Item=feedback_data)
        update_movie_stats(movie_id)
        
        send_notification("New Feedback", 
                         f"New feedback for {movie['title']} - Rating: {feedback_data['rating']}")
        
        return redirect(url_for('thankyou', movie_id=movie_id))
    
    return render_template('feedback.html', movie=movie)

@app.route('/thankyou/<movie_id>')
def thankyou(movie_id):
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    
    movie_response = movies_table.get_item(Key={'id': movie_id})
    movie = movie_response.get('Item')
    
    return render_template('thankyou.html', movie=movie)

@app.route('/admin')
def admin_panel():
    if session.get('user_type') != 'admin': 
        return redirect(url_for('login'))
    
    # Get all feedbacks with movie titles
    feedbacks_response = feedbacks_table.scan()
    feedbacks = feedbacks_response.get('Items', [])
    
    # Add movie titles to feedbacks
    for feedback in feedbacks:
        movie_resp = movies_table.get_item(Key={'id': feedback['movie_id']})
        if 'Item' in movie_resp:
            feedback['movie_title'] = movie_resp['Item']['title']
    
    return render_template('admin.html', feedbacks=feedbacks)

@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    session.clear()
    flash('👋 Logged out!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🚀 Initializing CinemaPulse AWS...")
    init_dynamodb()
    print("\n🎬 http://localhost:5000")
    print("🔧 AWS DynamoDB + SNS Integration Active!")
    app.run(host='0.0.0.0', port=5000, debug=True)
