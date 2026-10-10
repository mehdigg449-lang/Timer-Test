from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

Window.clearcolor = (0.96, 0.93, 0.85, 1)

SUBJECTS = {
    'Experimental': {
        'Biology': 60,
        'Math': 120,
        'Physics': 80,
        'Chemistry': 60,
        'Geology': 120,
    },
    'Math-Physics': {
        'Mathematics': 105,
        'Physics': 77,
        'Chemistry': 60,
    },
    'Humanities': {
        'Math & Statistics': 90,
        'Literature': 60,
        'Arabic': 60,
        'History & Geography': 50,
        'Philosophy & Logic': 60,
        'Economics': 60,
        'Psychology': 80,
    },
    'Art': {
        'General Art': 60,
        'Math-Physics Art': 80,
        'Visual Creativity': 75,
    },
}


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        img = FloatLayout()

        bg = Image(source='bg.png', allow_stretch=True, keep_ratio=False)
        bg.disabled = True
        img.add_widget(bg)

        layout = BoxLayout(
            orientation='vertical',
            padding=250,
            spacing=8,
            size_hint=(1, 1),
            pos_hint={'x': 0.05, 'y': -0.27}
        )

        worker = Button(text='Start', font_size=30, color=(0, 0, 0, 1), size_hint=(0.7, 0.5))
        worker.background_normal = ''
        worker.background_color = (0.15, 0.65, 0.75, 1)

        exi = Button(text='Exit', font_size=30, color=(0, 0, 0, 1), size_hint=(0.7, 0.5))
        exi.background_normal = ''
        exi.background_color = (0.9, 0.4, 0.6, 1)

        layout.add_widget(worker)
        layout.add_widget(exi)

        exi.bind(on_press=self.exit_app)
        worker.bind(on_press=self.go_to_timer)

        img.add_widget(layout)
        self.add_widget(img)

    def exit_app(self, instance):
        App.get_running_app().stop()

    def go_to_timer(self, instance):
        self.manager.current = 'timer'


class TimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.time_standard = 0
        self.time_max = 0
        self.time_left = 0
        self.timer_event = None
        self.running = False

        root = FloatLayout()

        bg = Image(source='', allow_stretch=True, keep_ratio=False)
        bg.color = (0.85, 0.92, 0.90, 1)
        bg.disabled = True
        root.add_widget(bg)

        back_btn = Button(
            text='← Back',
            font_size=dp(16),
            size_hint=(0.25, 0.06),
            pos_hint={'x': 0.03, 'top': 0.97},
            background_normal='',
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1),
        )
        back_btn.bind(on_release=self.go_back)
        root.add_widget(back_btn)

        self.field_spinner = Spinner(
            text='Select Field',
            values=list(SUBJECTS.keys()),
            size_hint=(0.4, 0.08),
            pos_hint={'x': 0.05, 'top': 0.88},
            font_size=dp(16),
            background_normal='',
            background_color=(0.2, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
        )
        self.field_spinner.bind(text=self.on_field_change)

        self.subject_spinner = Spinner(
            text='Select Subject',
            values=[],
            size_hint=(0.4, 0.08),
            pos_hint={'x': 0.55, 'top': 0.88},
            font_size=dp(16),
            background_normal='',
            background_color=(0.2, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
        )
        self.subject_spinner.bind(text=self.on_subject_change)

        root.add_widget(self.field_spinner)
        root.add_widget(self.subject_spinner)

        self.timer_label = Label(
            text='00:00',
            font_size=dp(70),
            color=(0.15, 0.25, 0.30, 1),
            size_hint=(1, 0.2),
            pos_hint={'center_x': 0.5, 'top': 0.72},
        )
        root.add_widget(self.timer_label)

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint=(0.8, 0.03),
            pos_hint={'center_x': 0.5, 'top': 0.5},
        )
        root.add_widget(self.progress)

        self.start_btn = Button(
            text='Start',
            font_size=dp(22),
            size_hint=(0.5, 0.12),
            pos_hint={'center_x': 0.5, 'y': 0.28},
            background_normal='',
            background_color=(0.2, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
        )
        self.start_btn.bind(on_release=self.toggle_timer)
        root.add_widget(self.start_btn)

        self.result_label = Label(
            text='',
            font_size=dp(26),
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.13},
        )
        root.add_widget(self.result_label)

        self.add_widget(root)

    def go_back(self, instance):
        self.reset_timer()
        self.manager.current = 'main'

    def on_field_change(self, spinner, text):
        if text in SUBJECTS:
            self.subject_spinner.values = list(SUBJECTS[text].keys())
            self.subject_spinner.text = 'Select Subject'
            self.reset_timer()

    def on_subject_change(self, spinner, text):
        field = self.field_spinner.text
        if field in SUBJECTS and text in SUBJECTS[field]:
            self.time_standard = SUBJECTS[field][text]
            self.time_max = self.time_standard * 2
            self.time_left = self.time_max
            self.update_timer_label()
            self.progress.value = 0
            self.result_label.text = ''

    def toggle_timer(self, instance):
        if not self.running:
            if self.time_standard == 0:
                self.result_label.text = 'Select a subject first!'
                self.result_label.color = (0.8, 0.1, 0.1, 1)
                return
            self.start_timer()
        else:
            self.stop_timer()

    def start_timer(self):
        if self.time_left <= 0:
            self.time_left = self.time_max
            self.update_timer_label()
            self.progress.value = 0
        self.running = True
        self.start_btn.text = 'Solved'
        self.start_btn.background_color = (0.9, 0.3, 0.3, 1)
        self.result_label.text = ''
        self.timer_event = Clock.schedule_interval(self.tick, 1)

    def stop_timer(self):
        self.running = False
        self.start_btn.text = 'Start'
        self.start_btn.background_color = (0.2, 0.7, 0.4, 1)
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self.evaluate()
        self.time_left = self.time_max
        self.update_timer_label()
        self.progress.value = 0

    def tick(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer_label()
            elapsed = self.time_max - self.time_left
            self.progress.value = (elapsed / self.time_max) * 100
        else:
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None
            self.running = False
            self.start_btn.text = 'Start'
            self.start_btn.background_color = (0.2, 0.7, 0.4, 1)
            self.result_label.text = 'Time is up! Terrible ❌'
            self.result_label.color = (0.8, 0.1, 0.1, 1)
            self.time_left = self.time_max
            self.update_timer_label()
            self.progress.value = 0

    def update_timer_label(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.text = f'{minutes:02d}:{seconds:02d}'

    def evaluate(self):
        elapsed = self.time_max - self.time_left
        ratio = elapsed / self.time_standard if self.time_standard > 0 else 0

        if ratio < 0.75:
            self.result_label.text = 'Good ✅'
            self.result_label.color = (0.1, 0.6, 0.2, 1)
        elif ratio <= 1.0:
            self.result_label.text = 'Average ⚠️'
            self.result_label.color = (0.9, 0.6, 0.1, 1)
        else:
            self.result_label.text = 'Terrible ❌'
            self.result_label.color = (0.8, 0.1, 0.1, 1)

    def reset_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self.running = False
        self.time_standard = 0
        self.time_max = 0
        self.time_left = 0
        self.timer_label.text = '00:00'
        self.progress.value = 0
        self.result_label.text = ''
        self.start_btn.text = 'Start'
        self.start_btn.background_color = (0.2, 0.7, 0.4, 1)


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(TimerScreen(name='timer'))
        return sm


MyApp().run()