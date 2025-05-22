from flask import Flask, render_template_string

def runsite():    
    app = Flask(__name__)
    
    html_content = """
    <!DOCTYPE html>
    <html lang="fa">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>وضعیت ربات</title>
      <style>
        body {
          background: linear-gradient(135deg, #00c9ff, #92fe9d);
          font-family: 'Vazir', sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100vh;
          margin: 0;
          direction: rtl;
        }
        .message-box {
          background-color: white;
          padding: 40px;
          border-radius: 20px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.2);
          text-align: center;
          max-width: 400px;
        }
        .message-box h1 {
          color: #2ecc71;
          font-size: 2em;
          margin: 0;
        }
        .robot-icon {
          font-size: 4em;
          margin-bottom: 20px;
          color: #2ecc71;
        }
      </style>
      <link href="https://fonts.googleapis.com/css2?family=Vazir&display=swap" rel="stylesheet">
    </head>
    <body>
      <div class="message-box">
        <div class="robot-icon">😎</div>
        <h1>ربات روشن هست</h1>
      </div>
    </body>
    </html>
    """
    
    @app.route('/')
    def robot_status():
        return render_template_string(html_content)
    
    if __name__ == '__main__':
        app.run(debug=True,port=8080)
runsite()
    
