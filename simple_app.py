from flask import Flask
import os
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🎉 Todo Management App - Test Page</h1>
    <p>✅ Flask is working!</p>
    <p>🌐 DigitalOcean deployment successful!</p>
    <p>🔗 <a href="/test">Test endpoint</a></p>
    '''

@app.route('/test')
def test():
    return {
        'status': 'success',
        'message': 'DigitalOcean deployment working!',
        'python_version': sys.version,
        'flask_version': '2.3.3'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
