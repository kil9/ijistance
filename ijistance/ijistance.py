# -*- encoding: utf-8 -*-

app = Flask(__name__)

@app.route('/')
def main():
    return 'automatic report servie for i-jistance'

if __name__ == '__main__':
    app.run(port=21000, debug=True)
