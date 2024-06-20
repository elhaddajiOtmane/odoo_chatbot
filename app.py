from flask import Flask, request, jsonify
import xmlrpc.client
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

url = 'https://havetdigital1.odoo.com'
db = 'havetdigital1'
username = 'necherrate@havetdigital.fr'
password = 'Nour.2022'

@app.route('/')
def hello_world():
    return '''
    <html>
        <head>
            <title>Hello, World!</title>
            <style>
                body {
                    background-color: black;
                    color: green;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                }
                h1 {
                    font-size: 3em;
                }
            </style>
        </head>
        <body>
            <h1>Hello, World!</h1>
        </body>
    </html>
    '''

@app.route('/create_lead', methods=['POST'])
def create_lead():
    logging.debug('Received request for /create_lead')
    
    # Check for X-Token header
    x_token = request.headers.get('X-Token')
    if x_token != '8lGC0d8AHr98O5dM':
        logging.warning('Invalid token')
        return jsonify({'status': 'failed', 'error': 'Invalid token'}), 401
    
    data = request.json
    logging.debug(f'Request data: {data}')
    
    partner_name = data.get('partner_name')
    name = data.get('name')
    phone = data.get('phone')
    email_from = data.get('email_from')
    offre = data.get('x_studio_offre')

    # Authenticate
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [{
                'partner_name': partner_name,
                'name': name,
                'phone': phone,
                'email_from': email_from,
                'x_studio_offre': offre,
            }])
            logging.info(f'Lead created with id: {lead_id}')
            return jsonify({'status': 'success', 'lead_id': lead_id})
        else:
            logging.error('Authentication failed')
            return jsonify({'status': 'failed', 'error': 'Authentication failed'}), 401
    except Exception as e:
        logging.error(f'Error during lead creation: {e}')
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/get_leads', methods=['GET'])
def get_leads():
    logging.debug('Received request for /get_leads')

    # Check for X-Token header
    x_token = request.headers.get('X-Token')
    if x_token != '8lGC0d8AHr98O5dM':
        logging.warning('Invalid token')
        return jsonify({'status': 'failed', 'error': 'Invalid token'}), 401

    # Authenticate
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            leads = models.execute_kw(db, uid, password, 'crm.lead', 'search_read', [
                [],  
                ['partner_name', 'name', 'phone', 'email_from', 'x_studio_offre']
            ])
            logging.info(f'Leads retrieved: {leads}')
            return jsonify({'status': 'success', 'leads': leads})
        else:
            logging.error('Authentication failed')
            return jsonify({'status': 'failed', 'error': 'Authentication failed'}), 401
    except Exception as e:
        logging.error(f'Error during lead retrieval: {e}')
        return jsonify({'status': 'failed', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
