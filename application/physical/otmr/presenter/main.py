import platform

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def root():

    python_version = platform.python_version()

    return render_template('index.html', python_version=python_version)


if __name__ == '__main__':
    # This is used when running locally only
    app.run(host='127.0.0.1', port=8080, debug=True)
