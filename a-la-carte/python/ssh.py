"""
Basic SSH implementation with paramiko.
"""

import os
import paramiko
import socket

from typing import List, Set, Dict, Tuple, Optional

import logging
logging.basicConfig(format='%(name)s[%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

class ClientSSH:
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if not os.path.exists(f'{os.environ.get("HOME")}/.ssh/beta.pub'):
            raise Exception('Aborting. ~/.ssh/beta.pub does not exist.')

        try:
            self.client.connect(
                    self.ip_address, 
                    username='root', 
                    key_filename=f'{os.environ.get("HOME")}/.ssh/beta.pub',
                    timeout=1,
                    banner_timeout=5,
                    auth_timeout=1,
                    )
        except FileNotFoundError:
            raise Exception(f'The cert file {cert_path} does not exist!')
        except paramiko.ssh_exception.AuthenticationException:
            raise Exception(f'Authentication failed. Not a Density Unit?')
        except paramiko.ssh_exception.NoValidConnectionsError:
            raise Exception(f'No valid connection. Is this the right IP?')
        except socket.timeout:
            raise Exception(f'Unit is rebooting?')
        except Exception as e:
            raise e
                
    def __del__(self):
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()

    def send_command(self, command: str) -> Tuple[str, str]:
        stdin, stdout, stderr = self.client.exec_command(command)
        status = stdout.channel.recv_exit_status() 
        stdout = ''.join(map(str, stdout))
        stderr = ''.join(map(str, stderr))
        return {
                'status': status,
                'stdout': stdout,
                'stderr': stderr,
                }

    def copy_file_to_unit(self, local_filepath, remote_filepath):
        logger.info(f'Copying {local_filepath} to {remote_filepath}...')
        ftp_client = self.client.open_sftp()
        ftp_client.put(local_filepath, remote_filepath)
        ftp_client.close()
    
    def copy_file_from_unit(self, local_filepath, remote_filepath):
        logger.info(f'Copying to {local_filepath} from {remote_filepath}...')
        ftp_client = self.client.open_sftp()
        ftp_client.get(remote_filepath, local_filepath)
        ftp_client.close()

if __name__ == "__main__":
    with ClientSSH('192.168.68.147') as client:
        result = client.send_command('cat /etc/os-release')
