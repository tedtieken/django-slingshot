from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import media

def index(request):
	return render_to_response('index.html', locals(), context_instance=RequestContext(request))
	
def login(request):
	return render_to_response('login.html', locals(), context_instance=RequestContext(request))
	
def signup(request):
	return render_to_response('signup.html', locals(), context_instance=RequestContext(request))
	
def features(request):
	return render_to_response('features.html', locals(), context_instance=RequestContext(request))
	
def learn(request):
	return render_to_response('learn.html', locals(), context_instance=RequestContext(request))
	
def faqs(request):
	return render_to_response('faqs.html', locals(), context_instance=RequestContext(request))
	
def support(request):
	return render_to_response('support.html', locals(), context_instance=RequestContext(request))