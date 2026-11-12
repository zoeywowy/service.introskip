"""Offline Kodi 22 integration and keyless Cinemeta resolver tests for 0.0.23."""
import os
import sys
import types
import time
import unittest
import threading
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
settings_values = {
    'general.use_intro': True, 'general.use_recap': True,
    'general.use_outro': True, 'general.use_movie_credits': True,
    'customize.theme': 'Dark', 'customize.size': '1',
    'customize.position': '0', 'customize.style': '0',
    'customize.contents': '0', 'customize.button_color': '0',
    'customize.button_color_light': '0',
}
logs = []

class Addon:
    def getAddonInfo(self, key):
        return {'id':'service.introskip','name':'IntroSkip', 'path':str(BASE),
                'profile':tempfile.gettempdir()}.get(key, '')
    def getSettingBool(self,key):return settings_values.get(key,False)
    def getSetting(self,key):return str(settings_values.get(key,''))
    def getSettingString(self,key):return str(settings_values.get(key,''))
    def getLocalizedString(self,key):return {32002:'Light',32003:'Dark'}.get(key, '')
    def setSetting(self,key,value):settings_values[key]=value
    def setSettingString(self,key,value):settings_values[key]=value

class VideoTag:
    def __init__(self,media_type='episode',season=1,episode=3):
        self.media_type,self.season,self.episode=media_type,season,episode
    def getMediaType(self):return self.media_type
    def getSeason(self):return self.season
    def getEpisode(self):return self.episode
    def getTVShowTitle(self):return 'The Rings of Power'
    def getTitle(self):return 'Test Movie'
    def getYear(self):return 2020
    def getIMDBNumber(self):raise AssertionError('Kodi ID must not be queried')

class FakeKodiPlayer:
    playing_tag = VideoTag()
    def __init__(self,*args,**kwargs):pass
    def getVideoInfoTag(self):return self.playing_tag
    def getTotalTime(self):return 3600
    def isPlayingVideo(self):return True
    def getPlayingFile(self):return 'https://stream/example/The.Rings.of.Power.S01E03.mkv'

class Control:
    next_id=1000
    def __init__(self,*args,**kwargs):
        self.args=args;self.kwargs=kwargs
        Control.next_id+=1;self.id=Control.next_id
    def getId(self):return self.id

class WindowXMLDialog:
    def __init__(self,*args,**kwargs):
        self.controls=[];self.properties={};self.focus=None
    def addControl(self,c):self.controls.append(c)
    def removeControl(self,c):self.controls.remove(c)
    def setFocus(self,c):self.focus=c
    def setProperty(self,k,v):self.properties[k]=v
    def getProperty(self,k):return self.properties.get(k,'')
    def close(self):pass

xbmc=types.ModuleType('xbmc')
xbmc.Player=FakeKodiPlayer
xbmc.Monitor=object
for k,n in [('LOGDEBUG',0),('LOGINFO',1),('LOGWARNING',2),('LOGERROR',3),('LOGFATAL',4)]:setattr(xbmc,k,n)
xbmc.log=lambda msg,level=0: logs.append((msg,level))
xbmc.getInfoLabel=lambda key: '22.0' if key=='System.BuildVersion' else ''
xbmc.sleep=lambda ms:None
xbmc.executeJSONRPC=lambda request:'{}'
xbmcgui=types.ModuleType('xbmcgui')
xbmcgui.WindowXMLDialog=WindowXMLDialog
xbmcgui.ControlButton=Control
xbmcgui.ControlImage=Control
xbmcgui.NOTIFICATION_INFO='info'
xbmcvfs=types.ModuleType('xbmcvfs')
xbmcvfs.translatePath=lambda path:path
xbmcvfs.exists=os.path.exists
xbmcvfs.mkdir=os.mkdir
xbmcaddon=types.ModuleType('xbmcaddon');xbmcaddon.Addon=Addon
for k,mod in [('xbmc',xbmc),('xbmcgui',xbmcgui),('xbmcvfs',xbmcvfs),('xbmcaddon',xbmcaddon)]:
    sys.modules[k]=mod

from resources.lib import tools,button_assets,color,cinemeta
from resources.lib.player import Player
from resources.lib.skip_dialog import IntroSkipDialog

