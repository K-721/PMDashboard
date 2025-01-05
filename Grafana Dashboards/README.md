## Guide to Import Grafana Dashboard JSON File to Localhost

This guide provides step-by-step instructions to import a Grafana dashboard JSON file into a Grafana instance running on your localhost.

---

### **Prerequisites**

1. **Grafana Installed on Localhost**
   - Download and install Grafana from [Grafana's official website](https://grafana.com/grafana/download).

2. **Admin Access**
   - Ensure you have administrator privileges to manage Grafana dashboards.

3. **Dashboard JSON File**
   - Obtain the JSON file for the dashboard you want to import.  
     The dashboard's JSON files are located in the same folder as this file.

---

### **Steps to Import the Dashboard JSON File**

#### **1. Access Grafana**

1. Open a web browser.  
2. Navigate to `http://localhost:3000`.  
3. Log in using your Grafana credentials:  
   - Default Username: `admin`  
   - Default Password: `admin` (you may need to change this upon first login).

---

#### **2. Navigate to the Import Page**

1. In the left-hand sidebar, click the **“+ (Create)”** icon.  
2. Select **“Import”** from the dropdown menu.

---

#### **3. Upload the JSON File**

1. Click the **“Upload JSON File”** button.  
2. Locate and select the JSON file for the dashboard you want to import.

---

#### **4. Configure Data Sources**

1. Once the JSON file is loaded, Grafana will prompt you to select or configure the data source.  
2. Choose an existing data source from the dropdown menu, or:  
   - Navigate to **Settings > Data Sources**.  
   - Add a new data source (e.g., PostgreSQL, Prometheus, InfluxDB).  
   - Return to the import page and select the newly added data source.

To replicate the existing dashboard, here are my connection settings:  
- **Host URL**: `localhost:5433` (Note: I changed my port number to `5433` during local installation of PSQLv17 since the Docker-based TimescaleDB uses port `5432`).  
- **Database Name**: `postgres`  
- **Username**: `postgres`  
- **Password**: `password`  
- **TLS/SSL Mode**: `disable`  
- The rest are default settings.  

Click **Save & Test**.

---

### **Verify the Imported Dashboard**

1. Go to **Dashboards > Manage** in the left sidebar.  
2. Open the imported dashboard.  
3. Check if all panels are displaying data correctly.

---

### **Troubleshooting**

- **Missing Data Source**: Ensure the required data source is properly configured in Grafana.  
- **Dashboard Not Displaying Data**: Verify the data source connection and ensure the database contains valid data.  
  - If the error details say "Datasource `<randomletters>` was not found," click the menu icon on each panel's top right side, select **Edit**, then click **Run Query**. You can also check the "DBImport" video inside the same folder.
- **Connection Issues**: Check the network access between Grafana and the data source.

---

