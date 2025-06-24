import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import get_db_connection, init_db

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key-for-production' # Change for production
# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Initialize the database
init_db()


# --- Main Dashboard Route ---
@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    
    # Get all companies
    companies = conn.execute('SELECT * FROM companies ORDER BY name').fetchall()
    
    # Get all reservations with company names
    reservations = conn.execute('''
        SELECT r.id, r.sponsorship_package, r.stand_id, r.contract_status, c.name as company_name
        FROM reservations r
        JOIN companies c ON r.company_id = c.id
        ORDER BY r.id DESC
    ''').fetchall()
    
    # Get reservations that DO NOT have a stand assigned yet (for the manual reservation modal)
    unassigned_reservations = conn.execute('''
        SELECT r.id, c.name as company_name
        FROM reservations r
        JOIN companies c ON r.company_id = c.id
        WHERE r.stand_id IS NULL OR r.stand_id = ''
    ''').fetchall()

    conn.close()
    
    # Create a set of reserved stand IDs for quick lookup in the template
    reserved_stands = {res['stand_id'] for res in reservations if res['stand_id']}
    
    return render_template(
        'admin_dashboard.html', 
        companies=companies, 
        reservations=reservations,
        unassigned_reservations=unassigned_reservations,
        reserved_stands=reserved_stands
    )

# --- API-like Routes for Dynamic Actions ---

@app.route('/admin/add_company', methods=['POST'])
def add_company():
    name = request.form['name']
    representative = request.form['representative']
    email = request.form['email']
    phone = request.form['phone']

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO companies (name, representative, email, phone) VALUES (?, ?, ?, ?)',
                     (name, representative, email, phone))
        conn.commit()
    except conn.IntegrityError:
        # Handle cases where email or name is not unique
        pass # In a real app, you'd return an error message
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_reservation', methods=['POST'])
def add_reservation():
    company_id = request.form['company_id']
    package = request.form['sponsorship_package']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO reservations (company_id, sponsorship_package, contract_status) VALUES (?, ?, ?)',
                 (company_id, package, 'Pending Quote'))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/reserve_stand', methods=['POST'])
def reserve_stand():
    data = request.get_json()
    reservation_id = data.get('reservation_id')
    stand_id = data.get('stand_id')
    
    if not reservation_id or not stand_id:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
        
    conn = get_db_connection()
    # Also update status to 'Confirmed' when a stand is manually assigned
    conn.execute('UPDATE reservations SET stand_id = ?, contract_status = ? WHERE id = ?', 
                 (stand_id, 'Confirmed', reservation_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Stand {stand_id} reserved successfully!'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)