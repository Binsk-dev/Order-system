from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QTableWidget, QLabel, QVBoxLayout, QComboBox, QPushButton, QHeaderView, QTableWidgetItem, QAbstractItemView, QRadioButton
from db_utils import DataQuery, FileExporter
import sys

class SubWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.wanted = ["orderLineNo", "products.productCode", "products.name", "quantity", "priceEach"]
        self.current_table = ''
        self.current_order = ''
        self.resize(600, 300)
        self.setup_ui()

    def setup_ui(self):
        # Setting basic config
        self.setWindowTitle("Selected order list")
        self.setGeometry(0, 0, 500, 550)

        #------ Widgets --------
        # Labels
        self.order_detail_label = QLabel("주문 상세 내역")
        self.order_number_label = QLabel("주문번호:")
        self.order_number_result_label = QLabel("---")
        self.product_count_label = QLabel("상품개수:")
        self.product_count_result_label = QLabel("--")
        self.cost_label = QLabel("주문액:")
        self.cost_result_label = QLabel("---")
        self.file_export_label = QLabel("파일 출력")
        
        # Push buttons
        self.save_button = QPushButton("저장")

        # Table
        self.order_table = QTableWidget()

        # RadioButton
        self.csv_button = QRadioButton("CSV")
        self.json_button = QRadioButton("JSON")
        self.xml_button = QRadioButton("XML")

        # Top layout
        top_layout = QGridLayout()
        top_layout.addWidget(self.order_detail_label, 0, 0)
        top_layout.addWidget(self.order_number_label, 1, 0)
        top_layout.addWidget(self.order_number_result_label, 1, 1)
        top_layout.addWidget(self.product_count_label, 1, 2)
        top_layout.addWidget(self.product_count_result_label, 1, 3)
        top_layout.addWidget(self.cost_label, 1, 4)
        top_layout.addWidget(self.cost_result_label, 1, 5)

        # Middle layout
        mid_layout = QGridLayout()
        mid_layout.addWidget(self.order_table)

        # Bottom layout
        bottom_layout = QGridLayout()
        bottom_layout.addWidget(self.file_export_label, 0, 0)
        bottom_layout.addWidget(self.csv_button, 0, 1)
        bottom_layout.addWidget(self.json_button, 0, 2)
        bottom_layout.addWidget(self.xml_button, 0, 3)
        bottom_layout.addWidget(self.save_button, 0, 4)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(mid_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        # Widget setting
        self.save_button.clicked.connect(self.save_clicked)
        self.csv_button.setChecked(True)
        self.order_table.cellClicked.connect(lambda i: self.table_clicked(i))

    def setup_order_table(self, rows):
        header = ["orderLineNo", "productCode", "productName", "quantity", "priceEach", "상품주문액"]
        self.order_table.setColumnCount(len(header))
        self.order_table.setRowCount(len(self.current_table))
        self.order_table.setHorizontalHeaderLabels(header)
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # print(rows)
        self.current_table = rows
        for row, instance in enumerate(self.current_table):
            self.current_table[row] = {'orderLineNo': instance['orderLineNo'], 'productCode': instance['productCode'], \
                                    'name': instance['name'], 'quantity': instance['quantity'], 'priceEach': instance['priceEach'], \
                                    'total': instance['quantity'] * instance['priceEach']} 
            self.order_table.setItem(row, 0, QTableWidgetItem(str(instance['orderLineNo'])))
            self.order_table.setItem(row, 1, QTableWidgetItem(str(instance['productCode'])))
            self.order_table.setItem(row, 2, QTableWidgetItem(str(instance['name'])))
            self.order_table.setItem(row, 3, QTableWidgetItem(str(instance['quantity'])))
            self.order_table.setItem(row, 4, QTableWidgetItem(str(instance['priceEach'])))
            self.order_table.setItem(row, 5, QTableWidgetItem(str(instance['quantity'] * instance['priceEach'])))
            instance['total'] = instance['quantity'] * instance['priceEach']

        self.order_table.resizeColumnsToContents()
        self.order_table.resizeRowsToContents()

    def save_clicked(self):
        if self.csv_button.isChecked():
            self.csv_export(self.current_order, self.current_table)
        elif self.json_button.isChecked():
            self.json_export(self.current_order, self.current_table)
        elif self.xml_button.isChecked():
            self.xml_export(self.current_order, self.current_table)
        else:
            print("오류입니다.")

    def display_total_cost(self):
        result = 0
        for row in self.current_table:
            result += row['total']
        self.cost_result_label.setText(str(result))

    def table_clicked(self, row):
        target = self.current_table[row]
        self.product_count_result_label.setText(str(target['quantity']))

    def csv_export(self, order, rows):
        FileExporter().export_to_csv(order, rows)

    def json_export(self, order, rows):
        FileExporter().export_to_json(order, rows)

    def xml_export(self, order, rows):
        FileExporter().export_to_xml(order, rows)

class MainWindow(QWidget):
    """
    Simple client program for classic models DB
    """
    def __init__(self):
        super().__init__()
        self.wanted = ["orderNo", "orderDate", "city", "country", "status", "name", "comments"]
        self.setup_ui()
        self.focus_target = "customer"
        self.sub_window = SubWindow()

    def setup_ui(self):
        # Setting basic config
        self.setWindowTitle("Classic model DB Client")
        self.setGeometry(0, 0, 800, 550)

        #------ Widgets --------
        # Labels
        search_label = QLabel("주문 검색")
        customer_label = QLabel("고객:")
        country_label = QLabel("국가:")
        city_label = QLabel("도시:")
        order_count_label = QLabel("주문된 검색의 갯수:")
        self.order_count_result_label = QLabel("0")
        
        # Combo boxes
        self.customer_combobox = QComboBox()
        self.country_combobox = QComboBox()
        self.city_combobox = QComboBox()
        
        # Push buttons
        self.search_button = QPushButton("검색")
        self.clear_button = QPushButton("초기화")

        # Table
        self.order_table = QTableWidget()

        # Top layout
        top_layout = QGridLayout()
        top_layout.addWidget(search_label)

        # Middle layout
        mid_layout = QGridLayout()
        mid_layout.addWidget(customer_label, 0, 0)
        mid_layout.addWidget(self.customer_combobox, 0, 1)
        mid_layout.addWidget(country_label, 0, 2)
        mid_layout.addWidget(self.country_combobox, 0, 3)
        mid_layout.addWidget(city_label, 0, 4)
        mid_layout.addWidget(self.city_combobox, 0, 5)
        mid_layout.addWidget(self.search_button, 0, 6)
        mid_layout.addWidget(order_count_label, 1, 0)
        mid_layout.addWidget(self.order_count_result_label, 1, 1)
        mid_layout.addWidget(self.clear_button, 1, 6)

        # Bottom layout
        bottom_layout = QGridLayout()
        bottom_layout.addWidget(self.order_table)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(mid_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        # Widget setting
        self.setup_widgets()

    def setup_widgets(self):
        rows = DataQuery().get_all_order(self.wanted)
        
        all_name = {'ALL'}
        all_country = {'ALL'}
        all_city = {'ALL'}

        for row in rows:
            all_name.add(row['name'])
            all_country.add(row['country'])
            all_city.add(row['city'])

        self.customer_combobox.addItems(sorted(list(all_name)))
        self.country_combobox.addItems(sorted(list(all_country)))
        self.city_combobox.addItems(sorted(list(all_city)))

        # Label setting
        self.order_count_result_label.setText(str(len(rows)))

        # Table setting
        self.setup_order_table(rows)
        self.order_table.cellDoubleClicked.connect(lambda i: self.item_double_clicked(i))

        # Push button setting
        self.search_button.clicked.connect(self.search_clicked)
        self.clear_button.clicked.connect(self.clear_clicked)

        # combo box setting
        self.customer_combobox.activated.connect(lambda: self.combobox_activated("customer"))
        self.country_combobox.activated.connect(lambda: self.combobox_activated("country"))
        self.city_combobox.activated.connect(lambda: self.combobox_activated("city"))

    def clear_clicked(self):
        self.order_table.setRowCount(0)
        self.order_count_result_label.setText("0")
        self.customer_combobox.setCurrentIndex(0)
        self.country_combobox.setCurrentIndex(0)
        self.city_combobox.setCurrentIndex(0)

    def search_clicked(self):
        wanted = ["orderNo", "orderDate", "city", "country", "status", "name", "comments"]
        result = ''
        
        # Category condition
        if self.focus_target == "customer":
            result = DataQuery().get_order_by_name(wanted, self.customer_combobox.currentText())
        elif self.focus_target == "country":
            result = DataQuery().get_order_by_country(wanted, self.country_combobox.currentText())
        elif self.focus_target == "city":
            result = DataQuery().get_order_by_city(wanted, self.city_combobox.currentText())
        
        self.setup_order_table(result)
        self.order_count_result_label.setText(str(len(result)))

    def combobox_activated(self, text):
        self.focus_target = text

    def setup_order_table(self, rows):
        table_columns = ["orderNo", "orderDate", "requiredDate", "shippedDate", "status", "customer", "comments"]
        self.order_table.setColumnCount(len(table_columns))
        self.order_table.setRowCount(len(rows))
        self.order_table.setHorizontalHeaderLabels(table_columns)
        # self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row, instance in enumerate(rows):
            for col, target in enumerate(self.wanted):
                item = QTableWidgetItem(str(instance[target]))
                self.order_table.setItem(row, col, item)
        
        self.order_table.resizeColumnsToContents()
        self.order_table.resizeRowsToContents()

    def item_double_clicked(self, row):
        # Get specific order
        item = self.order_table.item(row, 0)
        result = DataQuery().get_order_detail(self.sub_window.wanted, item.text())
        
        # Change order number
        self.sub_window.current_order = item.text()
        self.sub_window.current_table = result
        self.sub_window.setup_order_table(result)
        self.sub_window.order_number_result_label.setText(item.text())

        # Change total cost
        self.sub_window.display_total_cost()
        self.sub_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()