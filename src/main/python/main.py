from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys

from main_window import MainWindow

if __name__ == '__main__':
    appctxt = ApplicationContext()      
    stylesheet = appctxt.get_resource("styles.qss")
    appctxt.app.setStyleSheet(open(stylesheet).read())
    window = MainWindow(appctxt)
    window.show()
    exit_code = appctxt.app.exec_()    
    sys.exit(exit_code)
