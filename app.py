from flask import Flask, request, jsonify
import xmlrpc.client
import logging

app = Flask(__name__)

url = 'https://havetdigital1.odoo.com'
db = 'havetdigital1'
username = 'necherrate@havetdigital.fr'
password = 'Nour.2022'

# Set up logging
logging.basicConfig(level=logging.DEBUG)

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
    x_studio_requirements = data.get('x_studio_requirements')

    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if uid:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        try:
            lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [{
                'name': name,
                'contact_name': contact_name,
                'email_from': email_from,
                'phone': phone,
                'description': x_studio_requirements,  # Ensure this is the correct field
            }])
            if lead_id:
                return jsonify({
                    'status': 'success',
                    'lead': {
                        'name': name,
                        'contact_name': contact_name,
                        'email_from': email_from,
                        'phone': phone,
                        'x_studio_requirements': x_studio_requirements
                    },
                    'lead_id': lead_id
                })
            else:
                logging.error('Lead creation failed')
                return jsonify({'status': 'failed', 'error': 'Lead creation failed'}), 500
        except Exception as e:
            logging.error(f'Error creating lead: {e}')
            return jsonify({'status': 'failed', 'error': 'Lead creation failed'}), 500
    else:
        logging.error('Authentication failed')
        return jsonify({'status': 'failed', 'error': 'Authentication failed'}), 401

@app.route('/get_leads', methods=['GET'])
def get_leads():
    # Check for X-Token header
    x_token = request.headers.get('X-Token')
    if x_token != '8lGC0d8AHr98O5dM':
        return jsonify({'status': 'failed', 'error': 'Invalid token'}), 401

    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if uid:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        leads = models.execute_kw(db, uid, password, 'crm.lead', 'search_read', [
            [],  
            ['name', 'contact_name', 'email_from', 'phone', 'description']  
        ])
        return jsonify({'status': 'success', 'leads': leads})
    else:
        logging.error('Authentication failed')
        return jsonify({'status': 'failed', 'error': 'Authentication failed'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
