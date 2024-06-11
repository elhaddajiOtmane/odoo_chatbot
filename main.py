import xmlrpc.client

url = 'https://havetdigital1.odoo.com'
db = 'havetdigital1'
username = 'necherrate@havetdigital.fr'
password = 'Nour.2022'

# Authenticate
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
if not uid:
    print('Authentication failed.')
    exit()

# Fetch and print all fields of crm.lead
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
fields = models.execute_kw(db, uid, password, 'crm.lead', 'fields_get', [], {'attributes': ['string', 'help', 'type']})

# Print all fields
for field in fields:
    print(f"Field: {field}, Type: {fields[field]['type']}, Label: {fields[field]['string']}")

# Alternatively, print only custom fields
print("\nCustom Fields:")
for field in fields:
    if field.startswith('x_'):
        print(f"Field: {field}, Type: {fields[field]['type']}, Label: {fields[field]['string']}")
