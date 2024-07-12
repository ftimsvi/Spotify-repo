from flask_cors import CORS
from spotify import create_app

app = create_app()

CORS(app, resources={r'/*': {'origins': 'http://localhost:3000'}})

if __name__ == '__main__':
    app.run(debug=True)
