import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    server=os.getenv("DB_SERVER")
    database=os.getenv("DB_NAME")
    driver=os.getenv("DB_DRIVER")
    
    trusted=os.getenv("DB_TRUSTED_CONNECTION","yes")
    
    encrypt=os.getenv("DB_ENCRYPT","yes")
    
    trust_certificate=os.getenv("DB_TRUST_SERVER_CERTIFICATE","yes")
    
    connection_string=(
        f"DRIVER={{{driver}}};"
        f"SERVER={{{server}}};"
        f"DATABASE={{{database}}};"
        f"Trusted_Connection={{{trusted}}};"
        f"Encrypt={{{encrypt}}};"
        f"TrustServerCertificate={{{trust_certificate}}};"
    )
    
    connection=pyodbc.connect(
        connection_string,
        timeout=10
    )
    
    return connection

if __name__=="__main__":
    try:
        connection=get_connection()
        
        cursor=connection.cursor()
        
        cursor.execute(
            "SELECT @@SERVERNAME, DB_NAME()"
        )
        
        result=cursor.fetchone()
        
        print("SQL Server Connection Successful")
        
        print("Server :",result[0])
        print("Database :",result[1])
        
        cursor.close()
        connection.close()
        
    except Exception as error:
        print("Database Connection Failed.")
        
        print("Error: ",error)