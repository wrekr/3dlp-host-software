
import slicer
from 3dlp_slicer_gui import Ui_MainWindow
from slicer_settings_dialog_gui import Ui_Dialog

slicer = slicer.slicer()

slicer.OpenModel("wfu_cbi_skull_cleaned.stl")
slicer.slice()