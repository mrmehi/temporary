import subprocess
import os
import random
import string
from django.http import HttpResponseRedirect, HttpResponseNotFound
import traceback
import threading

# generate dict with scriptId and script name pairs
scriptId_to_scriptName = {
    1: 'function generate_google_dorks',
    2: __file__.replace("utils.py", '') + '../scripts/subfinder.sh',
    3: __file__.replace("utils.py", '') + '../scripts/nikto.sh',
    4: __file__.replace("utils.py", '') + '../scripts/wpscan.sh',
    5: __file__.replace("utils.py", '') + '../scripts/nmap.sh',
    6: __file__.replace("utils.py", '') + '../scripts/sqlmap.sh',
    7: __file__.replace("utils.py", '') + '../scripts/dirsearch.sh',
    8: __file__.replace("utils.py", '') + '../scripts/sslmap.sh',
    9: __file__.replace("utils.py", '') + '../scripts/joomscan.sh',
}


def generate_empty_file(save_path):
    file_name = generate_random_file_name()
    with open(save_path + file_name, 'w') as f:
        pass
    return save_path + file_name


def generate_random_file_name():
    # generate random file name with 20 characters
    return ''.join(random.choice(string.ascii_lowercase) for i in range(20))


def copy_and_save_file(file, path):
    uploaded_file = file
    save_path = path
    file_name = generate_random_file_name()

    with open(save_path + file_name, 'wb') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return save_path + file_name


def generate_google_dorks(script_parameters: dict):
    url = script_parameters.get('url', ' ')
    dork_type = script_parameters.get('type', None)

    google_dorks = {
        "1": "https://www.google.com/search?q=site:{}+ext:doc+|+ext:docx+|+ext:odt+|+ext:pdf+|+ext:rtf+|+ext:sxw+|+ext:psw+|+ext:ppt+|+ext:pptx+|+ext:pps+|+ext:csv".format(url),
        "2": "https://www.google.com/search?q=site:{}+intitle:index.of".format(url),
        "3": "https://www.google.com/search?q=site:{}+ext:xml+|+ext:conf+|+ext:cnf+|+ext:reg+|+ext:inf+|+ext:rdp+|+ext:cfg+|+ext:txt+|+ext:ora+|+ext:ini".format(url),
        "4": "https://www.google.com/search?q=site:{}+ext:sql+|+ext:dbf+|+ext:mdb".format(url),
        "5": "https://www.google.com/search?q=site:{}+ext:log".format(url),
        "6": "https://www.google.com/search?q=site:{}+ext:bkf+|+ext:bkp+|+ext:bak+|+ext:old+|+ext:backup".format(url),
        "7": "https://www.google.com/search?q=site:{}+inurl:login".format(url),
        "8": "https://www.google.com/search?q=site:{}+intext:%22sql+syntax+near%22+|+intext:%22syntax+error+has+occurred%22+|+intext:%22incorrect+syntax+near%22+|+intext:%22unexpected+end+of+SQL+command%22+|+intext:%22Warning:+mysql_connect()%22+|+intext:%22Warning:+mysql_query()%22+|+intext:%22Warning:+pg_connect()%22".format(url),
        "9": "https://www.google.com/search?q=site:{}+ext:php+intitle:phpinfo+%22published+by+the+PHP+Group%22".format(url),
    }

    if dork_type:
        dork = google_dorks.get(dork_type, 'Not found')
        if (dork == 'Not found'):
            return "Dork not found"
        return "<a target=\"_blank\" href=\"{0}\">{0}</a>".format(dork)


def get_parameters_for_script(script_id, script_parameters, files):
    returnValue: dict = {}
    returnValue['script_id'] = script_id

    if script_id == 1:
        returnValue['script_parameters'] = {
            'type':  script_parameters.get('type', None),
            'url': script_parameters.get('url', None),
        }
    elif script_id == 2:
        returnValue['script_parameters'] = {
            '-d': script_parameters.get('url', None),
        }
    elif script_id == 3:
        returnValue['script_parameters'] = {
            '-h': script_parameters.get('url', None),
        }
    elif script_id == 4:
        returnValue['script_parameters'] = {
            "--url": script_parameters.get('url', None)
        }
    elif script_id == 5:
        d: dict = {}
        scan_type = script_parameters.get('type', None)
        if scan_type:
            if scan_type == 'udp':
                d['-sU'] = None
            elif scan_type == 'tcp':
                d['-A'] = '-T4'
        d[script_parameters.get('url', None)] = None
        returnValue['script_parameters'] = d
    elif script_id == 6:
        returnValue['script_parameters'] = {
            "-u": script_parameters.get('url', None),
            "--batch": script_parameters.get('extra', None),
        }
    elif script_id == 7:
        returnValue['script_parameters'] = {
            "-u": script_parameters.get('url', None),
        }
    elif script_id == 8:
        returnValue['script_parameters'] = {
            "--host": script_parameters.get('url', None),
        }
    elif script_id == 9:
        returnValue['script_parameters'] = {
            '--url': script_parameters.get('url', None),
            '--ec': None
        }
    else:
        returnValue['script_parameters'] = ''

    return returnValue


