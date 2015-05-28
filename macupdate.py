import os
from os.path import dirname, join
import objc
import sys
from Foundation import NSObject


# https://github.com/sparkle-project/Sparkle/wiki/Customization

class Delegate(NSObject):

    def init(self):
        self = objc.super(Delegate, self).init()
        try:
            objc.loadBundle('Sparkle', globals(), join(dirname(sys.executable), os.pardir, 'Frameworks', 'Sparkle.framework'))
            self.updater = SUUpdater.sharedUpdater()
            self.updater.setDelegate_(self)
        except:
            # can't load framework - not frozen or not included in app bundle?
            self.updater = None
        self.infocallback = None
        return self

    def checkForUpdateInformation(self, callback):
        self.infocallback = callback
        if self.updater:
            self.updater.checkForUpdateInformation()

    def updater_didFindValidUpdate_(self, updater, item):
        self.infocallback(item.fileURL(), item.displayVersionString() or item.versionString())

    def checkForUpdates(self):
        if self.updater:
            self.updater.checkForUpdates_(None)

    # def updater_didFinishLoadingAppcast_(self, updater, appcast):
    #     print 'updater_didFinishLoadingAppcast_', appcast

    # def updaterDidNotFindUpdate_(self, updater):
    #     print 'updaterDidNotFindUpdate_', updater

Updater = Delegate.alloc().init()
