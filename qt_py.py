import sqlite3 as db
import sys
import os
import os.path
from glob import glob
from datetime import datetime as dt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
ifpath = "./Results.db"
if not os.path.exists(ifpath):

    # DB接続
    con = db.connect('Results.db', isolation_level=None)
    # 初回のみテーブル作成
    create_table = '''create table Results (filename varchar(40),filesize long,create_date varchar(20), status varchar(10))'''
    con.execute(create_table)
else:
    # DB接続のみ
    con = db.connect('Results.db', isolation_level=None)
# SQL文に値をセットする場合は，Pythonのformatメソッドなどは使わずに，
# セットしたい場所に?を記述し，executeメソッドの第2引数に?に当てはめる値を
# タプルで渡す．

# データインサート（テスト用）
tdatetime = dt.now()
tstr = tdatetime.strftime('%Y%m%d_%H%M%S')
sql = 'insert into Results (filename, filesize, create_date, status) values (?,?,?,?)'
aa = ('test.jpg',555555,tstr,'new')
con.execute(sql, aa)
cur = con.cursor()
cur.execute("SELECT * FROM Results")
all_data = cur.fetchall()

class TableWindow(QWidget):
    def __init__(self, parent=None):
        super(TableWindow, self).__init__(parent)
        self.initUI()
    def refreshUI(self):
        self.tablewidget.clear()
        cur.execute("SELECT * FROM Results")
        all_data = cur.fetchall()
        if len(all_data) > 0:
            colcnt = len(all_data[0])
            rowcnt = len(all_data)
            for n in range(rowcnt):
                for m in range(colcnt):
                    item = QTableWidgetItem(str(all_data[n][m]))
                    self.tablewidget.setItem(n, m, item)
    def initUI(self):
        colcnt = len(all_data[0])
        rowcnt = len(all_data)
        self.tablewidget = QTableWidget(rowcnt, colcnt)
        self.tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # ヘッダー設定
        horHeaders = ['filename', 'filesize', 'create_date', 'status']
        self.tablewidget.setHorizontalHeaderLabels(horHeaders)
        verHeaders = ['1', '2', '3','4']
        self.tablewidget.setVerticalHeaderLabels(verHeaders)
        self.tablewidget.setColumnWidth(0, 50)
        self.tablewidget.setColumnWidth(1, 120)
        self.tablewidget.setColumnWidth(2, 140)
        self.tablewidget.setColumnWidth(3, 100)

        # テーブルの中身作成
        for n in range(rowcnt):
            for m in range(colcnt):
                item = QTableWidgetItem(str(all_data[n][m]))
                self.tablewidget.setItem(n, m, item)
        # レイアウトにテーブルを追加
        layout = QVBoxLayout()
        layout.addWidget(self.tablewidget)
        # レイアウトにボタンを追加
        button1 = QPushButton("終了")
        button1.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(button1)
        # レイアウトにボタンを追加
        button2 = QPushButton("削除")
        button2.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(button2)
        # レイアウトにボタンを追加
        button3 = QPushButton("ロード")
        button3.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(button3)
        # レイアウトにボタンを追加
        button4 = QPushButton("手書き認識")
        button4.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(button4)
        # ボタンが押されたらアプリケーション終了
        button1.clicked.connect(self.button1Clicked)
        button2.clicked.connect(self.button2Clicked)
        button3.clicked.connect(self.button3Clicked)
        button4.clicked.connect(self.button4Clicked)
        self.setLayout(layout)
        self.setWindowTitle('画像管理')

    def button1Clicked(self):
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "本当に終了しますか？", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def button2Clicked(self):
        # 削除が押された場合

        # 1つでも選択されていれば削除
        if len(self.tablewidget.selectedItems()) > 0:
            bb = (self.tablewidget.takeItem(self.tablewidget.currentRow(), 0).text())

            # ファイル名が0でない場合
            if len(bb) > 0:
                # DBからも削除
                sql = 'delete from Results where filename = ?'
                con.execute(sql, (bb,))
                con.commit()

                # リストをリフレッシュする
                self.tablewidget.removeRow(self.tablewidget.currentRow())
                self.refreshUI()

    def button3Clicked(self):
        # ロードが押された場合

        # jpgファイルをリスト
        jpgfiles = glob("pics/*.jpg")
        for jpgfile in jpgfiles:
            file_name = os.path.basename(jpgfile)
            file_size = os.path.getsize(jpgfile)

            # Select-SQL組み立て
            sql = 'select * from Results where filename = ? and filesize = ?'
            dd = (file_name, file_size)

            # SQL実行
            cur = con.cursor()
            cur.execute(sql, dd)
            results = cur.fetchall()
            print(results)

            # ヒットしない場合、新規作成
            if len(results) == 0:
                print("chapterB")
                # SQL組み立て
                tstr = tdatetime.strftime('%Y%m%d_%H%M%S')
                sql = 'insert into Results (filename, filesize, create_date, status) values (?,?,?,?)'
                print("chapterBdash")
                ee = (file_name, file_size, tstr, 'NEW')
                # SQL実行
                print("chapterC:")
                con.execute(sql, ee)
                con.commit()
            # ヒットした場合、無視

        # リストをリフレッシュする
        self.tablewidget.removeRow(self.tablewidget.currentRow())
        self.refreshUI()

    def button4Clicked(self):
        # 手書き認識が押された場合

        # 1つも選択されていなければ実行しない
        selectedItems=self.tablewidget.selectedItems()
        if len(selectedItems) == 0:
            print("chapA")
            return

        # 選択した行の名前が空の場合も実行しない
        bb = (self.tablewidget.takeItem(self.tablewidget.currentRow(), 0).text())
        if len(bb) == 0:
            print("chapB")
            return

        for selectedItem in selectedItems:
            print("chapC")
            print(selectedItem.text())
            # url = "http://xxxx/xxxx"
            # method = "POST"
            # headers = {"Content-Type": "application/json"}

            # PythonオブジェクトをJSONに変換する
            # obj = {"xxx": "xxxx", 123: 123}
            # json_data = json.dumps(obj).encode("utf-8")

            # file = open('./pics/image.jpg', 'rt').read()
            # base64でencode
            # enc_file = base64.b64encode(file)

            # httpリクエストを準備してPOST
            # request = urllib.request.Request(url, data=json_data, method=method, headers=headers)
            # with urllib.request.urlopen(request) as response:
            #     response_body = response.read().decode("utf-8")

def main():
    app = QApplication(sys.argv)
    widget = TableWindow()
    widget.show()
    widget.raise_()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()