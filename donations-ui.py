import donations
import wx
import sys, os
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
        icon = wx.Icon(resourcePath('icon.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        # interface
        scroll_window = wx.ScrolledWindow(self, -1)
        
        main_panel = wx.Panel(scroll_window, -1)
        
        channel_text_box_label = wx.StaticText(main_panel, label="Channel - your channel name on Twitch")
        channel_text_box = wx.TextCtrl(main_panel, 1, size=(200,-1))
        
        api_key_text_box_label = wx.StaticText(main_panel, label="API Key - your API key from StreamDonations.net")
        api_key_text_box = wx.TextCtrl(main_panel, 1, size=(300,-1))
        
        
        clear_files_label = wx.StaticText(main_panel, label="Clear the donation lists")
        clear_donation_list_checkbox = wx.CheckBox(main_panel, 1, "Daily Donations List - clear the donations list on start")
        clear_recent_donation_checkbox = wx.CheckBox(main_panel, 1, "Most Recent Donation - clear the most recent donation list on start")
        clear_top_donation_checkbox = wx.CheckBox(main_panel, 1, "Daily Top Donation - clear the top donation list on start")
        
        
        sound_min_text_box_label = wx.StaticText(main_panel, label="Alarm Minimum - minimum donation amount before triggering alarm")
        sound_min_text_box = wx.TextCtrl(main_panel, 1, size=(100,-1))
        
        file_min_text_box_label = wx.StaticText(main_panel, label="File Minimum - minimum donation amount before adding to the list")
        file_min_text_box = wx.TextCtrl(main_panel, 1, size=(100,-1))
        
        
        donation_list_amount_box_label = wx.StaticText(main_panel, label="Donation List Amount - number of donations to include in the list")
        donation_list_amount_box = wx.TextCtrl(main_panel, 1, size=(100,-1))
        
        
        play_sound_checkbox = wx.CheckBox(main_panel, 1, "Play Sound - Play a sounds for new donations")
        
        donation_sound_text_box_label = wx.StaticText(main_panel, label="New Donation Sound - sound to play with a new donation. Enter the file name. MUST be in WAV format")
        donation_sound_text_box = wx.TextCtrl(main_panel, 1, size=(400,-1))
        
        top_donation_sound_text_box_label = wx.StaticText(main_panel, label="New Top Donation Sound - sound to play with a new top donation. Enter the file name. MUST be in WAV format")
        top_donation_sound_text_box = wx.TextCtrl(main_panel, 1, size=(400,-1))
        
        
        donation_formatting_label = wx.StaticText(main_panel, label="Donation Formatting - format how the donations will look. For advanced users only")
        
        donation_formatting_text_box_label = wx.StaticText(main_panel, label="Donation Formatting")
        donation_formatting_text_box = wx.TextCtrl(main_panel, 1, size=(500,-1))
        
        top_donation_formatting_text_box_label = wx.StaticText(main_panel, label="Top Donation Formatting")
        top_donation_formatting_text_box = wx.TextCtrl(main_panel, 1, size=(500,-1))
        
        donation_list_formatting_text_box_label = wx.StaticText(main_panel, label="Donation List Formatting")
        donation_list_formatting_text_box = wx.TextCtrl(main_panel, 1, size=(500,-1))
        
        console_formatting_text_box_label = wx.StaticText(main_panel, label="Console Formatting")
        console_formatting_text_box = wx.TextCtrl(main_panel, 1, size=(500,-1))
        
        formatting_help_label = wx.StaticText(main_panel, label="""
                {amount} = Amount with currency sign
                {note} = Note/memo field
                {username} = Twitch Username of contributer
                {processor} = Payment Processor
                {currencySymbol} = Currency Symbol
            """)
        
        # layout
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        
        panel_sizer.Add(channel_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(channel_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(api_key_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(api_key_text_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(clear_files_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(clear_donation_list_checkbox, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(clear_recent_donation_checkbox, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(clear_top_donation_checkbox, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(sound_min_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(sound_min_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(file_min_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(file_min_text_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(donation_list_amount_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(donation_list_amount_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(play_sound_checkbox, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(donation_sound_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(donation_sound_text_box, border=10, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(top_donation_sound_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(top_donation_sound_text_box, border=50, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        
        panel_sizer.Add(donation_formatting_label, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(donation_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(donation_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(top_donation_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(top_donation_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(donation_list_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(donation_list_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(console_formatting_text_box_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        panel_sizer.Add(console_formatting_text_box, border=20, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        panel_sizer.Add(formatting_help_label, border=5, flag= wx.ALIGN_LEFT | wx.BOTTOM)
        
        main_panel.SetSizer(panel_sizer)
        
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(main_panel, border=60, flag= wx.ALIGN_LEFT | wx.ALL)
        
        scroll_window.SetSizer(scroll_sizer)
        
        window_sizer = wx.BoxSizer(wx.VERTICAL)
        window_sizer.Add(scroll_window, 1, wx.ALL|wx.EXPAND, 0)
        
        
        main_panel.SetAutoLayout(True)
        main_panel.Layout()
        main_panel.Fit()
        
        self.SetSizer(window_sizer)
        self.Center()
        
        # scroll settings
        main_panel_width, main_panel_height = main_panel.GetSize()
        unit = 20
        scroll_window.SetScrollbars( unit, unit, main_panel_width/unit, main_panel_height/unit )
        
    def nativeClose(self, event):
        self.write_ini()
        self.Destroy()
        self.parent_window.Show()

    def write_ini(self):
        print('write the ini')
        
        #test_file = open(os.path.join(os.getcwd(), 'out_test.txt'), 'w+')
        #test_file.write(os.getcwd())
        #test_file.close()

class RunWindow(wx.Frame):
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        wx.Frame.__init__(self, None, title='Donation Tracker', size=(600, 400))
        self.SetBackgroundColour((255, 255, 255))
        
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
            internal_resource_path = sys._MEIPASS
        except Exception:
            internal_resource_path = os.path.abspath(".")
        
        # start donation tracking in a new thread
        donations_thread = Thread(target=donations.start_tracking, args=(internal_resource_path,))
        donations_thread.start()
        
    def nativeClose(self, event):
        self.Destroy()
        #self.parent_window.Show()
        
        os._exit(1)

def resourcePath(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # @UndefinedVariable
    except Exception:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

def main():
    app = wx.App()
    main_frame = MainWindow()
    main_frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
