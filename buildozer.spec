[app]
title =  Konkor Timer App
package.name = timerapp
package.domain = org.timerapp

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/icon.jpg

android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
