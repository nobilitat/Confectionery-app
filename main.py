import sys
from PySide6 import QtCore, QtWidgets, QtGui
from ConnectToDatabase import ConnectToDatabase
from ConnectDialogWindow import ConnectDialogWindow
from AddSupplierWindow import AddSupplierWindow
from AddRawWindow import AddRawWindow


class MainWindow(QtWidgets.QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QtGui.QIcon('icon-cake.png'))

        self.dialog = None
        self.connect = None

        self.resize(900, 600)
        self.setWindowTitle('Кондитерское производство')

        self.font = QtGui.QFont('times', 10)

        # Describe menu actions
        new_supply = QtGui.QAction('Новая поставка', self)
        show_supplies = QtGui.QAction('Просмотр поставок', self)
        new_raw = QtGui.QAction('Новое сырье', self)
        new_raw.triggered.connect(self.add_new_raw)
        show_raws = QtGui.QAction('Просмотр сырья', self)
        new_supplier = QtGui.QAction('Новый поставщик', self)
        new_supplier.triggered.connect(self.add_new_supplier)
        show_supplier = QtGui.QAction('Просмотр поставщиков', self)
        new_production = QtGui.QAction('Новый выпуск', self)
        show_productions = QtGui.QAction('Просмотр выпусков', self)
        new_product = QtGui.QAction('Новый продукт', self)
        show_product = QtGui.QAction('Просмотр продуктов', self)
        new_order = QtGui.QAction('Новый заказ', self)
        show_order = QtGui.QAction('Просмотр заказов', self)

        # create menuBar and add actions to menu
        menu = self.menuBar()
        menu.setFont(self.font)
        menu_supply = menu.addMenu('Поставка сырья')
        menu_supply.setFont(self.font)
        menu_supply.addAction(new_supply)
        menu_supply.addAction(show_supplies)
        menu_supply.addAction(new_raw)
        menu_supply.addAction(show_raws)
        menu_supply.addAction(new_supplier)
        menu_supply.addAction(show_supplier)
        menu_production = menu.addMenu('Производство')
        menu_production.setFont(self.font)
        menu_production.addAction(new_production)
        menu_production.addAction(show_productions)
        menu_production.addAction(new_product)
        menu_production.addAction(show_product)
        menu_order = menu.addMenu('Заказы')
        menu_order.setFont(self.font)
        menu_order.addAction(new_order)
        menu_order.addAction(show_order)

        self.title = QtWidgets.QLabel()

        # widget for table
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)

        # model for table
        self.model = QtGui.QStandardItemModel()

        # Table show
        self.main_layout = QtWidgets.QVBoxLayout(self.widget)

        self.main_table = QtWidgets.QTableView()
        self.main_table.setModel(self.model)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.main_table)

    def closeEvent(self, event):
        """Переопределение метода события вызываемого при закрытии окна"""
        if event.spontaneous():
            msg_box = QtWidgets.QMessageBox()
            msg_box.setFont(QtGui.QFont('times', 10))
            msg_box.setWindowTitle('Выход из программы')
            msg_box.setText('Вы уверены, что хотите выйти из программы?')
            msg_box.addButton('Да', QtWidgets.QMessageBox.ButtonRole.YesRole)
            msg_box.addButton('Нет', QtWidgets.QMessageBox.ButtonRole.NoRole)
            result = msg_box.exec()

            self.dialog.close() if not result else event.ignore()

    def connect_dialog(self):
        """Вызов диалогового окна"""
        self.dialog = ConnectDialogWindow()
        self.dialog.show()
        self.dialog.exec()

        return self.dialog.login_input.text(), self.dialog.password_input.text()

    @QtCore.Slot()
    def add_new_raw(self):
        """Вызов окна добавления сырья"""

        self.add_raw = AddRawWindow(self.connect)
        units = get_units(self.connect)
        for i in units:
            self.add_raw.unit.addItems(i)

        self.add_raw.show()

    @QtCore.Slot()
    def add_new_supplier(self):
        """Вызов окна добавления поставщика"""

        self.add_supplier = AddSupplierWindow(self.connect)
        self.add_supplier.show()


def get_units(connect):
    """Получение единиц измерения"""

    cursor = connect.cursor()
    cursor.execute("""
        select unit_name from unit
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def confectionary():
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.show()
    login, password = widget.connect_dialog()

    connect_object = ConnectToDatabase(login, password)
    connect = connect_object.connect_db()

    widget.connect = connect

    if connect:
        print("Подключение установлено")

        font = QtGui.QFont('times', 18)
        widget.title.setText('Текущие поставки')
        widget.title.setFont(font)

        cur = connect.cursor()
        cur.execute(
            '''select 
                sp.supply_number, 
                sp.supply_date, 
                r.raw_name,
                s.supplier_name,
                sp.supply_sum
            from supply sp
            inner join supplier s on sp.supplier_id = s.supplier_id
            inner join supply_raw sr on sr.supply_id = sp.supply_id 
            inner join raw r on r.raw_id = sr.raw_id;'''
            )
        result = cur.fetchall()
        cur.close()

        widget.model.setHorizontalHeaderItem(0, QtGui.QStandardItem('Номер'))
        widget.model.setHorizontalHeaderItem(1, QtGui.QStandardItem('Дата'))
        widget.model.setHorizontalHeaderItem(2, QtGui.QStandardItem('Наименование сырья'))
        widget.model.setHorizontalHeaderItem(3, QtGui.QStandardItem('Поставщик'))
        widget.model.setHorizontalHeaderItem(4, QtGui.QStandardItem('Сумма поставки'))
        widget.main_table.verticalHeader().hide()

        row_index = 0

        for i in result[::-1]:
            widget.model.insertRow(
                row_index,
                [
                    QtGui.QStandardItem(str(i[0])),
                    QtGui.QStandardItem(i[1].strftime("%m/%d/%Y")),
                    QtGui.QStandardItem(str(i[2])),
                    QtGui.QStandardItem(str(i[3])),
                    QtGui.QStandardItem(str(i[4]))
                 ])

        widget.main_table.setColumnWidth(1, 120)
        widget.main_table.setColumnWidth(2, 200)
        widget.main_table.setColumnWidth(3, 200)
        widget.main_table.setColumnWidth(4, 180)

    sys.exit(app.exec())


if __name__ == '__main__':
    confectionary()
