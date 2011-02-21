from django.db import models


class TestModel(models.Model):
    name = models.TextField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True)

    #Scaffold Notes: required for templates
    def __unicode__(self):
        return "%s" % (self.name)

    
    def get_absolute_url(self):
        return ""




    def scaffold(self):
        '''
        returns a settings dictionary.  If not provided, a default is used with create, detail, list
        views - a list of which views to create, either as strings, dicts, lists, or a combination
        '''

        return {
            "build_list": [
                    {"recipe": "detail", "name": "view", "overrides": 
                        {},
                    },
                    "create",
                    "edit",
                    "list",
                    ],
            "overrides": None,
            }