class PackageTests(unittest.TestCase):
    def setUp(self):
        settings_values.update({'customize.theme':'Dark', 'customize.size':'1',
                                'customize.position':'0', 'customize.contents':'0',
                                'customize.button_color':'0', 'customize.button_color_light':'0',
                                'general.use_intro':True,'general.use_recap':True,
                                'general.use_outro':True,'general.use_movie_credits':True})
    def test_manifest_version_and_dependencies(self):
        root=ET.parse(BASE/'addon.xml').getroot()
        self.assertEqual(root.attrib['version'],'0.0.23')
        deps=[item.attrib['addon'] for item in root.findall('requires/import')]
        self.assertEqual(deps,['xbmc.python','script.module.requests'])
    def test_settings_no_advanced_or_diagnostics(self):
        root=ET.parse(BASE/'resources/settings.xml').getroot()
        cats=root.findall('category')
        self.assertEqual(len(cats),3)
        ids=[item.attrib['id'] for item in root.iter('setting')]
        for old in ('general.inspect_chapters','advanced.playback_diagnostics',
                    'api.omdb_api_key','general.use_introdb','general.use_chapters'):
            self.assertNotIn(old,ids)
        self.assertIn('general.show_notifications',ids)
        self.assertIn('customize.button_color',ids)
        self.assertIn('customize.button_color_light',ids)
    def test_removed_modules_not_in_package(self):
        self.assertFalse((BASE/'resources/lib/omdb.py').exists())
        self.assertTrue((BASE/'resources/lib/cinemeta.py').exists())
        self.assertNotIn('playback_diagnostics',(BASE/'main.py').read_text())
        self.assertNotIn('inspect_chapters',(BASE/'main.py').read_text())
        self.assertNotIn('IntroSkip.Diagnostics',(BASE/'resources/lib/service.py').read_text())
        self.assertNotIn('VideoLibrary.GetTVShowDetails',(BASE/'resources/lib/player.py').read_text())
    def test_png_assets_all_exist(self):
        media=BASE/'resources/skins/Default/media'
        for theme in ('dark','light'):
            for style in range(3):
                self.assertTrue(all(Path(p).is_file() for p in button_assets.textures(str(media),theme,style)))
    def test_dialog_has_no_placeholder(self):
        root=ET.parse(BASE/'resources/skins/Default/1080i/intro_skip_dialog.xml').getroot()
        self.assertEqual(list(root.iter('control')),[])
    def test_light_button_color(self):
        settings_values.update({'customize.theme':'Light','customize.button_color_light':'3'})
        d=IntroSkipDialog('intro_skip_dialog.xml',str(BASE),'Default','1080i')
        d.configure('intro',123);d.onInit()
        self.assertEqual(d._button.kwargs['textColor'],color.COLOR_VALUES['light'][3])
        self.assertIn('modern_light',d._button.kwargs['focusTexture'])
    def test_dark_button_color(self):
        settings_values.update({'customize.theme':'Dark','customize.button_color':'5'})
        d=IntroSkipDialog('intro_skip_dialog.xml',str(BASE),'Default','1080i')
        d.configure('intro',123);d.onInit()
        self.assertEqual(d._button.kwargs['textColor'],color.COLOR_VALUES['dark'][5])
    def test_two_palettes_have_unique_colors(self):
        self.assertEqual(len(color.COLOR_NAMES),7)
        self.assertEqual(len(set(color.COLOR_VALUES['dark'])),7)
        self.assertEqual(len(set(color.COLOR_VALUES['light'])),7)
    def test_small_button_correct_first_position(self):
        settings_values.update({'customize.size':'0','customize.position':'3'})
        d=IntroSkipDialog('intro_skip_dialog.xml',str(BASE),'Default','1080i')
        d.configure('intro',90);d.onInit()
        self.assertEqual(d._button.args[:4],button_assets.button_layout(3,0))
    def test_big_button_correct_first_position(self):
        settings_values.update({'customize.size':'2','customize.position':'1'})
        d=IntroSkipDialog('intro_skip_dialog.xml',str(BASE),'Default','1080i')
        d.configure('movie_outro',190);d.onInit()
        self.assertEqual(d._button.args[:4],button_assets.button_layout(1,2))
    def test_icon_only_button_has_no_label(self):
        settings_values.update({'customize.contents':'2'})
        d=IntroSkipDialog('intro_skip_dialog.xml',str(BASE),'Default','1080i')
        d.configure('recap',90);d.onInit()
        self.assertEqual(d._button.args[4],'')
    def test_no_timestamp_writes(self):
        code=(BASE/'resources/lib/introdb.py').read_text()
        self.assertNotIn('sqlite',code)
        self.assertNotIn('cache_path',code)

