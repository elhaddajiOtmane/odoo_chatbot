from flask import Flask, request, jsonify
import xmlrpc.client

app = Flask(__name__)

url = 'https://webnexa.odoo.com'
db = 'webnexa'
username = 'oelhaddaji@webnexa.net'
password = 'N53C#x?pdm93<'

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/create_lead', methods=['POST'])
def create_lead():
    # Check for X-Token header
    x_token = request.headers.get('X-Token')
    if x_token != '8lGC0d8AHr98O5dM':
        return jsonify({'status': 'failed', 'error': 'Invalid token'}), 401
    
    data = request.json
    name = data.get('name')
    contact_name = data.get('contact_name')
    email_from = data.get('email_from')
    phone = data.get('phone')
    project_requirements = data.get('project_requirements')

    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if uid:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [{
            'name': name,
            'contact_name': contact_name,
            'email_from': email_from,
            'phone': phone,
            'description': project_requirements,  # Store project requirements in the description field
        }])
        return jsonify({'status': 'success', 'lead_id': lead_id})
    else:
        return jsonify({'status': 'failed', 'error': 'Authentication failed'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
