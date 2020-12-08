import json
import os
import re
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)

class API(db.Model):
    __tablename__ = 'apis'
    id = db.Column(db.Integer, primary_key=True)
    apiname = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Endpoints(db.Model):
    __tablename__ = 'endpoints'
    id = db.Column(db.Integer, primary_key=True)
    endpointname = db.Column(db.String)
    api_id = db.Column(db.Integer, db.ForeignKey('apis.id'))


"""
    CREATE TABLE recepie (
        id integer primary key auto_increment,
        recepie_name varchar(100),
        recepie_description text
    )
"""

def create_schema_from_dict(data):
    schema = data['schema']
    fields = [key for key in schema.keys() if type(schema[key]) != list and key != 'schema_name']
    schema_name = schema['schema_name']
    types = []
    for field in fields:
        type_data = schema[field]
        if type_data == 'primary_key':
            types.append('integer primary key')
        elif type_data.startswith("string"):
            size = re.findall(r'\(\d+\)', type_data)[0]
            types.append(f'varchar{size}')
        elif type_data.startswith('int'):
            types.append('integer')
        elif type_data.startswith('text'):
            types.append('text')

    field_rows = ', '.join(fields[i] + ' ' + types[i] for i in range(len(types)))

    sql_str = f"CREATE TABLE {schema_name} ({field_rows})"
    print(sql_str)
    db.engine.execute(sql_str)


@app.route("/")
def index():
    return "Index"

@app.route("/metaapi/<id>/apis/data", methods=['POST'])
def add_data(id):
    data = request.get_json()
    create_schema_from_dict(data)

@app.route("/apis/<path:uri>", methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def apis(uri):
    parts = uri.split('/')
    if len(parts) < 2:
        return json.dumps({'error': 'url must contain at least username and api name'})
    user = parts[0]
    api = parts[1]
    uri = parts[2:]
    method = request.method
    resp = {
        'method': method,
        'user': user,
        'api': api,
        'uri-parts': uri
    }
    return json.dumps(resp)


if __name__ == '__main__':
    app.run()
