import ascon
import subprocess
import os
from diffiehellman import DiffieHellman
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver



class Echo(LineReceiver):
    dh = DiffieHellman(group=14, key_bits=16)
    dh_public = dh.get_public_key()
    dh_shared = 0
    github_username = "fevgaray"
    github_password = "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"
    repository_path = "C:/Users/fevga/Desktop/Proy Apps/cripsens"
    
    commit_message = "Sensor data upload"

    nonce = b'qc\xb3\x0bJ\x92\xaf{\xee\r\x1a\x94d\x04o\xf8'
    associatedData = b"SENSOR"
    # Funcion para subir los datos a repo GitHub
    def git_push(self, username, password, repo_path, commit_message, data):
        try:        
            subprocess.check_output(['cd', repo_path], shell=True)
            os.chdir(repo_path)
            file_path = "stat4.txt"
            with open(file_path, "w") as file:
                file.write(data.decode())
            subprocess.check_output(['git', 'pull', '.'])
            subprocess.check_output(['git', 'add', '.'])
            subprocess.check_output(['git', 'commit', '-m', commit_message])
            subprocess.check_output(['git', 'push', '-u', f'https://{username}:{password}@github.com/{username}/cripsens.git', 'main', '--force'])
            

            print("Push successful.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.output}")

    def dataReceived(self, data):
        #print("receive:", data)
        #print("length:", len(data))
        if len(data) == 258:
            # print("SENT PUBLIC KEY :", self.dh_public)
            print("SENT SERVER PUBLIC KEY & RECEIVED SENSOR PUBLIC KEY")
            self.dh_shared = self.dh.generate_shared_key(data[:256])
            self.sendLine(self.dh_public)
        if len(data) == 36:
            print(data[:34])
            #print(self.dh_shared[:16])
            decrypted = ascon.ascon_decrypt(key=self.dh_shared[:16], nonce=self.nonce, associateddata=self.associatedData,
                                                ciphertext=data[:34], variant="Ascon-128")
            print("Decrypted :", decrypted)

            self.git_push(self.github_username, self.github_password, self.repository_path, self.commit_message, decrypted)

    
def main():
    f = Factory()
    f.protocol = Echo
    reactor.listenTCP(8000, f)
    reactor.run()


if __name__ == "__main__":
    main()

