# scaffold.py
# To be called from manage.py shell
# Design Objective - Simple with advanced features, unobtrusive

import os, sys
import re
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style

import django
from time import time
from helpers import *

DEFAULT_SETTINGS_DICT = {
    "build_list":[]    
}
DEFAULT_BUILD_LIST = []

#DEFAULT_SETTINGS_DICT = {
#    "build_list":
#        [
#            "list",
#            {"recipe": "detail", "name": "detail"},
#            ["create", "add_new"],
#        ],
#}
#DEFAULT_BUILD_LIST = ["create", "list", "detail"]

TAB = "    "
EOL = "\r\n"


def scaffold(app_name):
    #TODO NOW
    
    #TODO
    # Build Log to record success as well as failures
    # Revise workflow after getting feedback... maybe hook into command line
	# Add URL imports to recipe
	# Redo to allow for 
	#   app 
	#   app.model 
	#   app.model ["recipe", "name"]
	# Add check for unicode

    
    #TODO Consider
    # Redo Overrides, consider recipe overrides in file or in dict
    # Refactor Admin to be part of recipe
    # Consider revising !!! as recipe delimiter - maybe [!!] and [%%]
    # add 'l-model-name'
        
    # Verify app exists
    try:
        app = django.db.models.get_app(app_name)
    except:
        raise CommandError("Invalid app name, make sure app is in settings.py installed apps and restart the shell session")

    # initialize blank variables
    url_list = []
    view_list = []
    form_list = []
    template_list = []
    view_import_list = []
    form_import_list = []
    model_list = []
    errors = []    

    # Get models, set input dir
    app_models = django.db.models.get_models(app)    
    recipe_dir = 'scaffold/recipes/'        
    
    # Verify Model installed, also verifies that a DB has been created
    for model in app_models:
        if not model_installed(model):
            errors.append('WARNING: %s.%s does not appear to have been installed in db\r\n"python manage.py syncdb" or "python manage.py sql %s" may help' % (app_name, model.__name__, app_name))               
    
    # Setup out directory structure
    file_time = str(int(time()))
    scaffold_dir = 'scaffold/' + app_name + file_time
    scaffold_dir_template = scaffold_dir + "/templates"    
    if not os.path.exists (scaffold_dir):
        os.makedirs (scaffold_dir)
    if not os.path.exists (scaffold_dir_template):
        os.makedirs (scaffold_dir_template)
    

    
    # create imports
    base_import = "from %s.models import " % app_name
    form_import_star = "from %s.forms import *" % app_name

    # Itterate over models
    for model in app_models:
        model_name = model.__name__
        l_model_name = split_uppercase(model_name)
        model_list.append(model_name)
        base_import += model_name + ", " # Add to import list

        instance = model()  # Get an instance so we can get it's setting_dict
        swap_dict = {}      # model level dict, initialized at model level, 

        #Get and set up settings
        try:
            settings_dict = instance.scaffold()
        except:
            settings_dict = DEFAULT_SETTINGS_DICT
        if not type(settings_dict) is dict:
            settings_dict = DEFAULT_SETTINGS_DICT
    
        try:
            pre_scaffold = settings_dict['build_list']
        except ValueError:
            pre_scaffold = DEFAULT_BUILD_LIST
        if not type(pre_scaffold) is list:
            pre_scaffold = DEFAULT_BUILD_LIST

        build_list = create_build_list(pre_scaffold)
        print "%s build list: %s" % (model_name, build_list)
        
        for build_item in build_list:
            # Create Build Dictionary
            swap_dict = {
                "APP_NAME": app_name,
                "URL_PATH": url_format(l_model_name) + "/" + url_format(build_item['name']) + "/",    
                "URL_NAME": l_model_name + "_" + view_format(build_item['name']),
                "VIEW_NAME": l_model_name + "_" + view_format(build_item['name']),
                "URL_APP_TAG": app_name,
                "OBJECT_NAME": l_model_name + "_object",
                "TEMPLATE_OBJECT_NAME": l_model_name + "_object",
                "SET_NAME": l_model_name + "_set",
                "TEMPLATE_SET_NAME": l_model_name + "_set",
                "PAGINATED_NAME": l_model_name + "_set_paginated",
                "TEMPLATE_PATH": "",
                "TEMPLATE_NAME": l_model_name + "_" + view_format(build_item['name']) + ".html",
                "TEMPLATE_BASE": "base.html",
                "MODEL_NAME": model_name,
                "L_MODEL_NAME": l_model_name,
                "ACTION_NAME": build_item['name'].capitalize(),
                "URL_DETAIL": l_model_name + "_detail",
                "URL_LIST": l_model_name + "_list",
                "URL_CREATE": l_model_name + "_create",
                "URL_EDIT": l_model_name + "_edit",
                "FORM_NAME": model_name + form_format(build_item['name']),
                "FORM_FIELDS": form_list_the_object_fields(model, False), 
                "FORM_FIELDS_ALL": form_list_the_object_fields(model, True), 
                }
            
            #Override name of sub-urls for most common views in case they were renamed
            for bi2 in build_list:
                if bi2['recipe'].split(".")[0] == "detail":
                    swap_dict["URL_DETAIL"] = l_model_name + "_" + view_format(bi2['name'])
                elif bi2['recipe'].split(".")[0] == "list":
                    swap_dict["URL_LIST"] = l_model_name + "_" + view_format(bi2['name'])
                elif bi2['recipe'].split(".")[0] == "create":
                    swap_dict["URL_CREATE"] = l_model_name + "_" + view_format(bi2['name'])
                elif bi2['recipe'].split(".")[0] == "edit":
                    swap_dict["URL_EDIT"] = l_model_name + "_" + view_format(bi2['name'])

            # Settings dict from model class provides overrides if there is a collision
            for key in settings_dict:
                swap_dict[key] = settings_dict[key]    
            
            # Generate complex objects
            # After setting dict overrides in case of overwrites
            swap_dict["TEMPLATE_OBJECT_ASBR"] = br_the_object(model, swap_dict["TEMPLATE_OBJECT_NAME"], False),
            swap_dict["TEMPLATE_OBJECT_ASBR_WNAME"] = br_the_object(model, swap_dict["TEMPLATE_OBJECT_NAME"], True),

            # load recipe, on failure go to next recipie
            try:
                working_copy = load_recipe(recipe_dir, build_item['recipe'])                
            except IOError:
                errors.append("recipe not found: %s, in %s, skipped" % (build_item['recipe'], recipe_dir))
                working_copy = ""
                continue
                
            # process any includes
            to_replace = re.findall('!!!INCLUDE!!!(.*)!!!INCLUDE!!!', working_copy)
            for replacement in to_replace:
                try:
                    add_me = open(recipe_dir+replacement, 'r').read()
                except IOError:
                    errors.append("include not found: %s%s, invoked in recipe %s" % (recipe_dir, replacement, build_item['recipe']))
                else:
                    working_copy = re.sub('!!!INCLUDE!!!' + replacement + '!!!INCLUDE!!!', add_me, working_copy)
            
            working_copy = stilts_replace(working_copy, swap_dict, errors, build_item['recipe'], app_name, model_name)
            
            # setup template path to write        
            if swap_dict["TEMPLATE_PATH"]:
                template_file_name = scaffold_dir_template + "/" + swap_dict["TEMPLATE_PATH"] + swap_dict["TEMPLATE_NAME"] 
            else:
                template_file_name = scaffold_dir_template + "/" + swap_dict["TEMPLATE_NAME"] 
                
            # Cut recipe into components
            pre_url = re.search('!!!URL!!!(.*)!!!URL!!!', working_copy, re.DOTALL)
            pre_view = re.search('!!!VIEW!!!(.*)!!!VIEW!!!', working_copy, re.DOTALL)
            pre_view_import =  re.search('!!!VIEW_IMPORTS!!!(.*)!!!VIEW_IMPORTS!!!', working_copy, re.DOTALL)
            pre_template = re.search('!!!TEMPLATE!!!(.*)!!!TEMPLATE!!!', working_copy, re.DOTALL)
            pre_form = re.search('!!!FORM!!!(.*)!!!FORM!!!', working_copy, re.DOTALL)
            pre_form_import =  re.search('!!!FORM_IMPORTS!!!(.*)!!!FORM_IMPORTS!!!', working_copy, re.DOTALL)
            if pre_url:
                if pre_url.groups():
                    url_list.append(pre_url.groups()[0].strip())
            if pre_view:
                if pre_view.groups():
                    view_list.append(pre_view.groups()[0].strip())
            if pre_view_import:
                if pre_view_import.groups():
                    pre_view_imports = pre_view_import.groups()[0].strip().splitlines()
                    for imp in pre_view_imports:
                        if imp.rstrip() not in view_import_list:                    
                            view_import_list.append(imp.rstrip())
            if pre_form_import:
                if pre_form_import.groups():
                    pre_form_imports = pre_form_import.groups()[0].strip().splitlines()
                    for imp in pre_form_imports:
                        if imp not in form_import_list:                    
                            form_import_list.append(imp)
            if pre_template:
                if pre_template.groups():
                    f = open(template_file_name, 'w')
                    f.write(pre_template.groups()[0].strip())
                    f.close()
                    template_list.append(template_file_name)                    
            if pre_form:
                if pre_form.groups():
                    if pre_form.groups()[0].strip() != "":
                        form_list.append(pre_form.groups()[0].strip())

    
    # write the URLS.py
    url_out = ""    
    the_urls = ""
    try:    # load url meta recipe, on failure complain and continue
        f = open(recipe_dir+"__urls_base", 'r')
        url_out = f.read()
        f.close()
    except IOError:
        errors.append("meta recipe not found: %s__urls_base, skipped" % (recipe_dir))
    else:
        for url in url_list:
            the_urls += TAB + url + EOL #?? should this just be url?
        swap_dict['THE_URLS'] = the_urls
        url_out = stilts_replace(url_out, swap_dict, errors, "__urls_base", app_name, "final output")
        f = open(scaffold_dir + "/urls.py", 'w')
        f.write(url_out)
        f.close()    
    
    # write the VIEWS.py
    views_out = ""    
    the_views = ""
    the_imports = ""
    view_import_list.sort()
    try:    # load meta recipe, on failure complain and continue
        f = open(recipe_dir+"__views_base", 'r')
        views_out = f.read()
        f.close()
    except IOError:
        errors.append("meta recipe not found: %s__views_base, skipped" % (recipe_dir))
    else:
        for view in view_list:
            the_views += view + EOL*3 
        for imp in view_import_list:
            the_imports += imp + EOL
        swap_dict['THE_VIEWS'] = the_views
        swap_dict['VIEW_RECIPE_IMPORTS'] = the_imports
        swap_dict['MODEL_IMPORTS'] = remove_trailing_comma(base_import)
        if len(form_list) > 0:
            swap_dict['FORM_IMPORTS'] = form_import_star
        views_out = stilts_replace(views_out, swap_dict, errors, "__views_base", app_name, "final output")
        f = open(scaffold_dir + "/views.py", 'w')
        f.write(views_out)
        f.close()  
              
    # write the FORMS.py
    forms_out = ""    
    the_forms = ""
    the_imports = ""
    try:    # load meta recipe, on failure complain and continue
        f = open(recipe_dir+"__forms_base", 'r')
        forms_out = f.read()
        f.close()
    except IOError:
        errors.append("meta recipe not found: %s__forms_base, skipped" % (recipe_dir))
    else:
        for form in form_list:
            the_forms += form + EOL*3 
        for imp in form_import_list:
            the_imports += imp + EOL
        swap_dict['THE_FORMS'] = the_forms
        swap_dict['FORM_RECIPE_IMPORTS'] = the_imports
        swap_dict['MODEL_IMPORTS'] = remove_trailing_comma(base_import)
        forms_out = stilts_replace(forms_out, swap_dict, errors, "__forms_base", app_name, "final output")
        f = open(scaffold_dir + "/forms.py", 'w')
        f.write(forms_out)
        f.close()
        
    # Admin Bonus
    admin_out = remove_trailing_comma(base_import) + EOL
    admin_out += "from django.contrib import admin" + EOL*2
    for model in model_list:
        admin_out += "admin.site.register(%s)%s" % (model, EOL)
    f = open(scaffold_dir + "/admin.py", 'w')
    f.write(admin_out)
    f.close()          

    # base.html Bonus
    # For a VERY early stage project
    # Or, just don't copy this one over.
    are_belong = "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\r\n"
    are_belong += "<html lang=\"en\">\r\n"
    are_belong += "<head>\r\n"
    are_belong += "    <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">\r\n"
    are_belong += "    <title>{% " + "block title %}{% " + "endblock %}</title>\r\n"
    are_belong += "</head>\r\n"
    are_belong += "<body>\r\n"
    are_belong += "    {% "+"block content %}{% "+"endblock %}\r\n"
    are_belong += "</body>\r\n"
    are_belong += "</html>\r\n"
    f = open(scaffold_dir_template + "/base.html", 'w')
    f.write(are_belong)
    f.close()           

    # 
    #are_belong2 = "{%" + ' extends "base.html"%}\r\n'
    #are_belong2 = "{% " + "block title %}" + app_name + "{% " + "endblock %}"
    #f = open(scaffold_dir_template + "/" + app_name + "base.html", 'w')
    #f.write(are_belong2)
    #f.close()           

        
    errors.sort()
    for error in errors:
        print error    
    return errors



if __name__ == "__main__":
    #TODO build this 
    pass

                        
            
#Done
# 11/16
# Restructure build-list to reflect new recpie structure
# Write build-list transformation functions to try appending (.stilts) and remove .* to get name

# 11/19
# load form fields without loading id using isinstance()
# Write "edit" recipe
# Write "create" recipe    
# Sort imports to facilitate cleanup
# Right strip view imports to ensure spacing differences don't lead to duplication

# 12/3
# Check that db has been synced, warn if it hasn't
# test if model has been synced to db, if not warn and suggest remedy
# Add CSRF to forms
# Provide overrides for output names of views e.g. URL_DETAIL rewritten as mymodel_view
# Refactor Recipe Loads, Base Loads
# Add back base.html bonus
# Move ALL links to comments

# 12/4
# Rewrote recipe finding, removed unintuitive functionality

# 12/23
# Fix ["recipe", "my-compound-name"] in l_model name and such - 
# added form_format, view_foramt, and url_format helper functions
# Create "Blank" recipe
# Create "Confirm" recipe
# Add Model name to build list info printout
# Added {% empty %} to list recipes
