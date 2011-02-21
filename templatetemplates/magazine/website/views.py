from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

def index(request):
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))
    
def view_post(request):
    return render_to_response('post.html', locals(), context_instance=RequestContext(request))
    
def login_signup(request):
    return render_to_response('login_signup.html', locals(), context_instance=RequestContext(request))

def signup_action(request):
    return HttpResponseRedirect('/website/')
    
def login_action(request):
    return HttpResponseRedirect('/website/')
    
#DEVELOPMENT ONLY
def core_only(request):
    return render_to_response('core_only.html', locals(), context_instance=RequestContext(request))
    
def core_right(request):
    return render_to_response('core_right.html', locals(), context_instance=RequestContext(request))