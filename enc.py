import os
import base64
import zipfile
import getpass
import shutil
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
def get_password_only_fernet(password: bytes) -> Fernet:
    """Hashes the password to exactly 32 bytes so Fernet can use it directly as a key."""
    digest = hashes.Hash(hashes.SHA256())
    digest.update(password)
    hashed_key = digest.finalize()
    
    # Fernet requires the 32-byte key to be urlsafe base64 encoded
    fernet_key = base64.urlsafe_b64encode(hashed_key)
    return Fernet(fernet_key)

def encrypt_file(file_path, password):
    fernet = get_password_only_fernet(password.encode())
    
    with open(file_path, "rb") as f:
        data = f.read()
        
    encrypted_data = fernet.encrypt(data)
    
    return encrypted_data
    # Save only the encrypted output
    #with open(file_path + ".enc", "wb") as f:
    #    f.write(encrypted_data)
    print(f"\n🔒 Success! Encrypted to {file_path}.enc")

def decrypt_file(file_path, password):
    fernet = get_password_only_fernet(password.encode())
    
    with open(file_path, "rb") as f:
        encrypted_data = f.read()
        
    try:
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data
        #output_path = file_path.replace(".enc", "_restored")
        #with open(output_path, "wb") as f:
        #    f.write(decrypted_data)
        #print(f"\n🔓 Success! Decrypted to {output_path}")
    except Exception:
        print("\n❌ Decryption failed! Wrong password or corrupted file.")

def decrypt_zip_to_custom_folder(zip_path, password, target_folder_name):
    fernet = get_password_only_fernet(password.encode())
    
    # 1. Set the exact target path: download/your_folder_name
    final_output_dir = os.path.join("download", target_folder_name)
    
    # 2. Clean wipe ONLY this specific subfolder if it already exists
    if os.path.exists(final_output_dir):
        shutil.rmtree(final_output_dir)
    
    # Create the target subfolder fresh
    os.makedirs(final_output_dir, exist_ok=True)
        
    # 3. Setup a temporary directory for raw extraction
    temp_extract_dir = "temp_zip_extract"
    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
        
    # 4. Extract the raw encrypted zip contents
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)
        
    # 5. Walk through and decrypt everything into the custom folder
    for root, dirs, files in os.walk(temp_extract_dir):
        for file in files:
            src_encrypted_path = os.path.join(root, file)
            
            # Keep original relative layout
            relative_path = os.path.relpath(src_encrypted_path, temp_extract_dir)
            
            # Strip out .enc file extensions if present
            if relative_path.endswith(".enc"):
                clean_relative_path = relative_path[:-4]
            else:
                clean_relative_path = relative_path
                
            # Place it directly inside download/your_folder_name/
            dest_decrypted_path = os.path.join(final_output_dir, clean_relative_path)
            
            # Recreate nested directories if any
            os.makedirs(os.path.dirname(dest_decrypted_path), exist_ok=True)
            
            try:
                with open(src_encrypted_path, "rb") as f:
                    encrypted_data = f.read()
                    
                decrypted_data = fernet.decrypt(encrypted_data)
                
                with open(dest_decrypted_path, "wb") as f:
                    f.write(decrypted_data)
                    
            except Exception:
                print(f"❌ Failed to decrypt file: {relative_path}")
                shutil.rmtree(temp_extract_dir)
                return False

    # 6. Final cleanup of the temp zone
    shutil.rmtree(temp_extract_dir)
    print(f"\n🔓 Success! All files restored to: {final_output_dir}")
    return True
