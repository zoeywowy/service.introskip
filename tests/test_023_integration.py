"""Offline Kodi 22 integration, performance and multi-source tests."""
import os
import sys
import types
import time
import unittest
import threading
import tempfile
import gzip
import hashlib
import io
import json
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
settings_values = {
    'general.use_intro': True, 'general.use_recap': True,
    'general.use_outro': True, 'general.use_movie_credits': True, 'general.use_preview': False,
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
    def __init__(self):pass
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
        self.show_count=0;self.close_count=0
    def addControl(self,c):self.controls.append(c)
    def removeControl(self,c):self.controls.remove(c)
    def setFocus(self,c):self.focus=c
    def setProperty(self,k,v):self.properties[k]=v
    def getProperty(self,k):return self.properties.get(k,'')
    def show(self):self.show_count+=1
    def close(self):self.close_count+=1

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

from resources.lib import tools,button_assets,color,cinemeta,theintrodb,http_client,segment_policy
from resources.lib.introdb_open_data import IntroDBOpenDataAdapter
from resources.lib.player import Player
from resources.lib.skip_dialog import IntroSkipDialog
from resources.lib.kodi_native import KodiNativeMonitor

class KodiNativeMonitorTests(unittest.TestCase):
    def test_chapter_property_is_queued_once(self):
        monitor = KodiNativeMonitor()
        monitor.onNotification(
            "xbmc", "Player.OnPropertyChanged",
            json.dumps({"property": {"chapter": 2}})
        )
        self.assertEqual(monitor.take_changes(), {"chapters"})
        self.assertEqual(monitor.take_changes(), set())

    def test_unrelated_player_property_is_ignored(self):
        monitor = KodiNativeMonitor()
        monitor.onNotification(
            "xbmc", "Player.OnPropertyChanged",
            json.dumps({"property": {"speed": 2}})
        )
        self.assertEqual(monitor.take_changes(), set())

    def test_other_notifications_are_ignored(self):
        monitor = KodiNativeMonitor()
        monitor.onNotification(
            "xbmc", "Player.OnAVStarted",
            json.dumps({"property": {"chapter": 2}})
        )
        self.assertEqual(monitor.take_changes(), set())


class DialogLifecycleTests(unittest.TestCase):
    def test_close_is_noop_until_dialog_has_been_shown(self):
        dialog = IntroSkipDialog("intro_skip_dialog.xml", str(BASE))
        dialog.close()
        self.assertEqual(dialog.close_count, 0)
        self.assertFalse(dialog._is_open)

    def test_shown_dialog_closes_once(self):
        dialog = IntroSkipDialog("intro_skip_dialog.xml", str(BASE))
        dialog.show()
        self.assertTrue(dialog._is_open)
        dialog.close()
        self.assertFalse(dialog._is_open)
        self.assertEqual(dialog.close_count, 1)
        dialog.close()
        self.assertEqual(dialog.close_count, 1)


class ServiceLifecycleTests(unittest.TestCase):
    def test_idle_service_does_not_construct_native_skip_window(self):
        player = Player()
        self.assertIsNone(player.dialog)
        player.shutdown()
        self.assertIsNone(player.dialog)

    def test_playback_dialog_releases_native_player_reference(self):
        player = Player()
        self.assertIsNone(player.get_dialog())
        dialog = player.get_dialog(create=True)
        self.assertIs(dialog.player, player)
        self.assertIs(player.get_dialog(), dialog)
        dialog.show()
        player.shutdown()
        self.assertIsNone(player.dialog)
        self.assertIsNone(dialog.player)
        self.assertFalse(dialog._is_open)
        self.assertEqual(dialog.close_count, 1)
        self.assertIsNone(player.get_dialog())

    def test_native_gui_is_not_needed_for_playback_setup(self):
        player = Player()
        original_launch = player._launch_introdb
        original_chapters = player._read_local_chapters
        try:
            player._launch_introdb = lambda *args, **kwargs: None
            player._read_local_chapters = lambda *args, **kwargs: None
            player.onAVStarted()
            self.assertIsNone(player.dialog)
        finally:
            player._launch_introdb = original_launch
            player._read_local_chapters = original_chapters
            player.shutdown()

    def test_playback_worker_exits_on_shutdown(self):
        player = Player()
        started = threading.Event()
        original = cinemeta.lookup_imdb
        try:
            def slow_lookup(*args, **kwargs):
                started.set()
                player._shutdown_event.wait(4)
                return None
            cinemeta.lookup_imdb = slow_lookup
            key = (0, 'episode', '', '1', '2')
            player._launch_introdb(key, 'Test Series')
            self.assertTrue(started.wait(1))
            start = time.monotonic()
            player.shutdown()
            self.assertLess(time.monotonic() - start, 1)
            self.assertFalse(any(t.is_alive() for t in player._workers))
        finally:
            cinemeta.lookup_imdb = original
            player.shutdown()

    def test_open_data_sync_worker_is_joined_on_shutdown(self):
        player = Player()
        adapter = player.identifier.introdb_open_data
        entered = threading.Event()
        def sync_until_cancelled():
            entered.set()
            adapter._cancel_event.wait(2.0)
        adapter.sync_if_needed = sync_until_cancelled
        worker = adapter.start_background_sync()
        self.assertTrue(entered.wait(1))
        player.shutdown()
        self.assertFalse(worker.is_alive())

    def test_open_data_adapter_is_shared_across_threads(self):
        player = Player()
        found = []
        threads = [threading.Thread(target=lambda: found.append(player.identifier.introdb_open_data))
                   for _ in range(12)]
        for worker in threads:
            worker.start()
        for worker in threads:
            worker.join(timeout=1)
        self.assertEqual(len(found), 12)
        self.assertTrue(all(adapter is found[0] for adapter in found))
        player.shutdown()


class HTTPClientTests(unittest.TestCase):
    def test_json_query_uses_standard_library_and_encodes_parameters(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, size=-1): return b'{"ok":true}'
        calls = []
        old = http_client.urlopen
        http_client.urlopen = lambda request, timeout=None: (
            calls.append((request.full_url, timeout)) or Response()
        )
        try:
            data = http_client.get_json(
                "https://example.test/search",
                params={"title": "Amélie"},
                timeout=3,
            )
        finally:
            http_client.urlopen = old
        self.assertEqual(data, {"ok": True})
        self.assertIn("title=Am%C3%A9lie", calls[0][0])
        self.assertEqual(calls[0][1], 3)

    def test_download_streams_chunks_and_hashes_file(self):
        chunks = [b"first-", b"second", b""]
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, size=-1): return chunks.pop(0)
        old = http_client.urlopen
        http_client.urlopen = lambda request, timeout=None: Response()
        try:
            with tempfile.TemporaryDirectory() as folder:
                destination = os.path.join(folder, "snapshot.gz")
                size, digest = http_client.download_to_file(
                    "https://example.test/snapshot.gz", destination
                )
                with open(destination, "rb") as handle:
                    payload = handle.read()
        finally:
            http_client.urlopen = old
        self.assertEqual(payload, b"first-second")
        self.assertEqual(size, len(payload))
        self.assertEqual(digest, hashlib.sha256(payload).hexdigest())

    def test_introdb_live_http_failure_is_handled_without_requests_dependency(self):
        player = Player()
        original = http_client.get_json
        try:
            def offline(*args, **kwargs):
                raise http_client.HTTPTransportError('offline')
            http_client.get_json = offline
            self.assertIsNone(player.identifier.introdb_adapter.get_episode_data('tt7631058',1,3))
        finally:
            http_client.get_json = original
            player.shutdown()

    def test_cancelled_download_removes_partial_file(self):
        event = threading.Event()
        class Response:
            def __init__(self): self.sent = False
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, size=-1):
                if not self.sent:
                    self.sent = True
                    event.set()
                    return b"partial"
                return b""
        old = http_client.urlopen
        http_client.urlopen = lambda request, timeout=None: Response()
        try:
            with tempfile.TemporaryDirectory() as folder:
                destination = os.path.join(folder, "partial.gz")
                with self.assertRaises(http_client.DownloadCancelled):
                    http_client.download_to_file(
                        "https://example.test/large.gz",
                        destination,
                        cancel_event=event,
                    )
                self.assertFalse(os.path.exists(destination))
        finally:
            http_client.urlopen = old


