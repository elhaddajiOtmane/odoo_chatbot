from flask import Flask, request, jsonify
import xmlrpc.client
import logging
import socket
import smtplib
import dns.resolver
import idna

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

url = 'https://havet-digital.odoo.com'
db = 'havet-digital'
username = 'contact@onlysim.fr'
password = 'WT9JdYij436gt2'

def verify_email(email):
    print(f"Verifying email: {email}")
    
    try:
        local_part, domain = email.split('@')
        print(f"Local part: {local_part}")
        print(f"Domain: {domain}")
    except ValueError:
        return False, "Invalid email format"

    if not domain or len(domain) > 255:
        return False, "Invalid domain: empty or too long"

    try:
        encoded_domain = idna.encode(domain).decode('ascii')
        print(f"Encoded domain: {encoded_domain}")
    except idna.IDNAError as e:
        return False, f"Invalid domain: {str(e)}"

    try:
        mx_records = dns.resolver.resolve(encoded_domain, 'MX')
        print(f"MX records: {mx_records}")
    except dns.resolver.NXDOMAIN:
        return False, "Domain does not exist"
    except dns.resolver.NoAnswer:
        return False, "No MX records found for domain"
    except dns.exception.DNSException as e:
        return False, f"DNS error: {str(e)}"

    mx_servers = sorted(mx_records, key=lambda x: x.preference)
    for mx in mx_servers:
        mx_server = str(mx.exchange)
        print(f"Trying MX server: {mx_server}")
        
        if mx_server == '.':
            print("Invalid MX server, skipping")
            continue

        try:
            smtp = smtplib.SMTP(timeout=10)
            smtp.connect(mx_server)
            smtp.helo(smtp.local_hostname)
            smtp.mail('')
            code, message = smtp.rcpt(str(email))
            smtp.quit()

            if code == 250:
                return True, "Email address exists"
            else:
                return False, f"Email address does not exist (SMTP code: {code})"
        except (socket.gaierror, socket.error, smtplib.SMTPException, UnicodeError) as e:
            print(f"Error with MX server {mx_server}: {str(e)}")
            continue

    return False, "Unable to verify email with any MX server"

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
                    font-family: Arial, sans-serif.
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

    # Email verification
    email_valid, email_message = verify_email(email_from)
    email_validation_status = "oui" if email_valid else "no"
    
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
                'x_studio_valide': email_validation_status,
            }])
            logging.info(f'Lead created with id: {lead_id}')
            return jsonify({'status': 'success', 'lead_id': lead_id, 'email_validation': email_message})
        else:
            logging.error('Authentication failed')
            return jsonify({'status': 'failed', 'error': 'Authentication failed'}), 401
    except Exception as e:
        logging.error(f'Error during lead creation: {e}')
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/get_leads', methods=['GET'])
def get_leads():
    logging.debug('Received request for /get_leads')

    x_token = request.headers.get('X-Token')
    if x_token != '8lGC0d8AHr98O5dM':
        logging.warning('Invalid token')
        return jsonify({'status': 'failed', 'error': 'Invalid token'}), 401

    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            leads = models.execute_kw(db, uid, password, 'crm.lead', 'search_read', [
                [],  
                ['partner_name', 'name', 'phone', 'email_from', 'x_studio_offre', 'x_studio_valide']
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
