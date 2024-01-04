from flask import Flask, jsonify
import pandas as pd
from db_data import create_connection, mongo_db_create
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
# import pymongo

conn = create_connection()
mongo_db = mongo_db_create()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "dsjb2bjb2j2JHjhbhJknjbJj"
app.config['SERVER_NAME'] = '0.0.0.0:5000'
jwt = JWTManager(app)

@app.route('/register/<username>/<name>/<password>', methods=['POST'])
def register_user(name, username, password):

    try:
        user_df = pd.DataFrame(list(zip([username],[name], [generate_password_hash(password)])), columns=['username', 'name', 'password'])
        user_df.to_sql(name='Users', con=conn, if_exists='append', index=False)
    except Exception as e:
        user = find_by_username(username)
        if user:
            return jsonify({'error': 'Cannot create user due to username existing'}), 500
        
        return jsonify({'error': 'Cannot create user due to some error'}), 500

    access_token = create_access_token(identity=username)
    return jsonify({ "token": access_token, "user_id": username })

def find_by_username(username):
    
    try:
        # print("fetch user data")
        # print("SELECT * FROM Users WHERE username='{}'".format(username))
        data = pd.read_sql("SELECT * FROM Users WHERE username='{}'".format(username), conn)
        # print("data fetched: {}".format(data))
        # print("username: {}".format(data.iloc[0]['username']))
        # print("data.empty: {}".format(data.empty))
        if not data.empty:
            # print("Data sent: {}".format(data.iloc[0]))
            return data.iloc[0]['password']
    except:
        return

@app.route('/login/<username>/<password>', methods=['GET'])
def login_user(username, password):
    
    try:
        # print("in try")
        password_fetched = find_by_username(username)
        # print("Password check: {}".format(check_password_hash(password_fetched, password)))
        if username and check_password_hash(password_fetched, password):
            access_token = create_access_token(identity=username)
            return jsonify({ "token": access_token, "user_id": username })
    except Exception as e:
        return jsonify({'error': 'Not working'}), 500

@app.route('/insert_new_product/<name>/<description>/<cost>', methods=['POST'])
@jwt_required()
def insert_product(name: str, description: str, cost: int):
    current_user_id = get_jwt_identity()

    product = {'name': name, 'description': description, 'cost': cost}

    try:
        print("in try")
        mongo_db.insert_one(product)
        print("post try")
        return jsonify({'result': 'Product data inserted successfully'})
    except Exception as e:
        return jsonify({'error': 'Product insertion failed'})

@app.route('/list_products', methods=['GET'])
@jwt_required()
def list_products():
    current_user_id = get_jwt_identity()

    try:
        product_data = list(mongo_db.find({},{ "_id": 0, "name": 1, "description": 1, "cost": 1 }))
        return jsonify({'product_list': product_data})
    except Exception as e:
        return jsonify({'error': e.message})

@app.route('/get_product_detail/<name>', methods=['GET'])
@jwt_required()
def get_product_detail(name: str):

    current_user_id = get_jwt_identity()
    try:
        product_detail = list(mongo_db.find({'name': name},{ "_id": 0, "name": 1, "description": 1, "cost": 1 }))
        return jsonify({'product_detail': product_detail})
    except Exception as e:
        return jsonify({'error': 'Product detail finding failed'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# finkraft_backend_assignment-python-app-1
# finkraft_backend_assignment-mongodb-1