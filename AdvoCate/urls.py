from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'AdvoCate.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
   # url(r'^(?i)CategoryModeler/', include('Category_Modeler.urls')),
    url(r'^(?i)AdvoCate/', include('Category_Modeler.urls')),
#    url(r'^(?i)AdvoCate/accounts/$', include('Accounts.urls')),

)
