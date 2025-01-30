
def fetch_latest_measurements(conn):
    query = """
        SELECT meter_id, v_ab, v_bc, v_ca, v_a, v_b, v_c,
            i_a, i_b, i_c, freq, pf_a, pf_b, pf_c, kw_a, kw_b, kw_c,
            kw_total, kvar_a, kvar_b, kvar_c, kvar_total, kva_a, kva_b, kva_c, kva_total,
            kwh, kvarh, kvah, thd_v_ab, thd_v_bc, thd_v_ca, thd_v_a, thd_v_b, thd_v_c, thd_i_a, thd_i_b, thd_i_c
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

def fetch_kwh_data(conn):
    query = """
    SELECT timestamp, diff_kwh
    FROM live_measurements
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

def update_stats_panel(conn, meter_id, calculations):
    query = """
    INSERT INTO stats_panel (
        meter_id, total_energy_usage, total_cost, ave_efficiency, prev_bill, proj_usage,
        proj_cost, proj_savings, curr_monthly_usage, proj_monthly_usage, ave_monthly_usage
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        meter_id,
        #calculations['diff_kwh'],
        calculations['total_energy_usage'],
        calculations['total_cost'],
        calculations['ave_efficiency'],
        calculations['prev_bill'],
        calculations['proj_usage'],
        calculations['proj_cost'],
        calculations['proj_savings'],
        calculations['curr_monthly_usage'],
        calculations['proj_monthly_usage'],
        calculations['ave_monthly_usage']
    )
    
    with conn.cursor() as cursor:
        cursor.execute(query, values)
    conn.commit()
    print("Inserting stats_panel with values: %s", values)

def update_pred_maintenance(conn, meter_id, latest_measurement):
    query = """
    INSERT INTO pred_maintenance (
        meter_id, latest_v_ab, latest_v_bc, latest_v_ca, latest_i_a, latest_i_b, latest_i_c,
        latest_pf_a, latest_pf_b, latest_pf_c, latest_vthd_a, latest_vthd_b, latest_vthd_c,
        latest_ithd_a, latest_ithd_b, latest_ithd_c
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
     
    values = (
        meter_id,
        latest_measurement['v_ab'],
        latest_measurement['v_bc'],
        latest_measurement['v_ca'],
        latest_measurement['i_a'],
        latest_measurement['i_b'],
        latest_measurement['i_c'],
        latest_measurement['pf_a'],
        latest_measurement['pf_b'],
        latest_measurement['pf_c'],
        latest_measurement['thd_v_a'],
        latest_measurement['thd_v_b'],
        latest_measurement['thd_v_c'],
        latest_measurement['thd_i_a'],
        latest_measurement['thd_i_b'],
        latest_measurement['thd_i_c']
    )
    
    with conn.cursor() as cursor:
        cursor.execute(query, values)
    conn.commit()
    print("Inserting pred_maintenance with values: %s", values)