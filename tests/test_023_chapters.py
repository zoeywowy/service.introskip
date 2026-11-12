import sys, types, unittest, tempfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
logs=[]
settings_values={'general.use_chapters':True,'general.use_recap':True,'general.use_outro':True,'general.use_movie_credits':True}
class PlayerStub:
    def getTotalTime(self):return 3600
    def isPlayingVideo(self):return True
class Addon:
    def getAddonInfo(self,key):return {'id':'service.introskip','name':'IntroSkip','path':str(BASE),'profile':tempfile.gettempdir()}.get(key,'')
    def getSettingBool(self,key):return settings_values.get(key,False)
    def getSetting(self,key):return '0'
    def getSettingString(self,key):return ''
class Dialog:
    def __init__(self):self.showed=[]
    def textviewer(self,heading,text,usemono=False):self.showed.append(text)
    def ok(self,*args):pass
xbmc=types.ModuleType('xbmc')
xbmc.Player=PlayerStub
for k,n in [('LOGDEBUG',0),('LOGINFO',1),('LOGWARNING',2),('LOGERROR',3),('LOGFATAL',4)]:setattr(xbmc,k,n)
xbmc.log=lambda m,level=0: logs.append((m,level))
xbmc.getInfoLabel=lambda key:'22.0' if key=='System.BuildVersion' else ''
xbmcgui=types.ModuleType('xbmcgui');xbmcgui.Dialog=Dialog
xbmcvfs=types.ModuleType('xbmcvfs');xbmcvfs.translatePath=lambda s:s
xbmcaddon=types.ModuleType('xbmcaddon');xbmcaddon.Addon=Addon
for name,mod in [('xbmc',xbmc),('xbmcgui',xbmcgui),('xbmcvfs',xbmcvfs),('xbmcaddon',xbmcaddon)]:sys.modules[name]=mod
from resources.lib import chapters,tools

sample=[{'index':1,'time':0,'name':'Cold open'},
        {'index':2,'time':85,'name':'Main titles'},
        {'index':3,'time':165,'name':'Story'},
        {'index':4,'time':2000,'name':'End credits'},
        {'index':5,'time':2200,'name':'Post-Credits Scene'}]
