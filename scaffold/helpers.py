import re, os
from django.db.models.fields import AutoField

NOMATCH_OK = ["FORM", "URL", "VIEW", "TEMPLATE", "VIEW_IMPORTS", "FORM_IMPORTS", "INCLUDE"]


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    Stolen from manage.py syncdb/sql process

    """
    pass


# input:   StringManipulationFunction
# returns: string_manipulation_function
def split_uppercase(string):
    x=''
    count = 0
    for i in string:
        if i.isupper():
            if count == 0:
                x+= i.lower()
            else:
                x+= '_%s' % i.lower()
        else:
            x+=i
        count += 1

    return x.strip()

# in: a_string
# out: a-string
def url_format(string):
    x = ""
    for i in string:
        if i == "_":
            x+="-"
        else:
            x+=i
    return x
    
# in: a-string
# out: a_string
def view_format(string):
    x = ""
    for i in string:
        if i == "-":
            x+="_"
        else:
            x+=i
    return x

# in: a-string_formated
# out: AStringFormated

def form_format(string):
    x = ""
    skip=False
    count = 0
    for i in string:
        if count == 0:
            i = i.upper()
        count += 1
        if skip == True:
            skip = False
            x += i.upper()
        else:
            if i in ["-", "_"]:
                skip = True
            else:
                x += i
    return x

# input: a string that ends like this,
# output: a string that ends like this
def remove_trailing_comma(string):
    string = string.strip()
    last = len(string) - 1
    if string[last] == ",":
        return string[0:last]
    #elif string[last-1:last] == ", ":
    #    return string[0:last-2]
    else:
        return string


# input: a pre scaffold list of items to build of potentially heterogeneous form [str, dict, list]
# output: a normalized list of dicts of items to build
def create_build_list(pre_scaffold):
    build_list = []

    for build in pre_scaffold:
        if type(build) is str:
            add_me = {"recipe": build, "name": build.split(".")[0]}
        elif type(build) is list:
            if len(build) >= 2:
                add_me = {"recipe": build[0], "name": build[1].split(".")[0]}
            else:
                add_me = {"recipe": build[0], "name": build[0].split(".")[0]}
        elif type(build) is dict:
            add_me = {}
            if build.has_key("recipe"):
                add_me["recipe"] = build["recipe"]
                if build.has_key("name"):
                    add_me["name"] = build["name"].split(".")[0]
                else:
                    add_me["name"] = build["base"].split(".")[0]
            else:
                raise ValueError("When a dictionary is used in the build_list, at a minimum it must define a key 'recipe'")
        else:
            raise ValueError("build_list must be a list of strings, lists, or dicts")
        build_list.append(add_me)
    return build_list
    
    
def br_the_object(model, template_object_name, include_name):
    return_str = ""
    for f in model._meta.local_fields:
        if include_name:
            return_str += "%s: {{%s.%s}}<br>\r\n" % (f.name, template_object_name, f.name,)
        else:
            return_str += "{{%s.%s}}<br>\r\n" % (template_object_name, f.name,)
    return return_str



def form_list_the_object_fields(model, auto_too = False):
    return_str = ""
    for f in model._meta.local_fields:
        if auto_too:
            return_str += "'%s'," % f.name
        elif not isinstance(f, AutoField):
            return_str += "'%s'," % f.name
    return return_str


def stilts_replace(working_copy, swap_dict, errors, recipe_name, app_name = None, model_name = None):
    # create dictionary of tokens in recipie
    token_list = re.findall('!!!(\w+)!!!', working_copy)
    token_dict = {}
    for token in token_list:
        if not token_dict.has_key(token):
            token_dict[token] = token

    # replace all matched tokens 
    for token in token_dict:
        if swap_dict.has_key(token):
            working_copy = re.sub('!!!' + token + '!!!', swap_dict[token], working_copy)
        else:
            if token in NOMATCH_OK:
                continue
            if model_name:
                errors.append("no match for token: %s invoked in recipe %s (app:%s model:%s)" % (token, recipe_name, app_name, model_name))
            else:
                errors.append("no match for token: %s invoked in recipe %s (app:%s)" % (token, recipe_name, app_name))                
    return working_copy
    
    
def load_recipe(the_dir, recipe):
    # If exact file open and return
    if os.path.exists(the_dir+recipe):
        f = open(the_dir+recipe, 'r')
        working_copy = f.read()
        f.close()
        return working_copy   
    
    # If no exact match, raise IO error to be caught
    raise IOError
        
    # If we made it here, there is no exact match
    #rec = recipe.split(".")[0]      # Get the short recipe name (all left of the first .)
    #dir_list = os.listdir(the_dir) 
    #if len(dir_list) == 0:          # If dir is empty, can never load recipe, fail
    #    raise IOError
    #for item in dir_list:  
    #    if rec == item.split(".")[0]: 
    #        f = open(the_dir+item, 'r')
    #        working_copy = f.read()
    #        f.close()
    #        return working_copy
    #raise IOError       # If we make it here, nothing has been found raise IO to be caught

    #
    # if os.path.exists(the_dir+recipe):
    #     f = open(the_dir+recipe, 'r')
    #     working_copy = f.read()
    #     f.close()
    #     return working_copy        
    # elif os.path.exists(the_dir+recipe+".stilts"):
    #     f = open(the_dir+recipe+".stilts")
    #     working_copy = f.read()
    #     f.close()
    #     return working_copy 
    # elif os.path.exists(the_dir+recipe.split(".")[0]):
    #     f = open(the_dir+recipe.split(".")[0], 'r')
    #     working_copy = f.read()
    #     f.close()
    #     return working_copy        
    # else:
    #     raise IOError


# Modified from code in django.core.management.commands.syncdb.py 
def model_installed(model):
    from django.db import connection, close_connection
    
    tables = connection.introspection.table_names()
    opts = model._meta
    converter = connection.introspection.table_name_converter
    result = ((converter(opts.db_table) in tables) or
        (opts.auto_created and converter(opts.auto_created._meta.db_table) in tables))
    close_connection()
    return result

    