class DatabaseShutdownTests(unittest.TestCase):
    def test_cancel_interrupts_in_progress_sqlite_operation(self):
        class FakeSQLiteConnection:
            def __init__(self):
                self.interrupted = False
            def interrupt(self):
                self.interrupted = True
        with tempfile.TemporaryDirectory() as folder:
            adapter = IntroDBOpenDataAdapter(profile_path=folder)
            connection = FakeSQLiteConnection()
            adapter._active_db = connection
            adapter.cancel_sync()
            self.assertTrue(adapter._cancel_event.is_set())
            self.assertTrue(connection.interrupted)


class PackageTests(unittest.TestCase):
    def setUp(self):
        settings_values.update({'customize.theme':'Dark', 'customize.size':'1',
                                'customize.position':'0', 'customize.contents':'0',
                                'customize.button_color':'0', 'customize.button_color_light':'0',
                                'general.use_intro':True,'general.use_recap':True,
                                'general.use_outro':True,'general.use_movie_credits':True})
    def test_manifest_version_and_dependencies(self):
        root=ET.parse(BASE/'addon.xml').getroot()
        version_parts = root.attrib['version'].split('.')
        self.assertEqual(len(version_parts), 3)
        self.assertTrue(all(part.isdigit() for part in version_parts))
        deps=[item.attrib['addon'] for item in root.findall('requires/import')]
        self.assertEqual(deps,['xbmc.python'])
        for module in ('cinemeta.py','introdb.py','introdb_open_data.py','theintrodb.py'):
            source=(BASE/'resources/lib'/module).read_text()
            self.assertNotIn('import requests',source)
    def test_network_timeouts_are_bounded_for_service_shutdown(self):
        modules = ('http_client.py','cinemeta.py','introdb.py','theintrodb.py','introdb_open_data.py')
        for module in modules:
            source=(BASE/'resources/lib'/module).read_text()
            self.assertIn('timeout=3',source,module)

    def test_settings_no_advanced_or_diagnostics(self):
        root=ET.parse(BASE/'resources/settings.xml').getroot()
        cats=root.findall('category')
        self.assertEqual(len(cats),3)
        ids=[item.attrib['id'] for item in root.iter('setting')]
        for old in ('general.inspect_chapters','advanced.playback_diagnostics',
                    'api.omdb_api_key','general.use_introdb','general.use_chapters'):
            self.assertNotIn(old,ids)
        self.assertIn('general.show_notifications',ids)
        self.assertIn('general.use_preview',ids)
        self.assertIn('skip.preview_mode',ids)
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
        self.assertIn('sqlite3', (BASE/'resources/lib/introdb_open_data.py').read_text())

