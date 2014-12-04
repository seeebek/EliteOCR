from os import environ
from os.path import isdir, dirname, realpath
from PyQt4.QtCore import QSettings, QString
from PyQt4.QtGui import QMessageBox, QFileDialog

#@TODO: Refactor this into a class, with better defaults handling, so avoid the current monkeypatching in setSetting

def loadSettings(widget = None):
    """ Loads settings  from registry """
    settings = QSettings('seeebek', 'eliteOCR')
    if not settings.contains('export_dir'):
        setSetting(settings, 'export_dir')
    if not settings.contains('create_nn_images'):
        setSetting(settings, 'create_nn_images')
    if not settings.contains('log_dir'):
        setSetting(settings, 'log_dir')

    if settings.contains('screenshot_dir'):
        settings_dict = {'screenshot_dir': settings.value('screenshot_dir', type=QString),
                         'export_dir': settings.value('export_dir', type=QString),
                         'log_dir': settings.value('log_dir', type=QString),
                         'auto_fill': settings.value('auto_fill', type=bool),
                         'remove_dupli': settings.value('remove_dupli', type=bool),
                         'cal_points': settings.value('cal_points', type=float),
                         'img_res': settings.value('img_res', type=int),
                         'create_nn_images': settings.value('create_nn_images', type=bool)}
        return settings_dict
    else:
        return setDefaultSettings(widget)
        
def setSetting(settings, to_set):
    if to_set == 'export_dir':
        dir = dirname(realpath(__file__))
        settings.setValue(to_set, dir)
    if to_set == 'create_nn_images':
        settings.setValue(to_set, True)
    if to_set == 'log_dir':
        if isdir(environ['USERPROFILE']+'\\AppData\\Local\\Frontier_Developments\\Products\\FORC-FDEV-D-1002\\Logs'):
            dir = environ['USERPROFILE']+'\\AppData\\Local\\Frontier_Developments\\Products\\FORC-FDEV-D-1002\\Logs'
            settings.setValue(to_set, dir)
        else:
            QMessageBox.warning(None, "Warning", "The Game was not installed in the default "+\
                "location. Log directory could not be found. Please choose the directory in which "+\
                "you installed the game. Otherwise system names will not be added to the results.")
            dir = QFileDialog.getExistingDirectory(None, "Choose", "./")
            if dir != "":
                if isdir(dir+"\\Products\\FORC-FDEV-D-1002\\Logs"):
                    settings.setValue(to_set, dir+"\\Products\\FORC-FDEV-D-1002\\Logs")
                else:
                    QMessageBox.warning(None, "Warning", "Log directory not found.\n"+\
                        "You can add this directory later in settings menu. Until then your "+\
                        "results will not contain system names.")
                    settings.setValue(to_set, "./")
            else:
                settings.setValue(to_set, "./")
        
def setDefaultSettings(widget):
    """ Sets settings to default values """
    settings = QSettings('seeebek', 'eliteOCR')
    settings.setValue('auto_fill', False)
    settings.setValue('create_nn_images', True)
    settings.setValue('remove_dupli', True)
    #screenshot directory
    if isdir(environ['USERPROFILE']+'\\Pictures\\Frontier Developments\\Elite Dangerous'):
        dir = environ['USERPROFILE']+'\\Pictures\\Frontier Developments\\Elite Dangerous'
        settings.setValue('screenshot_dir', dir)
    else:
        dir = './'
        settings.setValue('screenshot_dir', dir)
        
    #export directory
    expdir = dirname(realpath(__file__))
    settings.setValue('export_dir', expdir)
    
    #log directory
    if isdir(environ['USERPROFILE']+'\\AppData\\Local\\Frontier_Developments\\Products\\FORC-FDEV-D-1002\\Logs'):
        logdir = environ['USERPROFILE']+'\\AppData\\Local\\Frontier_Developments\\Products\\FORC-FDEV-D-1002\\Logs'
        settings.setValue('log_dir', logdir)
    else:
        QMessageBox.warning(None, "Warning", "The Game was not installed in the default "+\
            "location. Log directory could not be found. Please choose the directory in which "+\
            "you installed the game. Otherwise system names will not be added to the results.")
        logdir = QFileDialog.getExistingDirectory(None, "Choose", "./")
        if logdir != "":
            if isdir(dir+"\\Products\\FORC-FDEV-D-1002\\Logs"):
                settings.setValue('log_dir', logdir+"\\Products\\FORC-FDEV-D-1002\\Logs")
            else:
                QMessageBox.warning(None, "Warning", "Log directory not found.\n"+\
                    "You can add this directory later in settings menu. Until then your "+\
                    "results will not contain system names.")
                settings.setValue('log_dir', "./")
        else:
            settings.setValue('log_dir', "./")
        
    #save settings
    settings.sync()
    QMessageBox.information(widget, "Calibration neccessary", "The OCR areas need to be set."+\
        " Callibration dialog will open now. Please choose a screenshot file."+\
        " You can recalibrate at any time by clicking on Calibrate in Settings menu.")
    widget.openCalibrate(dir)
    settings.sync()
    return loadSettings()
    