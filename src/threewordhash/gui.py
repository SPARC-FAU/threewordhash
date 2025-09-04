# src/threewordhash/gui.py
import sys


from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSpinBox,
)
from PySide6.QtGui import QFont

from threewordhash.core import (
    create_salt_digest,
    friendly_id,
    load_wordlist,
    parse_args,
)

# from threewordhash import encode, decode, Wordlist


class TWHApp(QMainWindow):

    # create signal for updating the salt text
    _custom_salt = QtCore.Signal(str)
    _new_id = QtCore.Signal(str)

    def __init__(
        self,
        wordlist: list[str],
        salt: str = "",
        salt_size: int = 32,
        word_count: int = 3,
        checksum_len: int = 2,
        sep: str = "-",
        lock_salt: bool = False,
    ):
        super().__init__()

        self._salt = salt
        self._salt_size = salt_size

        self._word_count = word_count
        self._checksum_len = checksum_len
        self._sep = sep

        self._wordlist = wordlist

        self._current_input = ""

        self._init_ui(lock_salt)

    def _set_salt(self, salt: str):
        self._salt = salt
        self._custom_salt.emit(salt)
        self.encode()

    def _set_salt_size(self, size: int):
        self._salt_size = size
        self.encode()

    def _create_salt(self):
        new_salt = create_salt_digest(self._salt_size)
        self._set_salt(new_salt)

    def _update_word_count(self, count: int):
        self._word_count = count
        self.encode()

    def _update_checksum_len(self, length: int):
        self._checksum_len = length
        self.encode()

    def _update_sep(self, sep: str):
        self._sep = sep
        self.encode()

    def _update_input(self, text: str):
        self._current_input = text

        self.encode()

    def _init_ui(
        self,
        lock_salt: bool,
    ):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # SALT SECTION
        salt_layout = QHBoxLayout()

        salt_label = QLabel("Secret Salt:")
        salt_field = QLineEdit()
        salt_field.setText(self._salt)
        salt_field.editingFinished.connect(lambda: self._set_salt(salt_field.text()))
        salt_field.setEnabled(not lock_salt)
        if lock_salt:
            salt_field.setEchoMode(QLineEdit.Password)

        self._custom_salt.connect(salt_field.setText)
        salt_generator = QPushButton("Generate")
        salt_generator.clicked.connect(self._create_salt)
        salt_generator.setEnabled(not lock_salt)

        salt_size = QSpinBox()
        salt_size.setMinimum(32)
        salt_size.setMaximum(4096)
        salt_size.setValue(self._salt_size)
        salt_size.setSuffix(" bytes")
        salt_size.valueChanged.connect(self._set_salt_size)
        salt_size.setEnabled(not lock_salt)

        salt_layout.addWidget(salt_label)
        salt_layout.addWidget(salt_field)
        salt_layout.addWidget(salt_generator)
        salt_layout.addWidget(salt_size)

        # OPTIONS SECTION
        word_count = QSpinBox()
        word_count.setMinimum(2)
        word_count.setMaximum(10)
        word_count.setValue(self._word_count)
        word_count.setSuffix(" words")
        word_count.valueChanged.connect(self._update_word_count)

        checksum_len = QSpinBox()
        checksum_len.setMinimum(0)
        checksum_len.setMaximum(5)
        checksum_len.setValue(self._checksum_len)
        checksum_len.setSuffix(" checksum chars")
        checksum_len.valueChanged.connect(self._update_checksum_len)

        sep_label = QLabel("Separator:")
        sep_field = QLineEdit()
        # sep_field.setInputMask("X;-")
        sep_field.setMaxLength(1)
        sep_field.setText(self._sep)
        sep_field.setMaximumWidth(20)
        sep_field.textChanged.connect(self._update_sep)

        options_layout = QHBoxLayout()
        options_layout.addWidget(word_count)
        options_layout.addWidget(checksum_len)
        options_layout.addWidget(sep_label)
        options_layout.addWidget(sep_field)

        # INPUT SECTION
        input_layout = QHBoxLayout()
        input_label = QLabel("Input:")
        input_field = QLineEdit()
        input_field.setPlaceholderText("e.g., name or email")
        input_field.editingFinished.connect(
            lambda: self._update_input(input_field.text())
        )
        input_field.setFont(QFont("Serif", 20))

        input_layout.addWidget(input_label)
        input_layout.addWidget(input_field)

        result = QLabel("")
        result.setFont(QFont("Courier", 36))
        result.setTextInteractionFlags(
            result.textInteractionFlags()
            | Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )

        result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._new_id.connect(result.setText)

        layout.addLayout(salt_layout)
        layout.addLayout(options_layout)
        layout.addLayout(input_layout)
        layout.addWidget(result)

        central_widget.setLayout(layout)

    def encode(self):
        result = friendly_id(
            user_input=self._current_input,
            secret_salt=self._salt,
            wordlist=self._wordlist,
            n_words=self._word_count,
            checksum_len=self._checksum_len,
            sep=self._sep,
        )

        self._new_id.emit(result)
        self.adjustSize()


def main():
    args = parse_args()

    # Create a minimal UI using pyside6
    app = QApplication(sys.argv)

    if args.wordlist is None:
        args.wordlist = "wordlist/eff_large_wordlist.txt"

    window = TWHApp(
        wordlist=load_wordlist(args.wordlist),
        salt=args.salt if args.salt else "",
        salt_size=args.salt_size,
        word_count=args.nwords,
        checksum_len=args.checksum,
        sep="-",
        lock_salt=args.salt is not None,
    )
    window.setWindowTitle("Three Word Hash Generator")

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