class CinemetaTests(unittest.TestCase):
    def setUp(self):
        self.orig=cinemeta.requests.get
        self.calls=[]
    def tearDown(self):cinemeta.requests.get=self.orig
    def mock(self,metas):
        class Resp:
            def raise_for_status(self):pass
            def json(self):return {'metas':metas}
        def getter(url,timeout=None,headers=None):
            self.calls.append(url)
            return Resp()
        cinemeta.requests.get=getter
    def test_user_supplied_rings_json_suffix(self):
        self.mock([
            {'type':'series','id':'tt7631058','name':'The Lord of the Rings: The Rings of Power','releaseInfo':'2022-'},
            {'type':'series','id':'tt7745956','name':'She-Ra and the Princesses of Power','releaseInfo':'2018-2020','score':99},
            {'type':'series','id':'tt0126171','name':'She-Ra: Princess of Power','releaseInfo':'1985-1987'},
            {'type':'series','id':'tt8263804','name':'Abuse of Power','releaseInfo':'2018-','score':1000}
        ])
        self.assertEqual(cinemeta.lookup_imdb('The Rings of Power','episode'),'tt7631058')
        self.assertIn('/catalog/series/top/search=The%20Rings%20of%20Power.json',self.calls[0])
    def test_movie_search(self):
        self.mock([{'type':'movie','id':'tt1375666','name':'Inception','releaseInfo':'2010'}])
        self.assertEqual(cinemeta.lookup_imdb('Inception','movie',2010),'tt1375666')
        self.assertIn('/catalog/movie/top/search=Inception.json',self.calls[0])
    def test_title_mismatch_is_rejected(self):
        self.mock([{'type':'series','id':'tt7745956','name':'She-Ra and the Princesses of Power'}])
        self.assertIsNone(cinemeta.lookup_imdb('The Rings of Power','episode'))
    def test_wrong_media_type_rejected(self):
        self.mock([{'type':'series','id':'tt1375666','name':'Inception'}])
        self.assertIsNone(cinemeta.lookup_imdb('Inception','movie'))
    def test_movie_year_mismatch_rejected(self):
        self.mock([{'type':'movie','id':'tt0111111','name':'Dune','releaseInfo':'1984'}])
        self.assertIsNone(cinemeta.lookup_imdb('Dune','movie',2021))
    def test_same_title_ambiguous_no_year(self):
        self.mock([{'type':'movie','id':'tt0111111','name':'Dune','releaseInfo':'1984'},
                   {'type':'movie','id':'tt1160419','name':'Dune','releaseInfo':'2021'}])
        self.assertIsNone(cinemeta.lookup_imdb('Dune','movie'))
    def test_same_title_resolves_using_year(self):
        self.mock([{'type':'movie','id':'tt0111111','name':'Dune','releaseInfo':'1984'},
                   {'type':'movie','id':'tt1160419','name':'Dune','releaseInfo':'2021'}])
        self.assertEqual(cinemeta.lookup_imdb('Dune','movie',2021),'tt1160419')
    def test_missing_candidate_year_rejected_when_year_required(self):
        self.mock([{'type':'movie','id':'tt1160419','name':'Dune'}])
        self.assertIsNone(cinemeta.lookup_imdb('Dune','movie',2021))
    def test_ambiguous_series_identical_titles_rejected(self):
        self.mock([{'type':'series','id':'tt1111111','name':'The Office'},
                   {'type':'series','id':'tt2222222','name':'The Office'}])
        self.assertIsNone(cinemeta.lookup_imdb('The Office','episode'))
    def test_duplicate_ids_are_safe(self):
        self.mock([{'type':'movie','id':'tt1375666','name':'Inception'},
                   {'type':'movie','imdb_id':'tt1375666','name':'Inception'}])
        self.assertEqual(cinemeta.lookup_imdb('Inception','movie'),'tt1375666')
    def test_disagreeing_id_fields_rejected(self):
        self.mock([{'type':'movie','id':'tt1375666','imdb_id':'tt2222222','name':'Inception'}])
        self.assertIsNone(cinemeta.lookup_imdb('Inception','movie'))
    def test_encoded_title_query(self):
        self.mock([{'type':'movie','id':'tt1234567','name':'Amélie','releaseInfo':'2001'}])
        self.assertEqual(cinemeta.lookup_imdb('Amélie','movie',2001),'tt1234567')
        self.assertIn('Am%C3%A9lie',self.calls[0])
    def test_no_persistent_or_in_memory_lookup_cache(self):
        self.mock([{'type':'series','id':'tt7631058','name':'The Rings of Power'}])
        self.assertEqual(cinemeta.lookup_imdb('The Rings of Power','episode'),'tt7631058')
        self.assertEqual(cinemeta.lookup_imdb('The Rings of Power','episode'),'tt7631058')
        self.assertEqual(len(self.calls),2)
    def test_invalid_queries_no_request(self):
        self.mock([])
        self.assertIsNone(cinemeta.lookup_imdb('','movie'))
        self.assertIsNone(cinemeta.lookup_imdb('Test','game'))
        self.assertEqual(self.calls,[])
    def test_network_error_no_exception(self):
        def raise_error(*args,**kwargs):raise cinemeta.requests.exceptions.ConnectionError('offline')
        cinemeta.requests.get=raise_error
        self.assertIsNone(cinemeta.lookup_imdb('Inception','movie',2010))
    def test_invalid_json_no_exception(self):
        self.mock([])
        self.assertIsNone(cinemeta.lookup_imdb('Inception','movie'))

