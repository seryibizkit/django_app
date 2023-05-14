from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    return render(request, "requestdataapp/user-bio-form.html")


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if int(request.headers.get("Content-Length")) < 1000000:
        if request.method == "POST" and request.FILES.get("myfile"):
            myfile = request.FILES["myfile"]
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print("saved file", filename)
            return render(request, "requestdataapp/file-upload.html")
        else:
            context = {
                "error": "No file added. Please, choose file.",
            }
            return render(request, "requestdataapp/file-upload.html", context=context)
    else:
        context = {
            "error": "This file is too large. Maximum size is 1MB.",
        }
        return render(request, "requestdataapp/file-upload.html", context=context)
