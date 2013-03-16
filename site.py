import sys
import cherrypy
import json

class Root:
    #-------------------------------administrative/debugging---------------------#
    @cherrypy.expose
    def index(self, **kw):
        if kw.get('x') == '1':
            cherrypy.engine.restart()
            ip = cherrypy.request.headers["X-Forwarded-For"] #get_client_ip
            from mem import MemoryMonitor
            x = MemoryMonitor('djotjog')
            memory  = x.usage()            
            return 'CherryPy RESETTING for duty, sir! '+str(memory)+' MB in memory. /cp2/ reset requested by '+str(ip)
        else:
            from mem import MemoryMonitor
            x = MemoryMonitor('djotjog')
            memory  = x.usage()
            return 'CherryPy reporting for duty, sir! ',memory,' MB in memory.'
    @cherrypy.expose
    def echo(self, param_1=None, param_2=None, *args, **kw):
        return repr(dict(param_1=param_1,
                         param_2=param_2,
                         args=args,
                         kw=kw))  

    #-------------------generate a gexf file from wd['relevant'] ids----#
    @cherrypy.expose
    def wordtree_org_topical(self,org_json_filename):
        import wordtree_org_topic
        result = wordtree_org_topic.wordtree(org_json_filename)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps( result )
    
    @cherrypy.expose
    def wordtree_org_contrast(self,org_json_filename):
        import wordtree_org_topic
        result = wordtree_org_topic.wordtree_contrast(org_json_filename)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps( result )
            
    #-------------------fetch org data and make json--------------------#
    @cherrypy.expose
    def make_org_json(self, org_stats_id =0, gg_org_id = 0,report_id=0,  **kw): #import_source = 'pickle', verbose=False): #*args, **kw):        
        import gridplot
        filename = gridplot.wrapper_for_make_match_scoresheet(org_stats_id,gg_org_id,report_id=0)
        cherrypy.response.headers['Content-Type'] = 'application/json' #; charset=utf-8'
        return json.dumps( filename )
        
    @cherrypy.expose
    def gridplot(self, filename, location = 'nairobi', data_type = 'all', org_specific=False):
        import gridplot
        loc = gridplot.gridplot_fast(filename, location)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps( loc )     

    @cherrypy.expose
    def test_gridplot(self, filename, location = 'nairobi', data_type = 'all', org_specific=False):
        import gridplot
        loc = gridplot.test_gridplot(filename, location, data_type, org_specific)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps( loc )                                      

    @cherrypy.expose
    def grid_narrative(self, json_string={}):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        if json_string == {}:
            return "ERROR: no data received."
        else:
            from grid_narrative import grid_narrative
            return grid_narrative(json_string)
        

    #----------------------------search-dashboard-drill-down----------------#
    @cherrypy.expose
    def shlearch(self, param_1=None, param_2=None, *args, **kw):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        import slearch
        html = slearch.s(kw)
        return html

    @cherrypy.expose
    def search2(self, param_1=None, param_2=None, *args, **kw):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        import slearch
        html = slearch.s2(kw)
        return html

    @cherrypy.expose
    def search3(self, param_1=None, param_2=None, *args, **kw):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        import slearch
        html = slearch.s3(kw)
        return html

    @cherrypy.expose
    def s2_subsearch(self, string=None, orig_terms=None,session_id=None,subtype=None, *args, **kw):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        import slearch
        return slearch.s2_subsearch(string,orig_terms,session_id,subtype)
        
    #-------------------------------------------------------------------#                 
    @cherrypy.expose
    def test_phrases(self, ids = None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        #requires a [list of ids] passed as only parameter
        #returns a [list] of phrases -- converted to JSON here.
        IDS = str(ids).split(',')
        if len(IDS) < 2:
            from random import sample
            V = sample(xrange(36191),400)
            import metanarr
            textlist = metanarr.everything(V)
            return json.dumps(textlist)
        V = []
        if len(IDS) > 0:
            for x in IDS:
                try:
                    V.append(int(str(x).strip()))
                except:
                    continue
        else:
            return str(ids)
        import metanarr
        if type(V) is not list:
            return json.dumps([])
        if len(V) == 0:
            return json.dumps([])
        textlist = metanarr.everything(V)
        return json.dumps(textlist)

    @cherrypy.expose
    def fetch_phrases(self, ids = None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        #requires a [list of ids] passed as only parameter
        #returns a [list] of phrases -- converted to JSON here.
        IDS = str(ids).split(',')
        V = []
        if len(IDS) > 0:
            for x in IDS:
                try:
                    V.append(int(str(x).strip()))
                except:
                    continue
        else:
            return str(ids)
        import metanarr
        if type(V) is not list:
            return json.dumps([])
        if len(V) == 0:
            return json.dumps([])
        textlist = metanarr.phrases(V)
        return json.dumps(textlist)
    #-------------------------------------------------------------------#
    @cherrypy.expose
    def ratio_bubbles(self, **kw):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        import ratio_bubbles as rb
        json_out = rb.ratio_bubbles(kw.get('pref1'),
                                    kw.get('pref2'),
                                    kw.get('ptype1'),
                                    kw.get('ptype2'),
                                    kw.get('pw'))
        return json_out #already in json format
    @cherrypy.expose
    def ratio_bubbles_gg(self, **kw):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        import ratio_bubbles_gg as rb
        json_out = rb.ratio_bubbles(kw.get('pref1'),
                                    kw.get('pref2'),
                                    kw.get('ptype1'),
                                    kw.get('ptype2'))
        return json_out #already in json format
    #-------------------------------------------------------------------#
    @cherrypy.expose
    def benford_old(self, **kw):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        ip = cherrypy.request.headers["X-Forwarded-For"]
        import benford
        sparks = benford.heuristic_to_html(kw.get('textarea_1_1'),kw.get('description'),str(ip))
        if sparks != []:
            return sparks
        else:
            return "<html><body>Error. Try again.</body></html>"

    @cherrypy.expose
    def benford(self, **kw):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        ip = cherrypy.request.headers["X-Forwarded-For"]
        import benford
        sparks = benford.heuristic_to_words_html(kw.get('textarea_1_1'),kw.get('description'),str(ip))
        if sparks != []:
            return sparks
        else:
            return "<html><body>Error. Try again.</body></html>"


    @cherrypy.expose
    def benford_json(self, **kw): #API version- returns JSON only
        cherrypy.response.headers['Content-Type'] = 'text/html'
        ip = cherrypy.request.headers["X-Forwarded-For"]
        import benford
        sparks = benford.heuristic_json(kw.get('textarea_1_1'),kw.get('description'),str(ip))
        if sparks != []:
            return sparks
        else:
            return "<html><body>Error. Try again.</body></html>"

    #----------------org-dedupe-console------------------------------------------#
    # dedupe_org.py --> dedupe_org.html
    @cherrypy.expose
    def dedupe_org(self, **kw):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        import dedupe_org as dedo
        #orgname="",revorg="",pw="",selected=-1
        msg = dedo.dedupe_org(kw.get('orgname'),kw.get('revorg'),kw.get('pw'),kw.get('selected'))
        return msg 
    @cherrypy.expose
    def find_similar_orgs(self, **kw):
        #cherrypy.response.headers['Content-Type'] = 'application/json'
        #cherrypy.response.headers['Content-Type'] = 'text/plain'
        cherrypy.response.headers['Content-Type'] = 'text/html'
        import dedupe_org as dedo
        orgs = dedo.find_similar_orgs(kw.get('orgname'))
        return orgs #repr(orgs) #json.dumps(orgs)
    @cherrypy.expose
    def suggest(self):
        import dedupe_org as dedo
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return dedo.suggest()
    #-------------------------------------------------------------------#
        
cherrypy.config.update({
'environment': 'production',
'log.screen': False,
'log.error_file':'cperror.log',
'server.socket_host': '127.0.0.1',
'server.socket_port': 28096,
'server.thread_pool': 2,
'server.thread_pool_max': 2,
})
cherrypy.quickstart(Root())
"""
cherrypy.tree.mount(Root, "/")
if hasattr(cherrypy.engine, 'block'):
    # 3.1 syntax
    cherrypy.engine.start()
    cherrypy.engine.block()
"""
