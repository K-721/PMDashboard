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

