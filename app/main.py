from flask import Flask, jsonify, request, render_template, send_file, Response
from api import *


# Flask应用程序
app = Flask(__name__)

app.register_blueprint(web_api, url_prefix='/api')


@app.route('/')
def index():
    return render_template('app.html')

@app.route('/view')
def viewer():
    return render_template('viewer.html')


if __name__ == '__main__':
    # 启动Flask应用程序
    app.run(host='0.0.0.0', port=5000, debug=True)