from t_main import LoginDialog,IndexWindow
from PyQt5.QtWidgets import *
import sys
app = QApplication(sys.argv)
passdlg = LoginDialog()
if (passdlg.exec_() == QDialog.Accepted):
    window = IndexWindow()
    window.showFullScreen()
    window.searchButtonClicked()
    sys.exit(app.exec_())