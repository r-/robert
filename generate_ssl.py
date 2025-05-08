import subprocess
import os
import sys

def generate_self_signed_cert(cert_dir='certs', cert_name='server'):
    # Ensure the directory exists
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    cert_file = os.path.join(cert_dir, f"{cert_name}.crt")
    key_file = os.path.join(cert_dir, f"{cert_name}.key")

    # Check if the certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Certificate and key already exist at {cert_dir}.")
        return

    # Command to generate the certificate and key
    openssl_command = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', key_file,
        '-out', cert_file, '-days', '365', '-nodes', 
        '-subj', '/C=US/ST=State/L=City/O=Company/OU=IT/CN=localhost'
    ]
    
    try:
        # Run OpenSSL command
        print("Generating self-signed certificate and private key...")
        subprocess.run(openssl_command, check=True)
        print(f"Certificate and key saved to {cert_dir}.")
    except subprocess.CalledProcessError as e:
        print(f"Error during certificate generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the function to generate the certificate and key
    generate_self_signed_cert(cert_dir='certs', cert_name='server')
