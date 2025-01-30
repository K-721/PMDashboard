from datetime import datetime
import calendar

def perform_all_calculations(latest_measurement, user_inputs, live_measurements, kwh_data):
    latest_meter_id = latest_measurement['meter_id']
    latest_v_ab = latest_measurement['v_ab']
    latest_v_bc = latest_measurement['v_bc']
    latest_v_ca = latest_measurement['v_ca']
    latest_v_a = latest_measurement['v_a']
    latest_v_b = latest_measurement['v_b']
    latest_v_c = latest_measurement['v_c']
    latest_i_a = latest_measurement['i_a']
    latest_i_b = latest_measurement['i_b']
    latest_i_c = latest_measurement['i_c']
    latest_freq = latest_measurement['freq']
    latest_pf_a = latest_measurement['pf_a']
    latest_pf_b = latest_measurement['pf_b']
    latest_pf_c = latest_measurement['pf_c']
    latest_kw_a = latest_measurement['kw_a']
    latest_kw_b = latest_measurement['kw_b']
    latest_kw_c = latest_measurement['kw_c']
    latest_kw_total = latest_measurement['kw_total']
    latest_kvar_a = latest_measurement['kvar_a']
    latest_kvar_b = latest_measurement['kvar_b']
    latest_kvar_c = latest_measurement['kvar_c']
    latest_kvar_total = latest_measurement['kvar_total']
    latest_kva_a = latest_measurement['kva_a']
    latest_kva_b = latest_measurement['kva_b']
    latest_kva_c = latest_measurement['kva_c']
    latest_kva_total = latest_measurement['kva_total']
    latest_kwh = latest_measurement['kwh']
    latest_kvarh = latest_measurement['kvarh']
    latest_kvah = latest_measurement['kvah']
    latest_thd_v_a = latest_measurement['thd_v_a']
    latest_thd_v_b = latest_measurement['thd_v_b']
    latest_thd_v_c = latest_measurement['thd_v_c']
    latest_thd_i_a = latest_measurement['thd_i_a']
    latest_thd_i_b = latest_measurement['thd_i_b']
    latest_thd_i_c = latest_measurement['thd_i_c']

    kwh_rate = user_inputs['kwh_rate']
    target_usage = user_inputs['target_usage']

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
    diff_kwh = live_measurements['diff_kwh']

    # Extract 'kwh' values from the last two rows
    #kwh_values = [row['kwh'] for row in last_two_kwh]
    data_timestamp = [(row['timestamp']) for row in kwh_data]
    data_diff_kwh = [(row['diff_kwh']) for row in kwh_data]

    # Call calculations
    voltage_imbalance = calculate_voltage_imbalance(latest_v_ab, latest_v_bc, latest_v_ca)
    current_limit = calculate_max_current(latest_i_a, latest_i_b, latest_i_c)
    kvar_imbalance = calculate_kvar_imbalance(latest_kvar_a, latest_kvar_b, latest_kvar_c)
    kw_imbalance = calculate_kw_imbalance(latest_kw_a, latest_kw_b, latest_kw_c)
    max_pf = calculate_max_pf(latest_pf_a, latest_pf_b, latest_pf_c)
    max_vthd = calculate_max_vthd(latest_thd_v_a, latest_thd_v_b, latest_thd_v_c)
    max_ithd = calculate_max_ithd(latest_thd_i_a, latest_thd_i_b, latest_thd_i_c)

    #diff_kwh = calculate_diff_kwh(kwh_values)
    total_energy_usage = calculate_total_energy_usage(data_timestamp, data_diff_kwh)
    total_cost = calculate_total_cost(total_energy_usage, kwh_rate)
    ave_efficiency = calculate_ave_efficiency(latest_kw_total, latest_kvar_total)
    prev_bill = calculate_prev_bill(data_timestamp, data_diff_kwh, kwh_rate)
    proj_usage = calculate_proj_usage(data_timestamp, data_diff_kwh)
    proj_cost = calculate_proj_cost(proj_usage, kwh_rate)
    proj_savings = calculate_proj_savings(proj_cost, prev_bill)
    curr_monthly_usage = calculate_curr_monthly_usage(total_energy_usage)
    proj_monthly_usage = calculate_proj_monthly_usage(proj_usage)
    ave_monthly_usage = calculate_ave_monthly_usage(data_timestamp, data_diff_kwh)

    return {
        'latest_v_imbalance': voltage_imbalance,
        'latest_i': current_limit,
        'latest_kvar_imbalance': kvar_imbalance,
        'latest_kw_imbalance': kw_imbalance,
        'latest_pf': max_pf,
        'latest_vthd': max_vthd,
        'latest_ithd': max_ithd,

        #'diff_kwh': diff_kwh,
        'total_energy_usage': total_energy_usage,
        'total_cost': total_cost,
        'ave_efficiency': ave_efficiency,
        'prev_bill': prev_bill,
        'proj_usage' : proj_usage,
        'proj_cost': proj_cost,
        'proj_savings': proj_savings,
        'curr_monthly_usage': curr_monthly_usage,
        'proj_monthly_usage': proj_monthly_usage,
        'ave_monthly_usage': ave_monthly_usage
    }


def calculate_voltage_imbalance(latest_v_ab, latest_v_bc, latest_v_ca):
    v_avg = (latest_v_ab + latest_v_bc + latest_v_ca) / 3.0
    if v_avg == 0:
        return 0
    return max(abs(v_avg - latest_v_ab), abs(v_avg - latest_v_bc), abs(v_avg - latest_v_ca)) / v_avg * 100

def calculate_max_current(latest_i_a, latest_i_b, latest_i_c):
    # Simulates GREATEST logic in SQL by returning the max absolute value
    return max(abs(latest_i_a), abs(latest_i_b), abs(latest_i_c))

