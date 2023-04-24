from decimal import Decimal
import pymysql as mysql
import csv
import json
import xml.etree.ElementTree as ET

class DatabaseUtils:
    def query_execute(self, user, passwd, db, sql, params):
        conn = mysql.connect(host='localhost', user=user, password=passwd, db=db, charset='utf8')

        try:
            with conn.cursor(mysql.cursors.DictCursor) as cursor:     # dictionary based cursor
                cursor.execute(sql, params)
                instances = cursor.fetchall()
                return instances
        except Exception as e:
            print(e)
            print(type(e))
        finally:
            conn.close()

class DataQuery:
    # 모든 검색문은 여기에 각각 하나의 메소드로 정의
    def get_all_order(self, wanted: list):
        sql = f"SELECT {', '.join(wanted)} FROM orders INNER JOIN customers ON orders.customerId = customers.customerId ORDER BY orderNo"
        params = ()

        util = DatabaseUtils()
        rows = util.query_execute(db="classicmodels", user="guest", passwd="bemyguest", sql=sql, params=params)
        return rows

    def get_order_by_name(self, wanted, target="ALL"):
        sql = ''

        if target == "ALL":
            return self.get_all_order(wanted)
        else:
            sql = f"SELECT {', '.join(wanted)} FROM orders INNER JOIN customers ON orders.customerId = customers.customerId WHERE name=%s ORDER BY orderNo"
            util = DatabaseUtils()
            rows = util.query_execute(db="classicmodels", user="guest", passwd="bemyguest", sql=sql, params=target)
            return rows

    def get_order_by_country(self,wanted, target="ALL"):
        sql = ''

        if target == "ALL":
            return self.get_all_order(wanted)
        else:
            sql = f"SELECT {', '.join(wanted)} FROM orders INNER JOIN customers ON orders.customerId = customers.customerId WHERE country=%s ORDER BY orderNo"
            util = DatabaseUtils()
            rows = util.query_execute(db="classicmodels", user="guest", passwd="bemyguest", sql=sql, params=target)
            return rows

    def get_order_by_city(self, wanted, target="ALL"):
        sql = ''

        if target == "ALL":
            return self.get_all_order(wanted)
        else:
            sql = f"SELECT {', '.join(wanted)} FROM orders INNER JOIN customers ON orders.customerId = customers.customerId WHERE city=%s ORDER BY orderNo"
            util = DatabaseUtils()
            rows = util.query_execute(db="classicmodels", user="guest", passwd="bemyguest", sql=sql, params=target)
            return rows

    def get_order_detail(self, wanted, target):    
        sql = f"SELECT {', '.join(wanted)} FROM orderDetails INNER JOIN products ON orderDetails.productCode = products.productCode WHERE orderNo=%s ORDER BY orderLineNo"
        util = DatabaseUtils()
        rows = util.query_execute(db="classicmodels", user="guest", passwd="bemyguest", sql=sql, params=target)
        return rows

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)

class FileExporter():
    def export_to_csv(self, name, rows: list):
        file_name = name + ".csv"

        with open(file_name, "w") as f:
            w = csv.DictWriter(f, rows[0].keys())
            w.writeheader()
            w.writerows(rows)

    def export_to_json(self, name, rows):
        file_name = name + ".json"

        with open(file_name, "w") as f:
            data = json.dumps(rows, indent=4, cls=DecimalEncoder)
            f.write(data)

    def export_to_xml(self, name, rows):
        file_name = name + ".xml"

        table_name = name
        table_rows = rows
        
        root_element = ET.Element("Table")
        root_element.attrib['name'] = table_name

        for row in table_rows:
            row_element = ET.Element('Row')
            root_element.append(row_element)

            for column_name in list(row.keys()):
                if row[column_name] == None:  # NICKNAME, JOIN_YYYY, NATION 처리
                    row_element.attrib[column_name] = ''
                elif type(row[column_name]) == int:  # BACK_NO, HEIGHT, WEIGHT 처리
                    row_element.attrib[column_name] = str(row[column_name])
                elif type(row[column_name]) == Decimal:
                    row_element.attrib[column_name] = str(row[column_name])
                else:
                    row_element.attrib[column_name] = row[column_name]

        # XDM 트리를 화일에 출력
        ET.ElementTree(root_element).write(file_name, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    wanted = ["orderNo", "orderDate", "requiredDate", "shippedDate", "status", "name", "comments"]
    query = DataQuery()
    print(query.get_all_order(wanted))