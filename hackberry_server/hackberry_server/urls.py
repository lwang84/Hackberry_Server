from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hackberry_server.views.home', name='home'),
    # url(r'^hackberry_server/', include('hackberry_server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

	url(r'^api/init/$', 'api.views.importData'),
	url(r'^api/check/(?P<playerGuess>[a-z]+)/$', 'api.views.checkSound'),
	url(r'^api/(?P<playerID>\d+)/requestNewGameWithOpponentSpecified/(?P<opponentID>\d+)/$', 'api.views.requestNewGameWithOpponentSpecified'),
	url(r'^api/(?P<playerID>\d+)/requestNewGame/$', 'api.views.requestNewGame'),
)