def calculate_kvar_imbalance(latest_kvar_a, latest_kvar_b, latest_kvar_c):
    kvar_avg = (latest_kvar_a + latest_kvar_b + latest_kvar_c) / 3.0
    if kvar_avg == 0:
        return 0
    return max(abs(kvar_avg - latest_kvar_a), abs(kvar_avg - latest_kvar_b), abs(kvar_avg - latest_kvar_c)) / kvar_avg * 100

def calculate_kw_imbalance(latest_kw_a, latest_kw_b, latest_kw_c):
    kw_avg = (latest_kw_a + latest_kw_b + latest_kw_c) / 3.0
    if kw_avg == 0:
        return 0
    return max(abs(kw_avg - latest_kw_a), abs(kw_avg - latest_kw_b), abs(kw_avg - latest_kw_c)) / kw_avg * 100

def calculate_max_pf(latest_pf_a, latest_pf_b, latest_pf_c):
    # Return the greatest power factor value
    return max(latest_pf_a, latest_pf_b, latest_pf_c)

def calculate_max_vthd(latest_thd_v_a, latest_thd_v_b, latest_thd_v_c):
    return max(latest_thd_v_a, latest_thd_v_b, latest_thd_v_c)

def calculate_max_ithd(latest_thd_i_a, latest_thd_i_b, latest_thd_i_c):
    return max(latest_thd_i_a, latest_thd_i_b, latest_thd_i_c)

def calculate_total_energy_usage(data_timestamp, data_diff_kwh):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Ensure both lists are the same length
    if len(data_timestamp) != len(data_diff_kwh):
        raise ValueError("Mismatched data lengths between timestamps and kWh values")
    
    # Filter and sum kWh values for the current month
    total_energy_usage = sum(
        data_diff_kwh[i] for i in range(len(data_timestamp)) 
        if data_timestamp[i].month == current_month and data_timestamp[i].year == current_year
    )
    return total_energy_usage

def calculate_total_cost(total_energy_usage, kwh_rate):
    total_cost = total_energy_usage * float(kwh_rate)
    return total_cost

def calculate_ave_efficiency(latest_kvar_total, latest_kw_total):
    # Access the first element if these are tuples
    latest_kvar_total = latest_kvar_total[0] if isinstance(latest_kvar_total, tuple) else latest_kvar_total
    latest_kw_total = latest_kw_total[0] if isinstance(latest_kw_total, tuple) else latest_kw_total

    if latest_kvar_total == 0:
        return 0  # Avoid division by zero
    ave_efficiency = (latest_kw_total / latest_kvar_total) * 100
    return ave_efficiency

def calculate_prev_bill(data_timestamp, data_diff_kwh, kwh_rate):
    now = datetime.now()
    prev_month = (now.month - 1) if now.month > 1 else 12
    prev_year = now.year if now.month > 1 else now.year - 1  # Handle January case

    # Ensure data integrity
    if len(data_timestamp) != len(data_diff_kwh):
        raise ValueError("Mismatched data lengths between timestamps and kWh values")

    # Sum kWh for the previous month
    total_kwh_prev_month = sum(
        data_diff_kwh[i] for i in range(len(data_timestamp))
        if data_timestamp[i].month == prev_month and data_timestamp[i].year == prev_year
    )
    # Calculate the previous bill
    prev_bill = total_kwh_prev_month * float(kwh_rate)
    return prev_bill

def calculate_proj_usage(data_timestamp, data_diff_kwh):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Ensure both lists are the same length
    if len(data_timestamp) != len(data_diff_kwh):
        raise ValueError("Mismatched data lengths between timestamps and kWh values")
    
    # Group usage by day
    daily_usage = {}
    
    for i in range(len(data_timestamp)):
        if data_timestamp[i].month == current_month and data_timestamp[i].year == current_year:
            day = data_timestamp[i].day
            daily_usage[day] = daily_usage.get(day, 0) + data_diff_kwh[i]
    
    # Get total days in the current month
    total_days_in_month = calendar.monthrange(current_year, current_month)[1]
    
    # Calculate projected usage
    days_passed = len(daily_usage)
    
    if days_passed == 0:
        return 0  # Avoid division by zero if no data
    
    avg_daily_usage = sum(daily_usage.values()) / days_passed
    projected_usage = avg_daily_usage * total_days_in_month
    
    return projected_usage

def calculate_proj_cost(proj_usage, kwh_rate):
    proj_cost = proj_usage * float(kwh_rate)
    return proj_cost

def calculate_proj_savings(proj_cost, prev_bill):
    proj_savings = proj_cost - prev_bill
    return proj_savings

def calculate_curr_monthly_usage(total_energy_usage):
    curr_monthly_usage = total_energy_usage
    return curr_monthly_usage

def calculate_proj_monthly_usage(proj_usage):
    proj_monthly_usage = proj_usage
    return proj_monthly_usage

def calculate_ave_monthly_usage(data_timestamp, data_diff_kwh):
    if len(data_timestamp) != len(data_diff_kwh):
        raise ValueError("Mismatched data lengths between timestamps and kWh values")

    # Use a regular dictionary
    monthly_usage = {}

    for i in range(len(data_timestamp)):
        year_month = (data_timestamp[i].year, data_timestamp[i].month)
        
        # Check if the key exists before adding to it
        if year_month not in monthly_usage:
            monthly_usage[year_month] = 0.0
        
        monthly_usage[year_month] += data_diff_kwh[i]

    # Compute the average monthly usage
    if not monthly_usage:
        return 0  # Avoid division by zero if no data

    avg_monthly_usage = sum(monthly_usage.values()) / len(monthly_usage)
    
    return avg_monthly_usage
