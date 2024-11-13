import os
import random
import mysql.connector
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
from encryption import Encryption

class SerialKeyInserter:
    """
    SerialKeyInserter handles the generation and encrypted insertion of serial keys
    into a MySQL database over an SSH tunnel.
    """

    def __init__(self):
        """
        Initializes environment variables and default configuration for serial key insertion.
        """
        load_dotenv()
        self.ssh_host = os.getenv('SSH_HOST')
        self.ssh_user = os.getenv('SSH_USER')
        self.ssh_password = os.getenv('SSH_PASSWORD')
        self.ssh_pkey = os.getenv('SSH_PKEY')
        self.db_host = os.getenv('DB_HOST')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')
        self.db_port = int(os.getenv('DB_PORT', 3306))

        # Configurable parameters
        self.number_of_keys: int = 1
        self.product_id: int = 38
        self.activation_limit: int = 1
        self.status: str = 'available'
        self.validity: int = 0
        self.expire_date: str = None
        self.order_date: str = None
        self.uuid: str = None
        self.source: str = 'custom_source'
        self.created_date: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.separator: str = '-'
        self.blocks: int = 6
        self.digits_per_block: int = 4
        self.local_bind_port: int = 3308

    def generate_serial_key(self) -> str:
        """
        Generates a random serial key in the format XXXX-XXXX-XXXX-XXXX-XXXX.

        Returns:
            str: The generated serial key.
        """
        key = self.separator.join(
            ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=self.digits_per_block))
            for _ in range(self.blocks)
        )
        print(f"Generated serial key: {key}")
        return key

    def setup_ssh_tunnel(self) -> SSHTunnelForwarder:
        """
        Establishes an SSH tunnel to the database server.

        Returns:
            SSHTunnelForwarder: The SSH tunnel object.
        """
        print("Setting up SSH tunnel...")
        return SSHTunnelForwarder(
            (self.ssh_host, int(os.getenv('SSH_PORT', 22))),
            ssh_username=self.ssh_user,
            ssh_password=self.ssh_password,
            ssh_pkey=self.ssh_pkey,
            remote_bind_address=(self.db_host, self.db_port),
            local_bind_address=('127.0.0.1', self.local_bind_port)
        )

    def insert_serial_key(self, cursor, serial_key_encrypted: str):
        """
        Inserts a single encrypted serial key into the database.

        Args:
            cursor (mysql.connector.cursor): The MySQL database cursor.
            serial_key_encrypted (str): The encrypted serial key to insert.
        """
        insert_query = """
        INSERT INTO wp_serial_numbers (
            serial_key, product_id, activation_limit, activation_count,
            order_id, order_item_id, vendor_id, status, validity,
            expire_date, order_date, uuid, source, created_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            serial_key_encrypted, self.product_id, self.activation_limit, 0,
            0, 0, 0, self.status, self.validity,
            self.expire_date, self.order_date, self.uuid, self.source, self.created_date
        )
        cursor.execute(insert_query, data)
        print(f"Inserted serial key: {serial_key_encrypted}")

    def run(self):
        """
        Main function to set up the SSH tunnel, connect to the database,
        generate serial keys, encrypt them, and insert them into the database.
        """
        with self.setup_ssh_tunnel() as tunnel:
            tunnel.start()
            print("SSH tunnel established successfully.")
            print(f"SSH tunnel local bind port: {tunnel.local_bind_port}")

            try:
                connection = mysql.connector.connect(
                    user=self.db_user,
                    password=self.db_password,
                    host='127.0.0.1',
                    port=tunnel.local_bind_port,
                    database=self.db_name,
                    connection_timeout=10
                )
                print("Database connection established.")
                cursor = connection.cursor()

                for i in range(self.number_of_keys):
                    print(f"Inserting key {i + 1} of {self.number_of_keys}...")
                    serial_key_plain = self.generate_serial_key()
                    serial_key_encrypted = Encryption.encrypt(serial_key_plain)
                    self.insert_serial_key(cursor, serial_key_encrypted)

                connection.commit()
                print("Data insertion completed successfully.")
            except mysql.connector.Error as err:
                print("Database error:", err)
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
                print("Database connection closed.")

if __name__ == "__main__":
    inserter = SerialKeyInserter()
    inserter.run()
