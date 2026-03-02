import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.178.54', username='dreadnought', password='USsxrqqgF5eFqgaSUvU0in0RFTDsAK72LEIkn6gROJBTDRERgifAwuVw9qaPOahc', timeout=10)
cmds = ['cat /data/options.json 2>&1', 'netstat -tln 2>/dev/null', 'ls -la /config 2>/dev/null', 'ls /usr/share/hassio/addons 2>/dev/null']
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    print('===', cmd[:50], '===')
    print(out or err or '(leer)')
client.close()
