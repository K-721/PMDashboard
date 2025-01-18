from pymodbus.client import ModbusTcpClient
import psycopg2
from datetime import datetime
import struct
import schedule  # Import the schedule module
import time  # To keep the script running
import json
import concurrent.futures

# Load meter configuration
with open('meters_config.json', 'r') as f:
    meters_config = json.load(f)

# Define the function
def read_and_store_data(meter):
    meter_id = meter['meter_id']  # Get meter ID from the passed meter object

    # Database connection
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password",
        port=5433
    )
    cursor = conn.cursor()

    # Function to read float32 from the registers
    def read_float32(response_registers):
        combined = (response_registers[0] << 16) | response_registers[1]
        return struct.unpack('>f', combined.to_bytes(4, byteorder='big'))[0]

    # Modbus client
    client = ModbusTcpClient(meter['ip_address'], port=meter['port'], timeout=99999)

    # Read data from power meter
    data = {}
    for key, address in meter['registers'].items():
        try:
            print(f"Reading {key} from register {address} for meter {meter['meter_id']}...")
            response = client.read_holding_registers(address=address, count=2)
            if not response.isError():
                data[key] = read_float32(response.registers)
                print(f"Data for {key}: {data[key]}")
            else:
                data[key] = None
                print(f"Error reading data for {key}.")
        except Exception as e:
            print(f"Exception reading {key}: {e}")

    # Duplicate voltage and current for each phase
    data["voltage_bc"] = data.get("voltage_ab", None)
    data["voltage_ca"] = data.get("voltage_ab", None)
    data["voltage_a"] = data.get("voltage_ab", None)
    data["voltage_b"] = data.get("voltage_ab", None)
    data["voltage_c"] = data.get("voltage_ab", None)

    data["current_b"] = data.get("current_a", None)
    data["current_c"] = data.get("current_a", None)

    # Duplicate power factors for each phase
    data["power_factor_b"] = data.get("power_factor_a", None)
    data["power_factor_c"] = data.get("power_factor_a", None)

    # Duplicate active power for each phase
    data["active_power_b"] = data.get("active_power_a", None)
    data["active_power_c"] = data.get("active_power_a", None)

    # Duplicate reactive power for each phase
    data["reactive_power_b"] = data.get("reactive_power_a", None)
    data["reactive_power_c"] = data.get("reactive_power_a", None)

    # Duplicate apparent power for each phase
    data["apparent_power_b"] = data.get("apparent_power_a", None)
    data["apparent_power_c"] = data.get("apparent_power_a", None)

    # Prepare values to insert
    insert_values = (
        datetime.now(), meter_id,
        data["voltage_ab"], data["voltage_bc"], data["voltage_ca"],
        data["voltage_a"], data["voltage_b"], data["voltage_c"],
        data["current_a"], data["current_b"], data["current_c"],
        data["frequency"], data["power_factor_a"], data["power_factor_b"], data["power_factor_c"],  # Assuming pf_a for all phases
        data["active_power_a"], data["active_power_b"], data["active_power_c"], data["active_power_total"],
        data["reactive_power_a"], data["reactive_power_b"], data["reactive_power_c"], data["reactive_power_total"],
        data["apparent_power_a"], data["apparent_power_b"], data["apparent_power_c"], data["apparent_power_total"],
        data["active_energy_delivered"], data["reactive_energy_delivered"], data["apparent_energy_delivered"], # Placeholder for kWh, kvarh, kvah
        data["thd_voltage_ll"], data["thd_voltage_ll"], data["thd_voltage_ll"],
        data["thd_voltage_ll"], data["thd_voltage_ll"], data["thd_voltage_ll"],
        data["thd_current_a"], data["thd_current_a"], data["thd_current_a"]
    )

    # Log the values to be inserted
    # print("Inserting the following data into the database:")
    # for idx, field in enumerate([
    #     "timestamp", "meter_id", "v_ab", "v_bc", "v_ca", "v_a", "v_b", "v_c",
    #     "i_a", "i_b", "i_c", "freq", "pf_a", "pf_b", "pf_c", "kw_a", "kw_b", "kw_c",
    #     "kw_total", "kvar_a", "kvar_b", "kvar_c", "kvar_total", "kva_a", "kva_b",
    #     "kva_c", "kva_total", "kWh", "kvarh", "kvah", "thd_v_ab", "thd_v_bc",
    #     "thd_v_ca", "thd_v_a", "thd_v_b", "thd_v_c", "thd_i_a", "thd_i_b", "thd_i_c"
    # ]):
    #     print(f"{field}: {insert_values[idx]}")

    # Insert data into live_measurements table
    insert_query = """
        INSERT INTO live_measurements (
            timestamp, meter_id, v_ab, v_bc, v_ca, v_a, v_b, v_c,
            i_a, i_b, i_c, freq, pf_a, pf_b, pf_c, kw_a, kw_b, kw_c,
            kw_total, kvar_a, kvar_b, kvar_c, kvar_total, kva_a, kva_b, kva_c, kva_total,
            kWh, kvarh, kvah, thd_v_ab, thd_v_bc, thd_v_ca, thd_v_a, thd_v_b, thd_v_c, thd_i_a, thd_i_b, thd_i_c
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    # Execute the insert query with the values
    print("Inserting data into the database...")
    cursor.execute(insert_query, insert_values)

    # Commit transaction and close connections
    conn.commit()
    print(f"Data for meter {meter['meter_id']} inserted successfully.")
    cursor.close()
    conn.close()
    client.close()
    print("Connection closed.")

# Main function to fetch data from all meters simultaneously
def fetch_all_meters_data():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_meter = {executor.submit(read_and_store_data, meter): meter for meter in meters_config['meters']}
        
        for future in concurrent.futures.as_completed(future_to_meter):
            try:
                future.result()  # No need to print anything as the function already logs success
            except Exception as e:
                meter = future_to_meter[future]
                print(f"Error reading from meter {meter['meter_id']}: {e}")

# Schedule the fetching of data every minute
schedule.every(1).minute.do(fetch_all_meters_data)

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(1)  # Check if a job is due every second