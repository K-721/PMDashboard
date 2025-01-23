def perform_all_calculations(latest_measurement):
    #meter_id = latest_measurement['meter_id']
    v_a = latest_measurement['v_a']
    v_b = latest_measurement['v_b']
    v_c = latest_measurement['v_c']
    i_a = latest_measurement['i_a']
    i_b = latest_measurement['i_b']
    i_c = latest_measurement['i_c']
    kvar_a = latest_measurement['kvar_a']
    kvar_b = latest_measurement['kvar_b']
    kvar_c = latest_measurement['kvar_c']
    kw_a = latest_measurement['kw_a']
    kw_b = latest_measurement['kw_b']
    kw_c = latest_measurement['kw_c']
    pf_a = latest_measurement['pf_a']
    pf_b = latest_measurement['pf_b']
    pf_c = latest_measurement['pf_c']
    thd_v_a = latest_measurement['thd_v_a']
    thd_v_b = latest_measurement['thd_v_b']
    thd_v_c = latest_measurement['thd_v_c']
    thd_i_a = latest_measurement['thd_i_a']
    thd_i_b = latest_measurement['thd_i_b']
    thd_i_c = latest_measurement['thd_i_c']

    # Call calculations
    voltage_imbalance = calculate_voltage_imbalance(v_a, v_b, v_c)
    current_limit = calculate_max_current(i_a, i_b, i_c)
    kvar_imbalance = calculate_kvar_imbalance(kvar_a, kvar_b, kvar_c)
    kw_imbalance = calculate_kw_imbalance(kw_a, kw_b, kw_c)
    max_pf = calculate_max_pf(pf_a, pf_b, pf_c)
    max_vthd = calculate_max_vthd(thd_v_a, thd_v_b, thd_v_c)
    max_ithd = calculate_max_ithd(thd_i_a, thd_i_b, thd_i_c)

    
    return {
        'latest_v_imbalance': voltage_imbalance,
        'latest_i': current_limit,
        'latest_kvar_imbalance': kvar_imbalance,
        'latest_kw_imbalance': kw_imbalance,
        'latest_pf': max_pf,
        'latest_vthd': max_vthd,
        'latest_ithd': max_ithd
    }

def calculate_voltage_imbalance(v_a, v_b, v_c):
    v_avg = (v_a + v_b + v_c) / 3.0
    if v_avg == 0:
        return 0
    return max(abs(v_avg - v_a), abs(v_avg - v_b), abs(v_avg - v_c)) / v_avg * 100

def calculate_max_current(i_a, i_b, i_c):
    # Simulates GREATEST logic in SQL by returning the max absolute value
    return max(abs(i_a), abs(i_b), abs(i_c))

def calculate_kvar_imbalance(kvar_a, kvar_b, kvar_c):
    kvar_avg = (kvar_a + kvar_b + kvar_c) / 3.0
    if kvar_avg == 0:
        return 0
    return max(abs(kvar_avg - kvar_a), abs(kvar_avg - kvar_b), abs(kvar_avg - kvar_c)) / kvar_avg * 100

def calculate_kw_imbalance(kw_a, kw_b, kw_c):
    kw_avg = (kw_a + kw_b + kw_c) / 3.0
    if kw_avg == 0:
        return 0
    return max(abs(kw_avg - kw_a), abs(kw_avg - kw_b), abs(kw_avg - kw_c)) / kw_avg * 100

def calculate_max_pf(pf_a, pf_b, pf_c):
    # Return the greatest power factor value
    return max(pf_a, pf_b, pf_c)

def calculate_max_vthd(thd_v_a, thd_v_b, thd_v_c):
    return max(thd_v_a, thd_v_b, thd_v_c)

def calculate_max_ithd(thd_i_a, thd_i_b, thd_i_c):
    return max(thd_i_a, thd_i_b, thd_i_c)
