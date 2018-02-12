# Import
import string
import sys

# Get Python version
ver = sys.version_info[0]
#print('Version: '+str(ver))
if ver==2:  # Python 2
    import urllib    
else:       # Python 3+
    import urllib.request, urllib.parse, urllib.error
    #import socket

if ver==2:  # Python 2

    def cmd(server, app, aline, disp=True):
        '''Send a request to the server \n \
           server = address of server \n \
           app      = application name \n \
           aline  = line to send to server \n \
           disp = Print output \n'''
        try:
            # Web-server URL address
            url_base = string.strip(server) + '/online/apm_line.php'
            app = app.lower()
            app.replace(" ", "")
            params = urllib.urlencode({'p': app, 'a': aline})
            f = urllib.urlopen(url_base, params)
            # Stream solution output
            if(aline=='solve'):
                line = ''
                while True:
                    char = f.read(1)
                    if not char:
                        break
                    elif char == '\n':
                        if disp: 
                            print(line)
                        line = ''
                    else:
                        line += char
            # Send request to web-server
            response = f.read()
        except:
            response = 'Failed to connect to server'
        return response

    def get_ip(server):
        '''Get current IP address \n \
           server   = address of server'''
        # get ip address for web-address lookup
        url_base = string.strip(server) + '/ip.php'
        f = urllib.urlopen(url_base)
        ip = string.strip(f.read())
        return ip

    def get_file(server,app,filename):
        '''Retrieve any file from web-server\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        try:
            # Web-server URL address
            app = app.lower()
            app.replace(" ","")
            url = string.strip(server) + '/online/' + ip + '_' + app + '/' + filename
            f = urllib.urlopen(url)
            # Send request to web-server
            file = f.read()
            # Write the file
            #fh = open(filename,'w')
            #fh.write(file.replace('\r',''))
            #fh.close()
            return (file)
        except:
            print('Could not retrieve ' + filename + ' from server')
            return []

else:       # Python 3+
    
    def cmd(server,app,aline, disp=True):
        '''Send a request to the server \n \
           server = address of server \n \
           app      = application name \n \
           aline  = line to send to server \n \
           disp = Print output \n'''
        try:
            # Web-server URL address
            url_base = server.strip() + '/online/apm_line.php'
            app = app.lower()
            app.replace(" ","")
            params = urllib.parse.urlencode({'p':app,'a':aline})
            en_params = params.encode()
            f = urllib.request.urlopen(url_base,en_params)
            # Stream solution output
            if(aline=='solve'):
                line = ''
                while True:
                    en_char = f.read(1)
                    char = en_char.decode()
                    if not char:
                        break
                    elif char == '\n':
                        if disp:
                            print(line)
                        line = ''
                    else:
                        line += char
            # Send request to web-server
            en_response = f.read()
            response = en_response.decode()
        except:
            response = 'Failed to connect to server'
        return response

    def get_ip(server):
        '''Get current IP address \n \
           server   = address of server'''
        # get ip address for web-address lookup
        url_base = server.strip() + '/ip.php'
        f = urllib.request.urlopen(url_base)
        fip = f.read()
        ip = fip.decode().strip()
        return ip

    def get_file(server,app,filename):
        '''Retrieve any file from web-server\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        try:
            # Web-server URL address
            app = app.lower()
            app.replace(" ","")
            url = server.strip() + '/online/' + ip + '_' + app + '/' + filename
            f = urllib.request.urlopen(url)
            # Send request to web-server
            file = f.read()
            # Write the file
            #fh = open(filename,'w')
            #en_file = file.decode().replace('\r','')
            #fh.write(en_file)
            #fh.close()
            return (file)
        except:
            print('Could not retrieve ' + filename + ' from server')
            return []
            


