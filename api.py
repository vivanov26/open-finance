from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import Response
import pandas as pd

app = Flask(__name__)


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


@app.route('/', methods=['GET'])
def index():
    if request_wants_json():
        return jsonify({'endpoints': [
            {'/': 'Index'},
            {'/notes/<symbol>': 'Single structured note historical value'}
        ]})
    else:
        return '''
        <html>
            <head>Welcome to Open Finance</head>
            <body>
                Available end-points (HTML or JSON depending on specified accepted MIME type header):
                <br/>
                <ol>
                    <li><b>/</b> -this page</li>
                    <li><b>/notes/&lt;symbol&gt;</b> -single structured note historical value</li>
                </ol>
            </body>
        </html>
        '''


@app.route('/notes/<string:symbol>', methods=['GET'])
def note(symbol):
    try:
        f = getattr(__import__("notes.%s" %
                               (symbol), fromlist=['notes']), 'response')
        r = f()
        result = pd.Series.to_json(r.portfolio, orient='split', date_format='iso')
        if request_wants_json():
            response = Response(result, status=200, mimetype='application/json')
        else:
            response = render_template('timeseries.html', data=result)
        
        return response
    except ModuleNotFoundError:
        app.logger.error("Module for %s not found." % symbol)
        return {'message': "Pricing for %s not found." % symbol}, 404


if __name__ == '__main__':
    app.run()