def run_script_from_id(script_id: int, script_parameters: dict, outfile: str):
    # Get the script name from the scriptId
    script_name: str = scriptId_to_scriptName.get(int(script_id))

    # Check if the script name exists
    if script_name and script_name.startswith('function'):
        return {
            'success': True,
            'error': None,
            'output': eval(script_name.replace('function ', ''))(script_parameters)
        }
    elif script_name:
        bash_command = generate_bash_command(script_name, script_parameters)
        print(bash_command, script_parameters)
        # Execute the bash command
        execution_result = execute_bash_command(bash_command, outfile)

        # Check if the execution was successful
        if execution_result['success']:
            return {
                'success': True,
                'output': execution_result['output'],
                'error': None,
            }
        else:
            return {
                'success': False,
                'output': None,
                'error': execution_result['error']
            }
    else:
        return {
            'success': False,
            'output': None,
            'error': f'Script with id {script_id} does not exist.',
        }


def generate_bash_command(command: str, parameters: dict) -> str:
    # Construct the command string with the provided command
    bash_command = command

    # Add parameters as key-value pairs
    if parameters:
        for key, value in parameters.items():
            bash_command += f" {key} {value if value else ''}"

    return bash_command


def execute(cmd):
    command = cmd.split(" ", 1)
    print('command', command)
    # Execute the command as a subprocess pipe and stream output line by line
    popen = subprocess.Popen(command, stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    for stderr_line in iter(popen.stderr.readline, ""):
        yield stderr_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

    # popen = subprocess.Popen(
    #     args=cmd, stdout=subprocess.PIPE, universal_newlines=True)
    # for stdout_line in iter(popen.stdout.readline, ""):
    #     yield stdout_line
    # popen.stdout.close()
    # return_code = popen.wait()
    # if return_code:
    #     raise subprocess.CalledProcessError(return_code, cmd)


def execute_bash_command(command: str, outfile: str):
    try:
        # Run the command and capture both stdout and stderr
        def runit():
            with open(outfile, 'a') as f:
                pp_command = command.split("scripts/", 1)[1] + "\n"
                f.write(pp_command)
                f.write('-' * len(pp_command) + "\n")
                f.flush()
                for line in execute(command):
                    print('line', line)
                    f.write(line + "\n")
                    f.flush()
                f.write('=====EOF=====\n')
                f.flush()

        t1 = threading.Thread(target=runit)
        t1.start()
        return {
            'success': True,
            'error': None,
            'output': "<a href='/result/{0}' target='_blank'>{0}</a>".format(outfile.split("/")[-1][::-1])
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command execution timed out.'
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': e.output
        }
    except Exception as e:
        print(traceback.format_exc())
        return {
            'success': False,
            'error': str(e)
        }


def handle_session(request):
    sessionId = request.COOKIES.get('sessionId', None)
    if sessionId is None:
        return HttpResponseRedirect('/login')

    username = get_username_from_session_id(sessionId)
    with (open('myproject/db/users.txt', 'r')) as f:
        lines = f.readlines()
        for line in lines:
            [_username, _] = line.split(':')
            if (_username == username):
                return None

    return HttpResponseRedirect('/login')


def generate_random_session_id(username):
    return encrypt(generate_random_file_name() + '.' + username)


def get_username_from_session_id(session_id):
    return decrypt(session_id).split('.')[1]


KEY = 3


def encrypt(text):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shift = 65 if char.isupper() else 97
            encrypted_char = chr((ord(char) - shift + KEY) % 26 + shift)
            encrypted_text += encrypted_char
        else:
            encrypted_text += char
    return encrypted_text


def decrypt(encrypted_text):
    decrypted_text = ""
    for char in encrypted_text:
        if char.isalpha():
            shift = 65 if char.isupper() else 97
            decrypted_char = chr((ord(char) - shift - KEY) % 26 + shift)
            decrypted_text += decrypted_char
        else:
            decrypted_text += char
    return decrypted_text


def read_file_by_id(id_reversed):
    id = id_reversed[::-1]
    with (open('./myproject/temp_files/' + id, 'r')) as f:
        return f.read()


def read_css_file(name):
    with (open('./myproject/static/css/' + name, 'r')) as f:
        return f.read()


def read_js_file(name):
    with (open('./myproject/static/js/' + name, 'r')) as f:
        return f.read()


def read_images_file(name):
    with (open('./myproject/static/images/' + name, 'rb')) as f:
        return f.read()


def read_fonts_file(name):
    with (open('./myproject/static/fonts/' + name, 'rb')) as f:
        return f.read()


def check_if_page_exists(page):
    if os.path.isfile(f'myproject/templates/{page}.html'):
        return None
    else:
        return HttpResponseNotFound()
