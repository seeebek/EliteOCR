from os import environ
from os.path import isdir, dirname, realpath
from PyQt4.QtCore import QSettings, QString
from PyQt4.QtGui import QMessageBox

def loadSettings(widget = None):
    """ Loads settings  from registry """
    settings = QSettings('seeebek', 'eliteOCR')
    if not settings.contains('export_dir'):
        setSetting(settings, 'export_dir')
    if settings.contains('screenshot_dir'):
        settings_dict = {'screenshot_dir': settings.value('screenshot_dir', type=QString),
                         'export_dir': settings.value('export_dir', type=QString),
                         'auto_fill': settings.value('auto_fill', type=bool),
                         'remove_dupli': settings.value('remove_dupli', type=bool),
                         'cal_points': settings.value('cal_points', type=float),
                         'img_res': settings.value('img_res', type=int)}
        return settings_dict
    else:
        return setDefaultSettings(widget)
        
def setSetting(settings, to_set):
    if to_set == 'export_dir':
        dir = dirname(realpath(__file__))
        settings.setValue(to_set, dir)
        
def setDefaultSettings(widget):
    """ Sets settings to default values """
    settings = QSettings('seeebek', 'eliteOCR')
    settings.setValue('auto_fill', False)
    settings.setValue('remove_dupli', True)
    if isdir(environ['USERPROFILE']+'\\Pictures\\Frontier Developments\\Elite Dangerous'):
        dir = environ['USERPROFILE']+'\\Pictures\\Frontier Developments\\Elite Dangerous'
        settings.setValue('screenshot_dir', dir)
    else:
        dir = './'
        settings.setValue('screenshot_dir', dir)
    expdir = dirname(realpath(__file__))
    settings.setValue('export_dir', expdir)
    settings.sync()
    QMessageBox.information(widget, "Calibration neccessary", "The OCR areas need to be set."+\
        " Callibration dialog will open now. Please choose a screenshot file."+\
        " You can recalibrate at any time by clicking on Calibrate in Settings menu.")
    widget.openCalibrate(dir)
    settings.sync()
    return loadSettings()
    