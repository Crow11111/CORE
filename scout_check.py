import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.178.54', username='dreadnought', password='USsxrqqgF5eFqgaSUvU0in0RFTDsAK72LEIkn6gROJBTDRERgifAwuVw9qaPOahc', timeout=10)
cmds = ['cat /data/options.json', 'find /config /data -name "*adguard*" 2>/dev/null', 'ss -tlnp 2>/dev/null']
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd)
    print('===', cmd, '===')
    print(stdout.read().decode() or '(leer)')
client.close()