class CinemetaTests(unittest.TestCase):
    def setUp(self):
        self.orig=cinemeta.http_client.get_json
        self.calls=[]
    def tearDown(self):cinemeta.http_client.get_json=self.orig
    def mock(self,metas):
        def getter(url,params=None,timeout=None,headers=None):
            self.calls.append(url)
            return {'metas':metas}
        cinemeta.http_client.get_json=getter
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
        def raise_error(*args,**kwargs):raise cinemeta.http_client.HTTPTransportError('offline')
        cinemeta.http_client.get_json=raise_error
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
        self.old_theintrodb=self.p.identifier.theintrodb_adapter.get_media_data
        self.old_bulk=self.p.identifier.introdb_open_data.get_episode_data
        cinemeta.lookup_imdb=lambda *args,**kwargs:'tt7631058'
        self.p.identifier.theintrodb_adapter.get_media_data=lambda *args,**kwargs:None
        self.p.identifier.introdb_open_data.get_episode_data=lambda *args,**kwargs:None
    def tearDown(self):
        cinemeta.lookup_imdb=self.old_lookup
        self.p.identifier.theintrodb_adapter.get_media_data=self.old_theintrodb
        self.p.identifier.introdb_open_data.get_episode_data=self.old_bulk
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

class MultiSourceTests(unittest.TestCase):
    def test_theintrodb_preserves_multiple_ranges_and_null_boundaries(self):
        data = {
            'intro': [
                {'start_ms': None, 'end_ms': 60000},
                {'start_ms': 70000, 'end_ms': 90000},
            ],
            'credits': [
                {'start_ms': 3000000, 'end_ms': 3300000},
                {'start_ms': 3400000, 'end_ms': None},
            ],
        }
        intro = theintrodb.TheIntroDBAdapter.get_ranges_from_data(data, 'intro', 3600)
        credits = theintrodb.TheIntroDBAdapter.get_ranges_from_data(data, 'credits', 3600)
        self.assertEqual(intro, [(0.0, 60.0), (70.0, 90.0)])
        self.assertEqual(credits, [(3000.0, 3300.0), (3400.0, 3600.0)])

    def test_theintrodb_movie_lookup_uses_imdb_duration_and_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            adapter = theintrodb.TheIntroDBAdapter(profile_path=folder)
            calls = []
            old = theintrodb.http_client.get_json
            def fake_get(url, params=None, timeout=None, headers=None):
                calls.append((url, params, timeout))
                return {'type':'movie','credits':[{'start_ms':3000000,'end_ms':None}]}
            theintrodb.http_client.get_json = fake_get
            try:
                first = adapter.get_media_data('tt1375666', is_movie=True, duration_ms=7200000)
                second = adapter.get_media_data('tt1375666', is_movie=True, duration_ms=7200000)
            finally:
                theintrodb.http_client.get_json = old
            self.assertEqual(first, second)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1]['imdb_id'], 'tt1375666')
            self.assertEqual(calls[0][1]['duration_ms'], 7200000)
            self.assertEqual(calls[0][1]['details'], 'true')

    def test_open_data_download_builds_local_index_and_skips_unchanged_snapshot(self):
        segments_csv = (
            'imdb_id,is_movie,season,episode,segment,start_ms,end_ms,confidence,submission_count,updated_at\n'
            'tt7631058,f,1,3,intro,76000,167000,0.92,14,2026-11-12T00:00:00Z\n'
            'tt7631058,f,1,3,recap,5000,74000,0.85,8,2026-11-12T00:00:00Z\n'
            'tt1375666,t,0,0,outro,3000000,3300000,0.9,11,2026-11-12T00:00:00Z\n'
        ).encode('utf-8')
        segmentless_csv = (
            'imdb_id,is_movie,season,episode,segment,updated_at\n'
            'tt7631058,f,1,4,intro,2026-11-12T00:00:00Z\n'
        ).encode('utf-8')
        segments_gz = gzip.compress(segments_csv)
        segmentless_gz = gzip.compress(segmentless_csv)
        manifest = {
            'generated_at':'2026-11-12T00:00:00Z',
            'license':'ODbL-1.0',
            'files':{
                'segments.csv.gz':{'size':len(segments_gz),'sha256':hashlib.sha256(segments_gz).hexdigest()},
                'segmentless.csv.gz':{'size':len(segmentless_gz),'sha256':hashlib.sha256(segmentless_gz).hexdigest()},
            },
        }
        manifest_bytes = json.dumps(manifest).encode('utf-8')
        responses = {
            'https://data.introdb.app/latest/manifest.json': manifest_bytes,
            'https://data.introdb.app/latest/segments.csv.gz': segments_gz,
            'https://data.introdb.app/latest/segmentless.csv.gz': segmentless_gz,
        }
        calls = []
        module = __import__('resources.lib.introdb_open_data', fromlist=['http_client'])
        old_get_bytes = module.http_client.get_bytes
        old_download = module.http_client.download_to_file
        def fake_get_bytes(url, timeout=None, headers=None, params=None):
            calls.append(url)
            return responses[url]
        def fake_download(url, destination, timeout=None, cancel_event=None, chunk_size=65536):
            calls.append(url)
            payload = responses[url]
            with open(destination, 'wb') as handle:
                handle.write(payload)
            return len(payload), hashlib.sha256(payload).hexdigest()
        module.http_client.get_bytes = fake_get_bytes
        module.http_client.download_to_file = fake_download
        try:
            with tempfile.TemporaryDirectory() as folder:
                adapter = IntroDBOpenDataAdapter(profile_path=folder)
                self.assertTrue(adapter.sync_if_needed())
                episode = adapter.get_episode_data('tt7631058', 1, 3)
                self.assertEqual(episode['intro']['start_ms'], 76000)
                self.assertEqual(episode['recap']['end_ms'], 74000)
                absent = adapter.get_episode_data('tt7631058', 1, 4)
                self.assertTrue(absent['no_intro'])
                self.assertFalse(adapter.sync_if_needed())

                # A new Kodi session must reject a damaged local cache even when
                # the remote manifest has not changed, then rebuild it safely.
                with open(adapter.db_path, 'wb') as damaged:
                    damaged.write(b'not a sqlite database')
                recovered = IntroDBOpenDataAdapter(profile_path=folder)
                self.assertTrue(recovered.sync_if_needed())
                repaired = recovered.get_episode_data('tt7631058', 1, 3)
                self.assertEqual(repaired['intro']['start_ms'], 76000)
        finally:
            module.http_client.get_bytes = old_get_bytes
            module.http_client.download_to_file = old_download
        self.assertEqual(calls.count('https://data.introdb.app/latest/manifest.json'), 3)
        self.assertEqual(calls.count('https://data.introdb.app/latest/segments.csv.gz'), 2)
        self.assertEqual(calls.count('https://data.introdb.app/latest/segmentless.csv.gz'), 2)

    def test_preview_theintrodb_multiple_ranges_are_confirmation_only(self):
        settings_values['general.use_preview'] = True
        player = Player()
        data = {'preview':[
            {'start_ms': 120000, 'end_ms': 160000, 'confidence': 0.9},
            {'start_ms': 250000, 'end_ms': 280000, 'confidence': 0.9},
        ]}
        try:
            found = player._apply_theintrodb_data('episode', data, 360000, 360)
            self.assertIn('preview', found)
            self.assertEqual(player.get_segments()['preview'],
                             [(120.0, 160.0), (250.0, 280.0)])
            evidence = player.evidence_for('preview',(120.0,160.0))
            self.assertEqual(evidence['source'], 'theintrodb')
            self.assertFalse(segment_policy.can_auto_skip('auto', evidence['source']))
        finally:
            player.shutdown()

    def test_preview_native_chapters_respect_toggle(self):
        player = Player()
        adapter = player.identifier.chapter_adapter
        calls = []
        adapter.last_match_kind = 'chapter_explicit'
        adapter.get_points = lambda *args: (calls.append(args[-1]) or
                                            ([(210.0, 240.0)] if args[-1] == 'preview' else None))
        try:
            settings_values['general.use_preview'] = True
            player._read_local_chapters('episode', '', 1, 3)
            self.assertEqual(player.get_segments()['preview'], [(210.0, 240.0)])
            player.reset_segment('preview')
            calls.clear()
            settings_values['general.use_preview'] = False
            player._read_local_chapters('episode', '', 1, 3)
            self.assertNotIn('preview', calls)
            self.assertEqual(player.get_segments()['preview'], [])
        finally:
            player.shutdown()

    def test_delayed_preview_chapter_refresh(self):
        settings_values['general.use_preview'] = True
        player = Player()
        adapter = player.identifier.chapter_adapter
        adapter._get_chapters_multiple_methods = lambda force=False: [{'title':'Next Episode Preview'}]
        adapter.get_points = lambda *args: ([(275.0,310.0)] if args[-1]=='preview' else None)
        adapter.last_match_kind = 'chapter_explicit'
        player._media_type = 'episode'
        try:
            self.assertTrue(player.refresh_chapter_segments(force=True))
            self.assertEqual(player.get_segments()['preview'], [(275.0, 310.0)])
        finally:
            player.shutdown()

    def test_preview_provider_maps_to_preview_segment(self):
        settings_values['general.use_preview'] = True
        player = Player()
        player.identifier.theintrodb_adapter.get_ranges_from_data = (
            lambda data, segment, duration: [(100.0, 130.0)] if segment == 'preview' else []
        )
        player.identifier.theintrodb_adapter.evidence_for = lambda *args: {
            'source':'theintrodb','confidence':0.9,'submissions':5
        }
        found = player._apply_theintrodb_data('episode', {'preview':[{}]}, 300000, 300)
        self.assertIn('preview', found)
        self.assertEqual(player.preview, (100.0, 130.0))



if __name__=='__main__':unittest.main(verbosity=2)
