from pymodbus.client import ModbusTcpClient
import psycopg2
from datetime import datetime
import struct
import schedule  # Import the schedule module
import time  # To keep the script running

# Define the function
def read_and_store_data():

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
    client = ModbusTcpClient('192.168.68.221', port=502, timeout=99999)
    register_mapping = {
        "current_a": 3000-1,
        "voltage_ab": 3020-1,
        "frequency": 3110-1,
        "power_factor_a": 3078-1,
        "active_power_a": 3054-1,
        "active_power_total": 3060-1,
        "reactive_power_a": 3062-1,
        "reactive_power_total": 3068-1,
        "apparent_power_a": 3070-1,
        "apparent_power_total": 3076-1,
        "thd_current_a": 21300-1,
        "thd_voltage_ll": 21328-1,
        "active_energy_delivered": 2700-1,
        "reactive_energy_delivered": 2708-1,
        "apparent_energy_delivered": 2716-1
    }

    # Read data from power meter
    data = {}
    for key, address in register_mapping.items():
        print(f"Reading data for {key} from register {address}...")
        response = client.read_holding_registers(address=address, count=2)
        if not response.isError():
            data[key] = read_float32(response.registers)
            print(f"Data for {key}: {data[key]}")
        else:
            data[key] = None  # Handle error appropriately
            print(f"Error reading data for {key}.")

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
        datetime.now(), 1,  # Assuming meter_id is 1; replace as needed
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
    print("Data inserted successfully.")
    cursor.close()
    conn.close()
    client.close()
    print("Connection closed.")


# Schedule the task
schedule.every(1).minutes.do(read_and_store_data)

# Keep running the scheduled task
while True:
    schedule.run_pending()
    time.sleep(1)