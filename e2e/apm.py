# Import
import string
import sys

# Get Python version
ver = sys.version_info[0]
#print('Version: '+str(ver))
if ver==2:  # Python 2
    import urllib    
    import urllib2
else:       # Python 3+
    import urllib.request, urllib.parse, urllib.error
    #import socket


def _request(url, data=None):
    # Identify all requests, including IP lookup and result downloads. Some
    # server firewalls reject urllib's default Python User-Agent.
    headers = {'User-Agent': 'GEKKO'}
    if ver == 2:
        return urllib2.urlopen(urllib2.Request(url, data, headers))
    return urllib.request.urlopen(urllib.request.Request(url, data, headers))


if ver==2:  # Python 2

    def cmd(server, app, aline, disp=True, debug=1):
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
            f = _request(url_base, params)
            # initialize apm_error recording
            record_error = False
            apm_error = ''
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
                        if debug >= 1:
                            # Start recording output if error is detected
                            if '@error' in line:
                                record_error = True
                            if record_error:
                                apm_error+= line + '\n'
                        line = ''
                    else:
                        line += char
            # Send request to web-server
            if apm_error != '': # check if any apm errors were found
                response = apm_error
            else:
                response = f.read()
        except IOError as exc:
            raise IOError('APMonitor command failed at {0}: {1}'.format(url_base, exc))
        return response
    

    def get_ip(server):
        '''Get current IP address \n \
           server   = address of server'''
        # get ip address for web-address lookup
        url_base = string.strip(server) + '/ip.php'
        f = _request(url_base)
        ip = string.strip(f.read())
        return ip

    def get_file(server,app,filename):
        '''Retrieve any file from web-server\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        
        # Web-server URL address
        app = app.lower()
        app.replace(" ","")
        url = string.strip(server) + '/online/' + ip + '_' + app + '/' + filename
        f = _request(url)
        # Send request to web-server
        file = f.read()
        # Write the file
        #fh = open(filename,'w')
        #fh.write(file.replace('\r',''))
        #fh.close()
        return (file)

else:       # Python 3+
    
    def cmd(server,app,aline, disp=True, debug=1):
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
            f = _request(url_base, en_params)
            # initialize apm_error recording
            record_error = False
            apm_error = ''
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
                        if debug >= 1:
                            # Start recording output if error is detected
                            if '@error' in line:
                                record_error = True
                            if record_error:
                                apm_error+= line + '\n'
                        line = '' # reset line
                    else:
                        line += char
            if apm_error != '': # check if any apm errors were found
                response = apm_error
            else:
                # Send request to web-server
                en_response = f.read()
                response = en_response.decode()
        except IOError as exc:
            raise IOError('APMonitor command failed at {0}: {1}'.format(url_base, exc))
        return response

    def get_ip(server):
        '''Get current IP address \n \
           server   = address of server'''
        # get ip address for web-address lookup
        url_base = server.strip() + '/ip.php'
        f = _request(url_base)
        fip = f.read()
        ip = fip.decode().strip()
        return ip

    def get_file(server,app,filename):
        '''Retrieve any file from web-server\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        
        # Web-server URL address
        app = app.lower()
        app.replace(" ","")
        url = server.strip() + '/online/' + ip + '_' + app + '/' + filename
        f = _request(url)
        # Send request to web-server
        file = f.read()
        # Write the file
        #fh = open(filename,'w')
        #en_file = file.decode().replace('\r','')
        #fh.write(en_file)
        #fh.close()
        return (file)
            