class PlaybackTests(unittest.TestCase):
    def setUp(self):
        self.p=Player()
        self.p.playback_generation=3
        self.key=(3,'episode','','1','3')
        self.p._episode_key=self.key
        settings_values.update({'general.use_intro':True,'general.use_recap':True,
                                'general.use_outro':True,'general.use_movie_credits':True})
        self.old_lookup=cinemeta.lookup_imdb
        cinemeta.lookup_imdb=lambda *args,**kwargs:'tt7631058'
    def tearDown(self):cinemeta.lookup_imdb=self.old_lookup
    def test_introdb_source_weaker_than_named_chapter(self):
        self.p._remember_segment('intro',(74,147),{'source':'chapter_explicit'})
        self.p._remember_segment('intro',(76,167),{'source':'introdb'})
        self.assertEqual(self.p.intro,(74,147))
    def test_worker_result_applied_on_service_thread(self):
        self.p.identifier.introdb_adapter.get_episode_data=lambda *a:{'intro':{'start_sec':76,'end_sec':167}}
        self.p._introdb_worker(self.key,'The Rings of Power')
        self.assertIsNone(self.p.intro)
        self.assertTrue(self.p.apply_ready_network_results())
        self.assertEqual(self.p._episode_key[2],'tt7631058')
        self.assertAlmostEqual(tools.convert_time_to_seconds(self.p.intro[0]),76)
    def test_no_timestamp_cached_after_result_applied(self):
        self.p.identifier.introdb_adapter.get_episode_data=lambda *a:{'intro':{'start_sec':76,'end_sec':167}}
        self.p._introdb_worker(self.key,'The Rings of Power')
        self.p.apply_ready_network_results()
        self.assertEqual(self.p._network_results,{})
    def test_old_playback_result_is_discarded(self):
        self.p.identifier.introdb_adapter.get_episode_data=lambda *a:{'intro':{'start_sec':76,'end_sec':167}}
        self.p.playback_generation=4
        self.p._introdb_worker(self.key,'The Rings of Power')
        self.assertFalse(self.p.apply_ready_network_results())
        self.assertIsNone(self.p.intro)
    def test_unmatched_title_preserves_chapters(self):
        cinemeta.lookup_imdb=lambda *a,**k:None
        self.p._remember_segment('recap',(5,74),{'source':'chapter_explicit'})
        self.p._introdb_worker(self.key,'Unknown series')
        self.assertIsNone(self.p.intro)
        self.assertEqual(self.p.recap,(5,74))
    def test_movie_lookup_produces_credits(self):
        self.p._episode_key=(3,'movie','','0','0')
        cinemeta.lookup_imdb=lambda *a,**k:'tt1375666'
        self.p.identifier.introdb_adapter.get_movie_data=lambda *a:{'outro':{'start_sec':3000,'end_sec':3500}}
        self.p._introdb_worker(self.p._episode_key,'Inception',2010)
        self.p.apply_ready_network_results()
        self.assertIsNotNone(self.p.movie_outro)
    def test_onav_uses_title_not_kodi_imdb_lookup(self):
        # VideoTag.getIMDBNumber raises; this must still work.
        self.p.identifier.chapter_adapter.get_points=lambda *a: [(74,147)] if a[-1]=='intro' else None
        self.p.identifier.chapter_adapter.last_match_kind='chapter_explicit'
        self.p.onAVStarted()
        self.assertEqual(self.p.intro,(74,147))
    def test_filename_title_fallback(self):
        filename='https://video/Show.Name.S02E05.1080p.WEB.mkv?token=private'
        self.assertEqual(self.p._filename_title('episode',filename),'Show Name')
    def test_disable_intro(self):
        settings_values['general.use_intro']=False
        self.p._apply_introdb_data('episode', {'intro':{'start_sec':20,'end_sec':80},
                                                'recap':{'start_sec':3,'end_sec':19}})
        self.assertIsNone(self.p.intro)
        self.assertIsNotNone(self.p.recap)
    def test_nonblocking_worker_thread(self):
        event=threading.Event()
        self.p.identifier.introdb_adapter.get_episode_data=lambda *a: (event.wait(.8) or True) and {'intro':{'start_sec':76,'end_sec':167}}
        start=time.monotonic()
        self.p._launch_introdb(self.key,'The Rings of Power')
        self.assertLess(time.monotonic()-start,.1)
        self.assertIn(self.key,self.p._requested_keys)
        event.set()
        for i in range(100):
            self.p.apply_ready_network_results()
            if self.p.intro:break
            time.sleep(.005)
        self.assertIsNotNone(self.p.intro)

if __name__=='__main__':unittest.main(verbosity=2)
