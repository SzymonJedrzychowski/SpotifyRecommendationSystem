import sys
from PyQt5.QtWidgets import *
from modules.window import Window

# Run the main script of the window
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    if window.ifWorks:
        window.show()
        sys.exit(app.exec_())