class NativeChapterTests(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        self.payload=sample
        self.active=[{'type':'video','playerid':1}]
        self.old=tools.execute_jsonrpc
        def api(method,params=None):
            self.calls.append((method,params))
            return self.active if method=='Player.GetActivePlayers' else {'chapters':self.payload}
        tools.execute_jsonrpc=api
        self.adapter=chapters.ChaptersAdapter()
        self.adapter.player=PlayerStub()
    def tearDown(self):tools.execute_jsonrpc=self.old
    def test_native_api_and_seconds(self):
        cs=self.adapter._get_chapters_multiple_methods()
        self.assertEqual(cs[1]['start'],85)
        self.assertEqual(cs[1]['end'],165)
        self.assertEqual(self.calls[1],('Player.GetChapters',{'playerid':1}))
        self.assertFalse(any(m=='Player.GetProperties' for m,p in self.calls))
    def test_intro_explicit(self):self.assertEqual(self.adapter.get_points('',1,1,'intro'),[(85.0,165.0)])
    def test_outro_excludes_postcredit(self):self.assertEqual(self.adapter.get_points('',1,1,'outro'),[(2000.0,2200.0)])
    def test_movie_credit(self):self.assertEqual(self.adapter.get_points('',1,1,'movie_outro'),[(2000.0,2200.0)])
    def test_postcredit(self):self.assertEqual(self.adapter.get_points('',1,1,'post_credits'),[(2200.0,3600.0)])
    def test_no_chapter_inspector(self):
        self.assertFalse(hasattr(self.adapter, 'report'))
    def test_unnamed_untrusted_outro(self):
        self.payload=[{'index':1,'time':0}, {'index':2,'time':400}, {'index':3,'time':3000}]
        self.assertIsNone(self.adapter.get_points('',1,1,'outro'))
        self.assertEqual(self.adapter.last_generic_count,3)
    def test_single_timing_heuristic_is_manual(self):
        self.payload=[{'index':1,'time':0},{'index':2,'time':100},{'index':3,'time':190},{'index':4,'time':500}]
        self.assertEqual(self.adapter.get_points('',1,1,'intro'),[(100.,190.)])
        self.assertEqual(self.adapter.last_match_kind,'chapter_heuristic')
    def test_multiple_timing_candidates_rejected(self):
        self.payload=[{'index':1,'time':0},{'index':2,'time':100},{'index':3,'time':170},{'index':4,'time':220},{'index':5,'time':300}]
        self.assertIsNone(self.adapter.get_points('',1,1,'intro'))
    def test_empty_not_cached(self):
        self.payload=[]
        self.assertEqual(self.adapter._get_chapters_multiple_methods(),[])
        self.payload=sample
        self.assertEqual(len(self.adapter._get_chapters_multiple_methods()),5)
        self.assertEqual(len([m for m,p in self.calls if m=='Player.GetChapters']),2)
    def test_wrong_player_type_rejected(self):
        self.active=[{'type':'audio','playerid':0}]
        self.assertEqual(self.adapter._get_chapters_multiple_methods(),[])
        self.assertIn('no active Kodi video',self.adapter.last_status)
    def test_invalid_timestamps_skipped(self):
        self.payload=[{'index':1,'time':float('nan')},{'index':2,'time':-1},{'index':3,'time':'bad'},{'index':4,'time':110,'name':'Recap'},{'index':5,'time':140,'name':'Scene'}]
        self.assertEqual(len(self.adapter._get_chapters_multiple_methods()),2)
        self.assertEqual(self.adapter.get_points('',0,0,'recap'),[(110.,140.)])
    def test_invalid_close_boundary(self):
        self.payload=[{'index':1,'time':800,'name':'Intro'}]
        self.assertIsNone(self.adapter.get_points('',0,0,'intro')) # no meaningful end
    def test_generic_name_does_not_match_outro(self):
        self.payload=[{'index':1,'time':0,'name':'Chapter 1'},{'index':2,'time':2100,'name':'Chapter 2'}]
        self.assertIsNone(self.adapter.get_points('',0,0,'movie_outro'))
    def test_merges_adjacent_named_intro_chapters(self):
        self.payload=[
            {'index':1,'time':0,'name':'Prime Video'},
            {'index':2,'time':5,'name':'Previously On'},
            {'index':3,'time':74,'name':'Opening Credits'},
            {'index':4,'time':147,'name':'Title Sequence'},
            {'index':5,'time':167,'name':'Scene 5'},
        ]
        self.assertEqual(self.adapter.get_points('',1,3,'intro'),[(74.,167.)])
        self.assertEqual(self.adapter.get_points('',1,3,'recap'),[(5.,74.)])
        self.assertTrue(self.adapter.chapter_cache)
        # Once Kodi exposes the full list, normal requests reuse it for this playback.
        self.assertEqual(len([m for m,p in self.calls if m=='Player.GetChapters']),1)
    def test_no_merging_unnamed_chapter_after_intro(self):
        self.payload=[
            {'index':1,'time':74,'name':'Opening Credits'},
            {'index':2,'time':147,'name':'Scene 2'},
            {'index':3,'time':167,'name':'Main Titles'},
            {'index':4,'time':200,'name':'Scene 4'}
        ]
        self.assertEqual(self.adapter.get_points('',1,3,'intro'),[(74.,147.)])

    def test_named_credits_not_opening(self):
        self.payload=[{'index':1,'time':0,'name':'Opening credits'},{'index':2,'time':2000,'name':'Story'}]
        self.assertIsNone(self.adapter.get_points('',0,0,'outro'))

if __name__=='__main__':unittest.main(verbosity=2)
