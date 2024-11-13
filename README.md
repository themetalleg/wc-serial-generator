# WooCommerce Serial Numbers Inserter

This project automates the insertion of encrypted serial numbers into the WooCommerce Serial Numbers plugin database. By leveraging SSH tunneling for secure database access, it ensures that serial keys are encrypted according to WooCommerce's standards before being stored in the database.

## Prerequisites

- **Python 3.x**
- **MySQL Connector** (`mysql-connector-python`)
- **Cryptographic Library** (`pycryptodome`)
- **Environment Management** (`python-dotenv`)
- **SSH Tunneling** (`sshtunnel`)

You can install the required packages with:

```bash
pip install mysql-connector-python pycryptodome python-dotenv sshtunnel
```

## Project Overview

This project consists of two main components:
1. **Serial Key Inserter**: A script that generates serial numbers, encrypts them, and inserts them into the WooCommerce database.
2. **Encryption Utility**: Provides AES-256 encryption for serial numbers to match WooCommerce’s security requirements.

## Setup

### Step 1: Configure the `.env` File

1. Copy the provided `env.example` template to a new file named `.env`.
2. Fill in your environment-specific values, including database credentials, SSH access details, and encryption settings. Below is a brief guide on each setting:

#### Finding Your Encryption Key and Initialization Vector

- **Encryption Key**: In your WordPress database, run the following SQL query to retrieve your WooCommerce Serial Numbers encryption key:

  ```sql
  SELECT * FROM [wordpressdatabase].wp_options WHERE option_name = "wcsn_pkey";
  ```

  Replace `[wordpressdatabase]` with your actual database name.

- **Initialization Vector**: The WooCommerce Serial Numbers plugin stores the initialization vector in its PHP code. It can be found in the following file:

  ```
  Wordpress/wp-content/plugins/wc-serial-numbers/src/Encryption.php
  ```

  Look for the following constant definition:

  ```php
  const INITVECTOR = '[vector]';
  ```

### Step 2: Running the Script

1. After configuring the `.env` file, you can run the script to insert serial numbers into the WooCommerce Serial Numbers plugin database.

   ```bash
   python serial_key_inserter.py
   ```

2. The script will:
   - Generate a random serial key in the format `XXXX-XXXX-XXXX-XXXX-XXXX`.
   - Encrypt the serial key using AES-256-CBC, matching WooCommerce’s encryption standard.
   - Insert the encrypted serial key into the `wp_serial_numbers` table in the WooCommerce database.

### Script Output

As the script runs, it will display log messages detailing each step:
- **SSH Tunnel Setup**: Confirmation of SSH tunnel establishment to the MySQL database.
- **Database Connection**: Messages indicating successful database connection.
- **Serial Key Generation and Insertion**: Logs of generated serial keys, encryption steps, and successful insertion.

## File Structure

```plaintext
.
├── serial_key_inserter.py       # Main script to insert serial keys
├── encryption.py                # Encryption utility for AES-256-CBC
├── .env                         # Environment variables for database, SSH, and encryption
└── README.md                    # Documentation for the project
```

## Troubleshooting

### Common Issues

1. **SSH Connection Fails**: Verify SSH credentials and ensure the SSH server allows port forwarding.
2. **Database Connection Refused**: Confirm that MySQL allows connections on `127.0.0.1:3306` and that the firewall permits this traffic.
3. **Encryption Key Errors**: Double-check that the encryption key and IV match those in your WooCommerce settings.

### Logs and Debugging

The script provides detailed log output. If any step fails, examine the error messages for hints on resolving the issue. Check for:
- SSH connection errors
- MySQL access permissions
- Misconfiguration in `.env` values

## License

This project is distributed under an open-source license, allowing free use and modification for those integrating serial numbers into WooCommerce.

## Disclaimer

Please handle sensitive information such as SSH and database credentials with care. Use this script at your own risk and verify its compatibility with your WooCommerce environment before using it in a production setting.