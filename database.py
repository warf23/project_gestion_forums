import sqlite3

def get_db_connection():
    """Creates a database connection that returns rows as dictionaries."""
    conn = sqlite3.connect('instance/main.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    
    # --- Create Companies Table ---
    conn.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            representative TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT
        )
    ''')
    
    # --- Create Reservations Table ---
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            sponsorship_package TEXT NOT NULL,
            stand_id TEXT,
            contract_status TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')

    # --- Check if dummy data exists ---
    company_count = conn.execute('SELECT COUNT(id) FROM companies').fetchone()[0]
    
    if company_count == 0:
        print("Populating database with sample data...")
        # Add sample companies
        conn.execute('INSERT INTO companies (name, representative, email, phone) VALUES (?, ?, ?, ?)',
                     ('Green Solutions Inc.', 'Alice Martin', 'alice@greensolutions.com', '555-0101'))
        conn.execute('INSERT INTO companies (name, representative, email, phone) VALUES (?, ?, ?, ?)',
                     ('Innovatech Corp', 'Bob Durand', 'bob@innovatech.com', '555-0102'))
        conn.execute('INSERT INTO companies (name, representative, email, phone) VALUES (?, ?, ?, ?)',
                     ('Data Systems', 'Charlie Leveque', 'charlie@datasys.fr', '555-0103'))
        
        # Add sample reservations
        conn.execute('INSERT INTO reservations (company_id, sponsorship_package, stand_id, contract_status) VALUES (?, ?, ?, ?)',
                     (1, 'Gold', 'A1', 'Confirmed'))
        conn.execute('INSERT INTO reservations (company_id, sponsorship_package, contract_status) VALUES (?, ?, ?)',
                     (2, 'Silver', 'Pending Contract'))
        conn.execute('INSERT INTO reservations (company_id, sponsorship_package, stand_id, contract_status) VALUES (?, ?, ?, ?)',
                     (3, 'Bronze', 'C5', 'Confirmed'))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")