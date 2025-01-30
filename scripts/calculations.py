def perform_all_calculations(latest_measurement, last_two_kwh, kwh_data, live_measurements, user_inputs):
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

    kwh_rate = user_inputs['kwh_rate']
    #target_usage = user_inputs['target_usage']

    meter_id = live_measurements['meter_id']
    v_ab = live_measurements['v_ab']
    v_bc = live_measurements['v_bc']
    v_ca = live_measurements['v_ca']
    v_a = live_measurements['v_a']
    v_b = live_measurements['v_b']
    v_c = live_measurements['v_c']
    i_a = live_measurements['i_a']
    i_b = live_measurements['i_b']
    i_c = live_measurements['i_c']
    freq = live_measurements['freq']
    pf_a = live_measurements['pf_a']
    pf_b = live_measurements['pf_b']
    pf_c = live_measurements['pf_c']
    kw_a = live_measurements['kw_a']
    kw_b = live_measurements['kw_b']
    kw_c = live_measurements['kw_c']
    kw_total = live_measurements['kw_total']
    kvar_a = live_measurements['kvar_a']
    kvar_b = live_measurements['kvar_b']
    kvar_c = live_measurements['kvar_c']
    kvar_total = live_measurements['kvar_total']
    kva_a = live_measurements['kva_a']
    kva_b = live_measurements['kva_b']
    kva_c = live_measurements['kva_c']
    kva_total = live_measurements['kva_total']
    kwh = live_measurements['kwh']
    kvarh = live_measurements['kvarh']
    kvah = live_measurements['kvah']
    thd_v_a = live_measurements['thd_v_a']
    thd_v_b = live_measurements['thd_v_b']
    thd_v_c = live_measurements['thd_v_c']
    thd_i_a = live_measurements['thd_i_a']
    thd_i_b = live_measurements['thd_i_b']
    thd_i_c = live_measurements['thd_i_c']

    kwh_values = [row['kwh'] for row in last_two_kwh]
    kwh_agg = [row['kwh'] for row in kwh_data]

    # Call calculations
    voltage_imbalance = calculate_voltage_imbalance(v_a, v_b, v_c)
    current_limit = calculate_max_current(i_a, i_b, i_c)
    kvar_imbalance = calculate_kvar_imbalance(kvar_a, kvar_b, kvar_c)
    kw_imbalance = calculate_kw_imbalance(kw_a, kw_b, kw_c)
    max_pf = calculate_max_pf(pf_a, pf_b, pf_c)
    max_vthd = calculate_max_vthd(thd_v_a, thd_v_b, thd_v_c)
    max_ithd = calculate_max_ithd(thd_i_a, thd_i_b, thd_i_c)
    diff_kwh = calculate_diff_kwh(kwh_values)
    total_energy_usage = calculate_total_energy_usage(kwh_agg)
    total_cost = calculate_total_cost(total_energy_usage, kwh_rate)
    ave_efficiency = calculate_ave_efficiency(kw_total, kvar_total)
    prev_bill = calculate_prev_bill(total_cost)

    return {
        'latest_v_imbalance': voltage_imbalance,
        'latest_i': current_limit,
        'latest_kvar_imbalance': kvar_imbalance,
        'latest_kw_imbalance': kw_imbalance,
        'latest_pf': max_pf,
        'latest_vthd': max_vthd,
        'latest_ithd': max_ithd,
        'diff_kwh': diff_kwh,
        'total_energy_usage': total_energy_usage,
        'total_cost': total_cost,
        'ave_efficiency': ave_efficiency,
        'prev_bill': prev_bill
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

def calculate_diff_kwh(kwh_values):
    if len(kwh_values) == 2:
        # Subtract the newer value from the older value
        diff_kwh = kwh_values[1] - kwh_values[0]
        return diff_kwh
    return 0

def calculate_total_energy_usage(kwh_agg):
    total_energy_usage = 0
    for i in range(1, len(kwh_agg)):
        diff_kwh = float(kwh_agg[i]) - float(kwh_agg[i-1])
        total_energy_usage += diff_kwh
    return total_energy_usage

def calculate_total_cost(total_energy_usage, kwh_rate):
    total_cost = total_energy_usage * float(kwh_rate)
    return total_cost

def calculate_ave_efficiency(kvar_total, kw_total):
    if kvar_total == 0:
        return 0  # Avoid division by zero
    ave_efficiency = (kw_total / kvar_total) * 100 
    return ave_efficiency

def calculate_prev_bill(total_cost):
    prev_bill = total_cost - 0
    return prev_bill

