from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import myproject.utils as utils

#####
# / #
#####


def index(request):
    sessionId = request.COOKIES.get('sessionId', None)
    isLogged = False
    if sessionId is not None:
        isNotLoggedIn = utils.handle_session(request)
        if isNotLoggedIn is None:
            isLogged = True

    return render(request, 'index.html', {'isLogged': isLogged})

##########
# /login #
##########


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        with (open('myproject/db/users.txt', 'r')) as f:
            lines = f.readlines()
            print(lines)
            for line in lines:
                line = line.replace('\n', '')
                [_username, _password] = line.split(':')
                print(_username, "{}".format(_password))
                print(username, "'{}'".format(password))
                print(username == _username, password == _password)
                if (_username == username and _password == password):
                    response = HttpResponse()
                    response.set_cookie(
                        'sessionId', utils.generate_random_session_id(username))
                    response.status_code = 302
                    response.setdefault('Location', '/')
                    return response

        return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')

###############
# /run-script #
###############


@csrf_exempt
def run_script(request):
    dontHaveAccess = utils.handle_session(request)
    if dontHaveAccess is not None:
        return dontHaveAccess

    if request.method == 'POST':
        try:
            data_files = request.FILES

            script_id = int(request.POST.get('script_id', 0))
            script_parameters: dict = request.POST.dict()

            parameters: dict = utils.get_parameters_for_script(
                script_id, script_parameters, data_files)

            print(parameters, script_id, script_parameters)

            print(script_id, script_parameters)

            # Check if the scriptId and scriptParameters are provided]
            if script_id:
                # Run the script
                result = utils.run_script_from_id(
                    script_id, parameters.get('script_parameters'),
                    utils.generate_empty_file('./myproject/temp_files/out')
                )
                # Return the result
                if result['success']:
                    print(result['output'])
                    return render(request, 'scan-result.html', {'data': result['output']})
                else:
                    return render(request, 'scan-result-failed.html', {'error': result['error']})
            else:
                return render(request, 'scan-result-failed.html')
            return JsonResponse(response_data)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return render(request, '500.html', status=500, context={
                'error': '{}'.format(e),
            })
    else:
        response_data = {
            'error': 'Only POST requests are allowed.',
        }
        return JsonResponse(response_data, status=405)

################
# /result/<id> #
################


def result(request, id):
    dontHaveAccess = utils.handle_session(request)
    if dontHaveAccess is not None:
        return dontHaveAccess

    content = utils.read_file_by_id(id)
    return render(request, 'result.html', {'content': content, 'id': id})

#############
# /css/<id> #
#############


def cssLoader(request, id):
    content = utils.read_css_file(id)
    return HttpResponse(content, content_type='text/css')

############
# /js/<id> #
############


def jsLoader(request, id):
    content = utils.read_js_file(id)
    return HttpResponse(content, content_type='text/javascript')

################
# /images/<id> #
################


def imagesLoader(request, id):
    content = utils.read_images_file(id)
    return HttpResponse(content, content_type='image/png')


###############
# /fonts/<id> #
###############

def fontsLoader(request, id):
    content = utils.read_fonts_file(id)
    return HttpResponse(content, content_type='application/octet-stream')

###########
# /logout #
###########


def logout(request):
    response = HttpResponse()
    response.delete_cookie('sessionId')
    response.status_code = 302
    response.setdefault('Location', '/')
    return response

#########################
# /terms-and-conditions #
#########################


def terms_and_conditions(request):
    return render(request, 'terms-and-conditions.html')

###########
# /<page> #
###########


def page(request, page):
    dontHaveAccess = utils.handle_session(request)
    if dontHaveAccess is not None:
        return dontHaveAccess

    pageDoesntExist = utils.check_if_page_exists(page)
    if pageDoesntExist:
        return render(request, '404.html')

    return render(request, "{}.html".format(page))
