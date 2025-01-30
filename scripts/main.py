from pymodbus.client import ModbusTcpClient
from calculations import perform_all_calculations
from update_db import fetch_latest_measurements, update_status_header, update_pred_maintenance, update_stats_panel, fetch_user_inputs, fetch_kwh_data 
from datetime import datetime
import psycopg2, struct, schedule, time, json, concurrent.futures

# Load meter configuration
with open('meters_config.json', 'r') as f:
    meters_config = json.load(f)

# Database connection
def conn_db():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password",
        port=5433
    )

# Define the function
def read_and_store_data(meter):
    meter_id = meter['meter_id']  # Get meter ID from the passed meter object

    with conn_db() as conn:
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
            #print(f"Reading {key} from register {address} for meter {meter['meter_id']}...")
            response = client.read_holding_registers(address=address, count=2)
            if not response.isError():
                data[key] = read_float32(response.registers)
                print(f"Data for {key}: {data[key]}")
            else:
                data[key] = None
                print(f"Error reading data for {key}.")
        except Exception as e:
            print(f"Exception reading {key}: {e}")

    # Prepare values to insert
    insert_values = (
        datetime.now(), meter_id,
    data["v_ab"], data["v_bc"], data["v_ca"],
    data["v_a"], data["v_b"], data["v_c"],
    data["i_a"], data["i_b"], data["i_c"],
    data["freq"], data["pf_a"], data["pf_b"], data["pf_c"],
    data["kw_a"], data["kw_b"], data["kw_c"],
    data["kw_total"], data["kvar_a"], data["kvar_b"], data["kvar_c"],
    data["kvar_total"], data["kva_a"], data["kva_b"], data["kva_c"],
    data["kva_total"], data["kWh"], data["kvarh"], data["kvah"],
    data["thd_v_ab"], data["thd_v_bc"], data["thd_v_ca"],
    data["thd_v_a"], data["thd_v_b"], data["thd_v_c"],
    data["thd_i_a"], data["thd_i_b"], data["thd_i_c"]
    )

    # Insert data into live_measurements table
    insert_query = """
        INSERT INTO live_measurements (
            timestamp, meter_id, v_ab, v_bc, v_ca, v_a, v_b, v_c,
            i_a, i_b, i_c, freq, pf_a, pf_b, pf_c, kw_a, kw_b, kw_c,
            kw_total, kvar_a, kvar_b, kvar_c, kvar_total, kva_a, kva_b, kva_c, kva_total,
            kwh, kvarh, kvah, thd_v_ab, thd_v_bc, thd_v_ca, thd_v_a, thd_v_b, thd_v_c, thd_i_a, thd_i_b, thd_i_c
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    # Execute the insert query with the values
    print("Inserting data into the database...")
    cursor.execute(insert_query, insert_values)

    inserted_timestamp_query = """
        SELECT timestamp
        FROM live_measurements
        WHERE meter_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """
    cursor.execute(inserted_timestamp_query, (meter_id,))
    inserted_timestamp_row = cursor.fetchone()

    if inserted_timestamp_row is None:
        print(f"No inserted timestamp found for meter_id {meter_id}")
        return  # Gracefully exit or handle as necessary

    inserted_timestamp = inserted_timestamp_row[0]

    # Fetch the previous kWh value for the same meter
    prev_kwh_query = """
        SELECT kwh
        FROM live_measurements
        WHERE meter_id = %s AND timestamp < %s
        ORDER BY timestamp DESC
        LIMIT 1
    """
    cursor.execute(prev_kwh_query, (meter_id, inserted_timestamp))
    prev_kwh_row = cursor.fetchone()

    # Calculate diff_kwh if there is a previous kWh value
    diff_kwh = None
    if prev_kwh_row:
        prev_kwh = prev_kwh_row[0]
        diff_kwh = data["kWh"] - prev_kwh
        print(f"Calculated diff_kwh for meter_id {meter_id}: {diff_kwh}")

        # Update the new row with the calculated diff_kwh
        update_query = """
            UPDATE live_measurements
            SET diff_kwh = %s
            WHERE meter_id = %s AND timestamp = %s
        """
        cursor.execute(update_query, (diff_kwh, meter_id, inserted_timestamp))
        print(f"Updated diff_kwh for meter_id {meter_id} with timestamp {inserted_timestamp}")
    else:
        print(f"No previous kWh value found for meter_id {meter_id} before {inserted_timestamp}")

    # Commit transaction and close connections
    conn.commit()
    print(f"Data for meter {meter['meter_id']} inserted successfully. Updated diff_kwh: {diff_kwh}")
    cursor.close()
    conn.close()
    client.close()
    print("Connection closed.")

# Main function to fetch data from all meters simultaneously
def fetch_all_meters_data():
    try:
        # Use ThreadPoolExecutor to manage multiple meter readings concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit tasks to the executor for each meter
            future_to_meter = {executor.submit(read_and_store_data, meter): meter for meter in meters_config['meters']}

            # Safely handle database operations separately to avoid interruptions
            try:
                # Get the database connection and perform operations
                with conn_db() as conn:

                    # Fetch the latest measurements
                    latest_measurement = fetch_latest_measurements(conn)
                    user_inputs = fetch_user_inputs(conn)
                    #live_measurements = fetch_live_measurements(conn)
                    kwh_data = fetch_kwh_data(conn)
                    #last_two_kwh = fetch_last_two_kwh_rows(conn)

                    # Perform all necessary calculations based on the latest measurements
                    calculations = perform_all_calculations(latest_measurement, user_inputs, kwh_data)

                    # Update tables with the calculations
                    for meter in meters_config['meters']:
                        meter_id = meter['meter_id']
                        update_status_header(conn, meter_id, calculations)
                        update_pred_maintenance(conn, meter_id, latest_measurement)
                        update_stats_panel(conn, meter_id, calculations)
            except Exception as e:
                print(f"Error in database operations: {e}")

            # Wait for all threads to complete their tasks
            for future in concurrent.futures.as_completed(future_to_meter):
                meter = future_to_meter[future]
                try:
                    # Execute the read_and_store_data function for each meter
                    future.result()
                except Exception as e:
                    print(f"Error reading from meter {meter['meter_id']}: {e}")

    except Exception as e:
        print(f"Critical error in fetch_all_meters_data: {e}")

# Ensure that the code only runs if executed directly, not when imported
if __name__ == "__main__":
    # Schedule the fetching of data every minute
    schedule.every(1).minute.do(fetch_all_meters_data)

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check if a job is due every second


