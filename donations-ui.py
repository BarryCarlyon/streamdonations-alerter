import donations
import wx
import wx.lib.agw.floatspin as FS
import sys, os
import ConfigParser
from threading import Thread

class RedirectText(object):
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl
 
    def write(self, string):
        #self.out.SetInsertionPoint()
        wx.CallAfter(self.out.AppendText, string)

class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Donation Tracker', size=(500, 300), style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.SetBackgroundColour((255, 255, 255))
        
        # events
        self.Bind(wx.EVT_CLOSE, self.nativeClose)
        
        # icon
        icon = wx.Icon(resourcePath('icon.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        # interface
        logo_image = wx.Image(resourcePath('logo.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        logo = wx.StaticBitmap(self, -1, logo_image, (logo_image.GetWidth(), logo_image.GetHeight()))
        
        button_panel = wx.Panel(self, -1)  # style=wx.SUNKEN_BORDER
        
        config_button = wx.Button(button_panel, -1, label='Configure', size=(200, -1))
        config_button.Bind(wx.EVT_BUTTON, self.openConfigWindowButton)
        
        run_button = wx.Button(button_panel, -1, label='Run', size=(200, -1))
        run_button.Bind(wx.EVT_BUTTON, self.runButton)
        
        # layout
        
        window_layout = wx.BoxSizer(wx.VERTICAL)
        
        window_layout.Add(logo , 1)
        
        # button layout
        button_layout = wx.BoxSizer(wx.HORIZONTAL)
        
        button_layout.Add(config_button, border=10, flag=wx.ALIGN_LEFT | wx.RIGHT)
        button_layout.Add(run_button, border=10, flag=wx.ALIGN_RIGHT | wx.LEFT)
        
        button_panel.SetSizer(button_layout)
        
        # add buttons to window_layout
        window_layout.Add(button_panel, border=20, flag=wx.ALIGN_CENTER | wx.BOTTOM)
        
        window_layout.AddStretchSpacer()
        
        self.SetSizer(window_layout)
        
        self.Center()
        
        #config_button.Disable()
        run_button.SetFocus()
        
    def openConfigWindowButton(self, event):
        config_frame = ConfigWindow(self)
        config_frame.Show()
        
        self.Hide()
        
    def runButton(self, event):
        run_frame = RunWindow(self)
        run_frame.Show()
        
        self.Hide()
        
    def nativeClose(self, event):
#         dlg = wx.MessageDialog(self, "Do you really want to close this application?", "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
#         result = dlg.ShowModal()
#         dlg.Destroy()
#         if result == wx.ID_OK:
#             self.Destroy()
        self.Destroy()
        os._exit(1)
        
class ConfigWindow(wx.Frame):
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        # window setup
        wx.Frame.__init__(self, None, title='Configure', size=(800, 600), style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.SetBackgroundColour((255, 255, 255))
        self.Bind(wx.EVT_CLOSE, self.nativeClose)
        
        # icon
        self.icon = wx.Icon(resourcePath('icon.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        
        # config
        self.config = ConfigParser.ConfigParser(allow_no_value = True, defaults={
              'channel': '',
              'api-key': '',
              'dailydonationlist': 'false',
              'dailyrecentdonation': 'false',
              'dailytopdonation': 'false',
              'soundminimum': '1.00',
              'fileminimum': '1.00',
              'donationlistamount': '5',
              'playwav': 'true',
              'donationwav': 'sound.wav',
              'topdonationwav': 'sound.wav',
              'donationformatting': '{currencySymbol}{amount} - {note} - From: {username}',
              'topdonationformatting': '{currencySymbol}{amount} - From: {username}',
              'donationlistformatting': '{username}: {currencySymbol}{amount}',
              'consoleformatting': '{currencySymbol}{amount} - {note} - From: {username}, using {processor}',
              })
        self.config.read(resourcePath('settings.ini', user=True))
        
        if not self.config.has_section("Donation Tracker Config"):
            self.config.add_section("Donation Tracker Config")
        
        # interface
        self.scroll_window = wx.ScrolledWindow(self, -1)
        
        self.main_panel = wx.Panel(self.scroll_window, -1)
        
        self.channel_text_box_label = wx.StaticText(self.main_panel, label="Channel - your channel name on Twitch")
        self.channel_text_box = wx.TextCtrl(self.main_panel, 1, size=(200,-1))
        self.channel_text_box.SetValue(self.config.get("Donation Tracker Config", 'channel'))
        
        self.api_key_text_box_label = wx.StaticText(self.main_panel, label="API Key - your API key from StreamDonations.net")
        self.api_key_text_box = wx.TextCtrl(self.main_panel, 1, size=(300,-1))
        self.api_key_text_box.SetValue(self.config.get("Donation Tracker Config", 'api-key'))
        
        
        self.clear_files_label = wx.StaticText(self.main_panel, label="Clear the donation lists")
        self.clear_donation_list_checkbox = wx.CheckBox(self.main_panel, 1, "Daily Donations List - clear the donations list on start")
        self.clear_donation_list_checkbox.SetValue(self.config.getboolean("Donation Tracker Config", 'dailydonationlist'))
        
        self.clear_recent_donation_checkbox = wx.CheckBox(self.main_panel, 1, "Most Recent Donation - clear the most recent donation list on start")
        self.clear_recent_donation_checkbox.SetValue(self.config.getboolean("Donation Tracker Config", 'dailyrecentdonation'))
        
        self.clear_top_donation_checkbox = wx.CheckBox(self.main_panel, 1, "Daily Top Donation - clear the top donation list on start")
        self.clear_top_donation_checkbox.SetValue(self.config.getboolean("Donation Tracker Config", 'dailytopdonation'))
        
        
        self.sound_min_text_box_label = wx.StaticText(self.main_panel, label="Alarm Minimum - minimum donation amount before triggering alarm")
        self.sound_min_text_box = FS.FloatSpin(self.main_panel, 1, size=(100,-1), min_val=0, max_val=1000, increment=1.0, digits=1)
        self.sound_min_text_box.SetValue(self.config.getfloat("Donation Tracker Config", 'soundminimum'))
        
        self.file_min_text_box_label = wx.StaticText(self.main_panel, label="File Minimum - minimum donation amount before adding to the list")
        self.file_min_text_box = FS.FloatSpin(self.main_panel, 1, size=(100,-1), min_val=0, max_val=1000, increment=1.0, digits=1)
        self.file_min_text_box.SetValue(self.config.getfloat("Donation Tracker Config", 'fileminimum'))
        
        
        self.donation_list_amount_box_label = wx.StaticText(self.main_panel, label="Donation List Amount - number of donations to include in the list")
        self.donation_list_amount_box = wx.SpinCtrl(self.main_panel, 1, size=(100,-1), min=0, max=30)
        self.donation_list_amount_box.SetValue(self.config.getint("Donation Tracker Config", 'donationlistamount'))
        
        
        self.play_sound_checkbox = wx.CheckBox(self.main_panel, 1, "Play Sound - Play a sounds for new donations")
        self.play_sound_checkbox.SetValue(self.config.getboolean("Donation Tracker Config", 'playwav'))
        
        self.donation_sound_text_box_label = wx.StaticText(self.main_panel, label="New Donation Sound - sound to play with a new donation. Enter the file name. MUST be in WAV format")
        self.donation_sound_text_box = wx.TextCtrl(self.main_panel, 1, size=(400,-1))
        self.donation_sound_text_box.SetValue(self.config.get("Donation Tracker Config", 'donationwav'))
        
        self.top_donation_sound_text_box_label = wx.StaticText(self.main_panel, label="New Top Donation Sound - sound to play with a new top donation. Enter the file name. MUST be in WAV format")
        self.top_donation_sound_text_box = wx.TextCtrl(self.main_panel, 1, size=(400,-1))
        self.top_donation_sound_text_box.SetValue(self.config.get("Donation Tracker Config", 'topdonationwav'))
        
        
        self.donation_formatting_label = wx.StaticText(self.main_panel, label="Donation Formatting - format how the donations will look. For advanced users only")
        
        self.donation_formatting_text_box_label = wx.StaticText(self.main_panel, label="Donation Formatting")
        self.donation_formatting_text_box = wx.TextCtrl(self.main_panel, 1, size=(500,-1))
        self.donation_formatting_text_box.SetValue(self.config.get("Donation Tracker Config", 'donationformatting'))
        
        self.top_donation_formatting_text_box_label = wx.StaticText(self.main_panel, label="Top Donation Formatting")
        self.top_donation_formatting_text_box = wx.TextCtrl(self.main_panel, 1, size=(500,-1))
        self.top_donation_formatting_text_box.SetValue(self.config.get("Donation Tracker Config", 'topdonationformatting'))
        
        self.donation_list_formatting_text_box_label = wx.StaticText(self.main_panel, label="Donation List Formatting")
        self.donation_list_formatting_text_box = wx.TextCtrl(self.main_panel, 1, size=(500,-1))
        self.donation_list_formatting_text_box.SetValue(self.config.get("Donation Tracker Config", 'donationlistformatting'))
        
        self.console_formatting_text_box_label = wx.StaticText(self.main_panel, label="Console Formatting")
        self.console_formatting_text_box = wx.TextCtrl(self.main_panel, 1, size=(500,-1))
        self.console_formatting_text_box.SetValue(self.config.get("Donation Tracker Config", 'consoleformatting'))
        
        self.formatting_help_label = wx.StaticText(self.main_panel, label="""
                {amount} = Amount with currency sign
                {note} = Note/memo field
                {username} = Twitch Username of contributer
                {processor} = Payment Processor
                {currencySymbol} = Currency Symbol
            """)
        
        # layout
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.panel_sizer.Add(self.channel_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.channel_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.api_key_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.api_key_text_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.clear_files_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.clear_donation_list_checkbox, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.clear_recent_donation_checkbox, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.clear_top_donation_checkbox, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.sound_min_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.sound_min_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.file_min_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.file_min_text_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.donation_list_amount_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.donation_list_amount_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.play_sound_checkbox, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.donation_sound_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.donation_sound_text_box, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.top_donation_sound_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.top_donation_sound_text_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        
        self.panel_sizer.Add(self.donation_formatting_label, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.donation_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.donation_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.top_donation_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.top_donation_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.donation_list_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.donation_list_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.console_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        self.panel_sizer.Add(self.console_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.panel_sizer.Add(self.formatting_help_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        self.main_panel.SetSizer(self.panel_sizer)
        
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_sizer.Add(self.main_panel, border=60, flag= wx.ALIGN_LEFT | wx.TOP | wx.LEFT | wx.RIGHT)
        
        self.scroll_window.SetSizer(self.scroll_sizer)
        
        self.window_sizer = wx.BoxSizer(wx.VERTICAL)
        self.window_sizer.Add(self.scroll_window, 1, wx.ALL|wx.EXPAND, 0)
        
        
        self.main_panel.SetAutoLayout(True)
        self.main_panel.Layout()
        self.main_panel.Fit()
        
        self.SetSizer(self.window_sizer)
        self.Center()
        
        # scroll settings
        self.main_panel_width, self.main_panel_height = self.main_panel.GetSize()
        self.unit = 20
        self.scroll_window.SetScrollbars( self.unit, self.unit, self.main_panel_width/self.unit, self.main_panel_height/self.unit )
        
    def nativeClose(self, event):
        self.write_config()
        self.Destroy()
        self.parent_window.Show()

    def write_config(self):
        self.config.set('Donation Tracker Config', 'channel', self.channel_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'api-key', self.api_key_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'dailydonationlist', self.clear_donation_list_checkbox.GetValue())
        self.config.set('Donation Tracker Config', 'dailyrecentdonation', self.clear_recent_donation_checkbox.GetValue())
        self.config.set('Donation Tracker Config', 'dailytopdonation', self.clear_top_donation_checkbox.GetValue())
        self.config.set('Donation Tracker Config', 'soundminimum', self.sound_min_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'fileminimum', self.file_min_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'donationlistamount', self.donation_list_amount_box.GetValue())
        self.config.set('Donation Tracker Config', 'playwav', self.play_sound_checkbox.GetValue())
        self.config.set('Donation Tracker Config', 'donationwav', self.donation_sound_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'topdonationwav', self.top_donation_sound_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'donationformatting', self.donation_formatting_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'topdonationformatting', self.top_donation_formatting_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'donationlistformatting', self.donation_list_formatting_text_box.GetValue())
        self.config.set('Donation Tracker Config', 'consoleformatting', self.console_formatting_text_box.GetValue())
        
        with open(resourcePath('settings.ini', user=True), 'w') as fp:
            self.config.write(fp)

class RunWindow(wx.Frame):
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        wx.Frame.__init__(self, None, title='Donation Tracker', size=(600, 400))
        
        # events
        self.Bind(wx.EVT_CLOSE, self.nativeClose)
        
        # icon
        icon = wx.Icon(resourcePath('icon.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        # interface
        #output_panel = wx.Panel(self, -1) # style=wx.SUNKEN_BORDER
        #output_panel.SetBackgroundColour((0, 0, 0))
        log = wx.TextCtrl(self, -1, size=(400,300), style = wx.TE_RICH | wx.TE_MULTILINE | wx.TE_READONLY)
        log.SetBackgroundColour((0, 0, 0))
        log.SetForegroundColour((200, 200, 200))
        
        # layout
        window_layout = wx.BoxSizer(wx.VERTICAL)
        
        window_layout.Add(log, 1, wx.ALL|wx.EXPAND, 0)
        
        self.SetSizer(window_layout)
        
        self.Center()
        
        self.SetFocus()
        
        # redirect text
        redir=RedirectText(log)
        sys.stdout=redir
        
        try:
            res_dir = sys._MEIPASS
        except Exception:
            res_dir = os.path.abspath(".")
        
        # start donation tracking in a new thread
        donations_thread = Thread(target=donations.start_tracking, args=(res_dir,))
        donations_thread.start()
        
    def nativeClose(self, event):
        self.Destroy()
        #self.parent_window.Show()
        
        os._exit(1)

def resourcePath(relative_path = '', user = False):
    base_dir = ''
    
    if getattr(sys, 'frozen', False):
        # running in a PyInstaller bundle
        if (user == False):
            # bundle dir
            base_dir = sys._MEIPASS
        else:
            # user access dir
            base_dir = os.path.dirname(sys.executable)
    else:
        # running in normal Python environment
        base_dir = os.path.dirname(__file__)
    
    return os.path.join(base_dir, relative_path)

def main():
    app = wx.App()
    main_frame = MainWindow()
    main_frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
