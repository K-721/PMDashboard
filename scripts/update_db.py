import psycopg2

def fetch_latest_measurements(conn):
    """
    Fetch the latest measurements from the live_measurements table.
    Returns a dictionary for easy access to named columns.
    """
    query = """
        SELECT meter_id, v_a, v_b, v_c, i_a, i_b, i_c, kvar_a, kvar_b, kvar_c,
               kw_a, kw_b, kw_c, pf_a, pf_b, pf_c,
               thd_v_a, thd_v_b, thd_v_c, thd_i_a, thd_i_b, thd_i_c
        FROM live_measurements
        ORDER BY timestamp DESC
        LIMIT 1
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]  # Get column names
        result = cursor.fetchone()
        if result:
            latest_measurement = dict(zip(column_names, result))
            return latest_measurement
        else:
            return None

def fetch_live_measurements(conn):
    query = """
    SELECT timestamp, meter_id, v_ab, v_bc, v_ca, v_a, v_b, v_c,
        i_a, i_b, i_c, freq, pf_a, pf_b, pf_c, kw_a, kw_b, kw_c,
        kw_total, kvar_a, kvar_b, kvar_c, kvar_total, kva_a, kva_b, kva_c, kva_total,
        kwh, kvarh, kvah, thd_v_ab, thd_v_bc, thd_v_ca, thd_v_a, thd_v_b, thd_v_c, thd_i_a, thd_i_b, thd_i_c
    FROM live_measurements
    ORDER BY timestamp DESC
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]  # Get column names
        result = cursor.fetchall()
        if result:
            live_measurements = dict(zip(column_names, result))
            return live_measurements
        else:
            return None

def fetch_last_two_kwh_rows(conn):
    query = """
    SELECT timestamp, kwh
    FROM live_measurements
    ORDER BY timestamp DESC
    LIMIT 2
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]  # Get column names
        result = cursor.fetchall()  # Fetch all rows
        
        if result:
            # Ensure last_two_kwh is a list of dictionaries
            last_two_kwh = []
            for row in result:
                row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
                last_two_kwh.append(row_dict)
            return last_two_kwh
        else:
            return []

def fetch_kwh_data(conn):
    query = """
    SELECT timestamp, kwh
    FROM live_measurements
    WHERE EXTRACT(MONTH FROM timestamp) = EXTRACT(MONTH FROM CURRENT_DATE)
    ORDER BY timestamp DESC
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]  # Get column names
        result = cursor.fetchall()  # Fetch all rows
        
        if result:
            # Convert each row to a dictionary
            kwh_data = []
            for row in result:
                row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
                kwh_data.append(row_dict)
                
            return kwh_data
        else:
            return []

def fetch_user_inputs(conn):
    query = """
        SELECT user_id, kwh_rate, target_usage
        FROM user_inputs
        ORDER BY created_at DESC
        LIMIT 1
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]  # Get column names
        result = cursor.fetchone()
        if result:
            user_inputs = dict(zip(column_names, result))
            return user_inputs
        else:
            return None

def update_status_header(conn, meter_id, calculations):
    query = """
    INSERT INTO status_header (
        meter_id, latest_v_imbalance, latest_i, latest_kvar_imbalance,
        latest_kw_imbalance, latest_pf, latest_vthd, latest_ithd
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (meter_id) 
DO UPDATE SET
    latest_v_imbalance = EXCLUDED.latest_v_imbalance,
    latest_i = EXCLUDED.latest_i,
    latest_kvar_imbalance = EXCLUDED.latest_kvar_imbalance,
    latest_kw_imbalance = EXCLUDED.latest_kw_imbalance,
    latest_pf = EXCLUDED.latest_pf,
    latest_vthd = EXCLUDED.latest_vthd,
    latest_ithd = EXCLUDED.latest_ithd;
    """
    values = (
        meter_id,
        calculations['latest_v_imbalance'],
        calculations['latest_i'],
        calculations['latest_kvar_imbalance'],
        calculations['latest_kw_imbalance'],
        calculations['latest_pf'],
        calculations['latest_vthd'],
        calculations['latest_ithd']
    )
    
    with conn.cursor() as cursor:
        cursor.execute(query, values)
    conn.commit()
    print("Upserting status_header with values: %s", values)

