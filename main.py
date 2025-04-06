import os
from datetime import datetime
import pytz
from pymongo import MongoClient
from dotenv import load_dotenv
from fasthtml.common import *

# Load environment variables
load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 50000
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"

# MongoDB connection
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client['sujalkiguestbook']
collection = db['Forks']

# Create app with a favicon link
app, rt = fast_app(
    hdrs=(
        Link(rel='icon', type='image/favicon.ico', href="/assets/me.ico"),
        Link(rel='preconnect', href="https://fonts.googleapis.com"),
        Link(rel='preconnect', href="https://fonts.gstatic.com", crossorigin=""),
        Link(rel='stylesheet', href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
        Link(rel='stylesheet', href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
    )
)

def get_ist_time():
    ist_tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist_tz)

def add_message(name, message):
    if not name or not message:
        raise ValueError("Name and message cannot be empty")
    
    name = name.strip()[:MAX_NAME_CHAR]
    message = message.strip()[:MAX_MESSAGE_CHAR]
    
    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    try:
        collection.insert_one(
            {"name": name, "message": message, "timestamp": timestamp}
        )
    except Exception as e:
        print(f"Database error: {e}")
        raise

def get_messages():
    try:
        messages = list(collection.find().sort("timestamp", -1))
        return messages
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

def render_message(entry):
    return (
        Article(
            Header(
                Div(
                    I(_class="fas fa-user-circle user-icon"),
                    Span(entry.get('name', 'Anonymous'), _class="username"),
                    _class="user-info"
                ),
                _class="message-header"
            ),
            Div(
                P(
                    entry.get('message', 'No message'),
                    _class="message-content",
                    **{"_hx-on:load": """
                        if(this.scrollHeight > this.clientHeight) {
                            this.classList.add('scrollable');
                        }
                    """}
                ),
                _class="message-body"
            ),
            Footer(
                I(_class="far fa-clock"),
                Small(entry.get('timestamp', 'Unknown time')),
                _class="message-footer"
            ),
            _class="message-card"
        )
    )

def render_message_list():
    messages = get_messages()
    message_elements = [render_message(entry) for entry in messages]
    
    if not message_elements:
        message_elements = [
            Div(
                I(_class="far fa-comment-dots empty-icon"),
                H3("No messages yet"),
                P("Be the first to leave a message!"),
                _class="empty-state"
            )
        ]
    
    return Div(
        Div(*message_elements, _class="message-grid"),
        id="message-list",
    )

def render_theme_toggle():
    # Theme toggle script
    theme_script = Script("""
    document.addEventListener('DOMContentLoaded', function() {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        // Update active button state
        updateActiveThemeButton(savedTheme);
        
        // Set up theme buttons
        document.querySelectorAll('.theme-btn').forEach(button => {
            button.addEventListener('click', function() {
                const theme = this.getAttribute('data-theme');
                document.documentElement.setAttribute('data-theme', theme);
                localStorage.setItem('theme', theme);
                updateActiveThemeButton(theme);
            });
        });
        
        function updateActiveThemeButton(activeTheme) {
            document.querySelectorAll('.theme-btn').forEach(btn => {
                if (btn.getAttribute('data-theme') === activeTheme) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }
    });
    """)
    
    return Div(
        H3("Theme", _class="theme-title"),
        Div(
            Button(
                I(_class="fas fa-sun"),
                Span("Light"),
                _class="theme-btn",
                **{"data-theme": "light"}
            ),
            Button(
                I(_class="fas fa-moon"),
                Span("Dark"),
                _class="theme-btn",
                **{"data-theme": "dark"}
            ),
            Button(
                I(_class="fas fa-palette"),
                Span("Cosmic"),
                _class="theme-btn",
                **{"data-theme": "cosmic"}
            ),
            _class="theme-toggle-group"
        ),
        theme_script,
        _class="theme-toggle-container"
    )

def render_content():
    css_style = Style(
        """
        /* Theme Variables */
        :root {
            /* Light Theme (default) */
            --bg-gradient: linear-gradient(120deg, #f8f9fa 0%, #e9ecef 100%);
            --card-bg: #ffffff;
            --card-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.12);
            --primary: #4361ee;
            --secondary: #3f37c9;
            --accent: #4895ef;
            --text-primary: #212529;
            --text-secondary: #6c757d;
            --border: #dee2e6;
            --form-bg: rgba(255, 255, 255, 0.9);
            --header-bg: linear-gradient(135deg, #4361ee, #4895ef);
            --input-bg: #f8f9fa;
            --theme-btn-bg: #f8f9fa;
            --theme-btn-text: #212529;
            --theme-btn-active-bg: #4361ee;
            --theme-btn-active-text: #ffffff;
            --footer-bg: rgba(255, 255, 255, 0.8);
            --scrollbar-track: #f1f1f1;
            --scrollbar-thumb: #4361ee;
        }
        
        /* Dark Theme */
        [data-theme="dark"] {
            --bg-gradient: linear-gradient(120deg, #121212 0%, #1e1e1e 100%);
            --card-bg: #2d2d2d;
            --card-shadow: 0 10px 20px rgba(0, 0, 0, 0.25);
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
            --primary: #4cc9f0;
            --secondary: #4895ef;
            --accent: #3a86ff;
            --text-primary: #f8f9fa;
            --text-secondary: #adb5bd;
            --border: #495057;
            --form-bg: rgba(45, 45, 45, 0.9);
            --header-bg: linear-gradient(135deg, #4cc9f0, #3a86ff);
            --input-bg: #343a40;
            --theme-btn-bg: #343a40;
            --theme-btn-text: #f8f9fa;
            --theme-btn-active-bg: #4cc9f0;
            --theme-btn-active-text: #212529;
            --footer-bg: rgba(45, 45, 45, 0.8);
            --scrollbar-track: #343a40;
            --scrollbar-thumb: #4cc9f0;
        }
        
        /* Cosmic Theme */
        [data-theme="cosmic"] {
            --bg-gradient: linear-gradient(120deg, #10002b 0%, #240046 100%);
            --card-bg: #3c096c;
            --card-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            --card-hover-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
            --primary: #9d4edd;
            --secondary: #c77dff;
            --accent: #e0aaff;
            --text-primary: #ffffff;
            --text-secondary: #e0aaff;
            --border: #5a189a;
            --form-bg: rgba(60, 9, 108, 0.9);
            --header-bg: linear-gradient(135deg, #9d4edd, #e0aaff);
            --input-bg: #240046;
            --theme-btn-bg: #240046;
            --theme-btn-text: #e0aaff;
            --theme-btn-active-bg: #9d4edd;
            --theme-btn-active-text: #ffffff;
            --footer-bg: rgba(60, 9, 108, 0.8);
            --scrollbar-track: #240046;
            --scrollbar-thumb: #9d4edd;
        }
        
        /* Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--bg-gradient);
            background-attachment: fixed;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
        }
        
        /* Header Styles */
        .guestbook-header {
            text-align: center;
            padding: 35px 25px;
            margin-bottom: 40px;
            background: var(--header-bg);
            border-radius: 16px;
            color: white;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1), 0 3px 6px rgba(0, 0, 0, 0.05);
            position: relative;
            overflow: hidden;
        }
        
        .guestbook-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.15) 0%, transparent 40%);
        }
        
        .guestbook-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
        }
        
        .guestbook-header p {
            margin-top: 12px;
            font-size: 1.1rem;
            opacity: 0.9;
            position: relative;
        }
        
        .guestbook-image {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            border: 3px solid white;
            display: block;
            margin: 20px auto 10px;
            object-fit: cover;
            position: relative;
        }
        
        .guestbook-image:hover {
            transform: scale(1.1) rotate(5deg);
        }
        
        /* Form Styles */
        .form-container {
            background: var(--form-bg);
            padding: 35px;
            border-radius: 16px;
            box-shadow: var(--card-shadow);
            margin: 20px auto 40px;
            max-width: 600px;
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
        }
        
        .form-title {
            margin-bottom: 20px;
            color: var(--primary);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        fieldset {
            border: none;
            padding: 0;
            margin: 0;
        }
        
        .input-wrapper {
            margin-bottom: 20px;
            position: relative;
        }
        
        .input-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--secondary);
        }
        
        input[type="text"] {
            width: 100%;
            padding: 14px 15px 14px 45px;
            border: 2px solid var(--border);
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: var(--input-bg);
            color: var(--text-primary);
        }
        
        input[type="text"]:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.25);
        }
        
        .message-input {
            width: 100%;
            padding: 14px 15px 14px 45px;
            border: 2px solid var(--border);
            border-radius: 12px;
            font-size: 16px;
            font-family: 'Inter', sans-serif;
            min-height: 100px;
            resize: vertical;
            transition: all 0.3s ease;
            background: var(--input-bg);
            color: var(--text-primary);
        }
        
        .message-input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.25);
        }
        
        .message-icon {
            top: 20px;
            transform: none;
        }
        
        button[type="submit"] {
            width: 100%;
            padding: 14px 25px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(67, 97, 238, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        button[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(67, 97, 238, 0.4);
        }
        
        button[type="submit"]:active {
            transform: translateY(1px);
        }
        
        /* Theme Toggle Styles */
        .theme-toggle-container {
            background: var(--form-bg);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
        }
        
        .theme-title {
            font-size: 18px;
            margin-bottom: 15px;
            color: var(--primary);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .theme-toggle-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .theme-btn {
            flex: 1;
            min-width: 100px;
            padding: 12px 15px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--theme-btn-bg);
            color: var(--theme-btn-text);
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-weight: 500;
        }
        
        .theme-btn.active {
            background: var(--theme-btn-active-bg);
            color: var(--theme-btn-active-text);
            border-color: var(--theme-btn-active-bg);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        }
        
        .theme-btn:hover:not(.active) {
            border-color: var(--primary);
            transform: translateY(-2px);
        }
        
        /* Message Grid Layout */
        .message-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .message-card {
            border: 1px solid var(--border);
            border-radius: 16px;
            background: var(--card-bg);
            box-shadow: var(--card-shadow);
            transition: all 0.3s ease;
            height: 300px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }
        
        .message-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--card-hover-shadow);
        }
        
        .message-header {
            padding: 20px 20px 15px;
            border-bottom: 1px solid var(--border);
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .user-icon {
            color: var(--primary);
            font-size: 20px;
        }
        
        .username {
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .message-body {
            padding: 15px 20px;
            flex-grow: 1;
            overflow: hidden;
            position: relative;
        }
        
        .message-content {
            margin: 0;
            color: var(--text-secondary);
            line-height: 1.7;
            height: 100%;
            overflow-y: auto;
            padding-right: 10px;
        }
        
        .message-content::-webkit-scrollbar {
            width: 6px;
        }
        
        .message-content::-webkit-scrollbar-track {
            background: var(--scrollbar-track);
            border-radius: 3px;
        }
        
        .message-content::-webkit-scrollbar-thumb {
            background-color: var(--scrollbar-thumb);
            border-radius: 3px;
        }
        
        .message-footer {
            padding: 15px 20px;
            border-top: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        /* Empty State */
        .empty-state {
            grid-column: 1 / -1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--card-bg);
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border);
            color: var(--text-secondary);
        }
        
        .empty-icon {
            font-size: 48px;
            margin-bottom: 15px;
            color: var(--primary);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: var(--text-secondary);
            background: var(--footer-bg);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
        }
        
        .footer a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        .author-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
        }
        
        .author-link {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .heart {
            color: #ff6b6b;
            display: inline-block;
            animation: heartbeat 1.5s infinite;
        }
        
        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message-card {
            animation: fadeIn 0.3s ease-out;
        }
        
        /* Responsive Styles */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .guestbook-header {
                padding: 25px 15px;
            }
            
            .guestbook-header h1 {
                font-size: 2rem;
            }
            
            .form-container {
                padding: 25px;
            }
            
            .theme-toggle-group {
                flex-direction: column;
            }
            
            .message-grid {
                grid-template-columns: 1fr;
            }
            
            .message-card {
                height: auto;
                min-height: 200px;
            }
        }
        """
    )

    # Form component
    form = Form(
        H3(I(_class="far fa-comment-dots"), " Leave a Message", _class="form-title"),
        Fieldset(
            Div(
                Div(
                    I(_class="fas fa-user input-icon"),
                    Input(
                        type="text",
                        name="name",
                        placeholder="Your Name",
                        required=True,
                        maxlength=MAX_NAME_CHAR,
                    ),
                    _class="input-wrapper"
                ),
                Div(
                    I(_class="fas fa-pen input-icon message-icon"),
                    Textarea(
                        placeholder="Write something nice!",
                        name="message",
                        required=True,
                        _class="message-input",
                    ),
                    _class="input-wrapper"
                ),
                Button(I(_class="fas fa-paper-plane"), " Send Message", type="submit"),
            ),
            role="group",
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset()",
        _class="form-container"
    )

    # Header component
    header = Div(
        H1("Suji's Guestbook"),
        P("Share your thoughts and connect with others"),
        _class="guestbook-header"
    )

    # Footer component
    footer = Div(
        P("Made with ", Span("❤️", _class="heart"), " by ", 
          A("Sujal", href="https://github.com/sujalkalra", target="_blank")),
        Div(
            A(I(_class="fab fa-github"), " GitHub", 
              href="https://github.com/sujalkalra", 
              target="_blank", 
              _class="author-link"),
            A(I(_class="fas fa-code"), " Try New Version", 
              href="https://sujiguestbook2.vercel.app", 
              target="_blank", 
              _class="author-link"),
            _class="author-links"
        ),
        _class="footer"
    )

    # User profile image
    image_with_link = A(
        Img(
            src="/assets/me.png",
            alt="Sujal's Profile",
            _class="guestbook-image"
        ),
        href="https://github.com/sujalkalra",
        target="_blank"
    )

    return Div(
        css_style,
        Div(
            header,
            image_with_link,
            render_theme_toggle(),
            form,
            render_message_list(),
            footer,
            _class="container"
        )
    )

@rt('/')
def get():
    return Titled("Suji's Guestbook", render_content())

@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    try:
        add_message(name, message)
        return render_message_list()
    except ValueError as ve:
        return Div(
            P(f"Error: {ve}"),
            id="message-list"
        )
    except Exception as e:
        return Div(
            P(f"Error: Could not submit message. Please try again. Details: {e}"),
            id="message-list"
        )

# Check MongoDB connection
try:
    mongo_client.server_info()
except Exception as e:
    raise EnvironmentError(f"Database connection error: {e}")

if not os.getenv("MONGO_URI"):
    raise EnvironmentError("Missing required environment variable: MONGO_URI")

serve()
