import psycopg2
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QAbstractScrollArea, QVBoxLayout, QHBoxLayout, QTableWidget, QGroupBox, QTableWidgetItem, QPushButton, QMessageBox, QInputDialog


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db()

        self.setWindowTitle("Schedule for БВТ2201")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_shedule_tab()
        self._create_teacher_tab()
        self._create_timetable_upper_tab()
        self._create_timetable_lower_tab()

        self.rowSelected = None
        self.idSelected = None


    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="timetable",
                                     user="postgres",
                                     password="tchad235",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    def _create_teacher_tab(self):
        self.teacher_tab = QWidget()
        self.tabs.addTab(self.teacher_tab, "Teacher")

        self.teacher_gbox = QGroupBox("Teacher")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.teacher_gbox)

        self._create_teacher_table()


        self.update_teacher_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_teacher_button)
        self.update_teacher_button.clicked.connect(self._update_teacher)

        self.shboxa = QHBoxLayout()
        self.shbox1.addLayout(self.shboxa)
        self.alter_teacher_button = QPushButton("Change")
        self.shboxa.addWidget(self.alter_teacher_button)
        self.alter_teacher_button.clicked.connect(lambda ch: self.update_teacher_info('Change'))

        self.shboxd = QHBoxLayout()
        self.shbox1.addLayout(self.shboxd)
        self.delete_teacher_button = QPushButton("Delete")
        self.shboxd.addWidget(self.delete_teacher_button)
        self.delete_teacher_button.clicked.connect(lambda ch: self.update_teacher_info('Delete'))

        self.shboxrow = QHBoxLayout()
        self.shbox1.addLayout(self.shboxrow)
        self.add_teacher_button = QPushButton("Add row")
        self.shboxrow.addWidget(self.add_teacher_button)
        self.add_teacher_button.clicked.connect(lambda ch: self.update_teacher_info('Add row'))

        self.teacher_tab.setLayout(self.svbox)

    def _create_teacher_table(self):
        self.teacher_table = QTableWidget()
        self.teacher_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.teacher_table.setColumnCount(3)
        self.teacher_table.setHorizontalHeaderLabels(["Full Name", "Subject", ""])

        self._update_teacher_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.teacher_table)
        self.teacher_gbox.setLayout(self.mvbox)

    def _update_teacher_table(self):
        self.cursor.execute("SELECT * FROM teacher")
        records = list(self.cursor.fetchall())

        self.teacher_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            updateTeach = QPushButton("Choose")

            self.teacher_table.setItem(i, 0, QTableWidgetItem(str(r[1])))
            self.teacher_table.setItem(i, 1, QTableWidgetItem(str(r[2])))

            self.teacher_table.setItem(len(records), 0, QTableWidgetItem(str('')))
            self.teacher_table.setItem(len(records), 1, QTableWidgetItem(str('')))

            self.teacher_table.setCellWidget(i, 2, updateTeach)
            updateTeach.clicked.connect(lambda ch, num=i, id=r[0]: self.select_row(num, id))

        selectTeach = QPushButton("Choose")
        self.teacher_table.setCellWidget(len(records), 2, selectTeach)
        selectTeach.clicked.connect(lambda ch, num=len(records): self.select_row(num))

        self.teacher_table.resizeRowsToContents()

    def update_teacher_info(self, query):
        if query == 'Change':
            self.cursor.execute("select count(full_name) from teacher")
            records = self.cursor.fetchall()
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                        "WHERE table_schema = 'public' AND table_name = 'teacher' ")
                    columns = self.cursor.fetchall()
                    new_values = []
                    for temp in columns[1:]:
                        text, ok = QInputDialog.getText(self, 'Change teacher',
                                                        'Enter a value {}:'.format(temp[0]))
                        if ok and text != "":
                            new_values.append(text)
                    if len(new_values) == 2:
                        try:
                            self.cursor.execute("update teacher "
                                                "set full_name = %s, subject = %s "
                                                "where id = {};".format(self.idSelected), tuple(new_values))
                            self.conn.commit()
                        except:
                            self.conn.commit()
                            QMessageBox.about(self, "Error", "This item does not exist in the given table")

            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Choose a non-empty row")

        elif query == 'Delete':
            self.cursor.execute("select count(full_name) from teacher")
            records = self.cursor.fetchall()
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    print(self.rowSelected)
                    self.cursor.execute("delete from teacher where id={}".format(self.idSelected))
                    self.conn.commit()
            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Choose a non-empty row.")

        elif query == 'Add row':
            self.cursor.execute("select count(full_name) from teacher")
            records = self.cursor.fetchall()
            if records[0][0] == self.rowSelected:
                print('Can do')
                self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                    "WHERE table_schema = 'public' AND table_name = 'teacher' ")
                columns = self.cursor.fetchall()
                new_values = []
                for temp in columns[1:]:
                    text, ok = QInputDialog.getText(self, 'Add new teacher',
                                                    'Enter a value {}:'.format(temp[0]))
                    if ok and text != "":
                        new_values.append(text)
                if len(new_values) == 2:
                    try:
                        self.cursor.execute("insert into "
                                            "teacher(full_name, subject) "
                                            "values(%s, %s);", tuple(new_values))
                        self.conn.commit()
                    except:
                        self.conn.commit()
                        QMessageBox.about(self, "Error", "The given item does not exist in the table.")

                print(new_values)

            else:
                QMessageBox.about(self, "Error", "Choose a non-empty row.")

    def _update_teacher(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_teacher_table()

    def _create_timetable_upper_tab(self):
        self.timetable_upper_tab = QWidget()
        self.tabs.addTab(self.timetable_upper_tab, "Upper week")

        self.timetable_upper_gbox = QGroupBox("Upper week")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.timetable_upper_gbox)

        self._create_timetable_upper_table()

        self.update_timetable_upper_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_timetable_upper_button)
        self.update_timetable_upper_button.clicked.connect(self._update_timetable_upper)

        self.timetable_upper_tab.setLayout(self.svbox)

    def _create_timetable_upper_table(self):
        self.timetable_upper_table = QTableWidget()
        self.timetable_upper_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.timetable_upper_table.setColumnCount(2)
        self.timetable_upper_table.setHorizontalHeaderLabels(["Day", "Lesson"])

        self._update_timetable_upper_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.timetable_upper_table)
        self.timetable_upper_gbox.setLayout(self.mvbox)

    def _update_timetable_upper_table(self):
        self.cursor.execute(
            "select day, string_agg(table_column, '\n\n') as table_row from (select day, timetable_upper.subject ||' |"
            " '|| room_numb ||' | '|| start_time ||' | '|| full_name as table_column from timetable_upper, teacher "
            "where teacher.subject = timetable_upper.subject order by start_time)timetable_upper group by 1 order by "
            "case when day = 'Upper Monday' then 1 when day = 'Upper Tuesday' then 2 when day = 'Upper Wednesday' then "
            "3 when day = 'Upper Thursday' then 4 else 5 end;")
        records = list(self.cursor.fetchall())

        self.timetable_upper_table.setRowCount(len(records))

        for i, r in enumerate(records):
            r = list(r)

            self.timetable_upper_table.setItem(i, 0,
                                               QTableWidgetItem(str(r[0])))
            self.timetable_upper_table.setItem(i, 1,
                                               QTableWidgetItem(str(r[1])))

        self.timetable_upper_table.resizeRowsToContents()

    def _update_timetable_upper(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_timetable_upper_table()

    def _create_timetable_lower_tab(self):
        self.timetable_lower_tab = QWidget()
        self.tabs.addTab(self.timetable_lower_tab, "Lower week")

        self.timetable_lower_gbox = QGroupBox("Lower week")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.timetable_lower_gbox)

        self._create_timetable_lower_table()

        self.update_timetable_lower_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_timetable_lower_button)
        self.update_timetable_lower_button.clicked.connect(self._update_timetable_lower)

        self.timetable_lower_tab.setLayout(self.svbox)

    def _create_timetable_lower_table(self):
        self.timetable_lower_table = QTableWidget()
        self.timetable_lower_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.timetable_lower_table.setColumnCount(2)
        self.timetable_lower_table.setHorizontalHeaderLabels(["Day", "Lesson"])

        self._update_timetable_lower_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.timetable_lower_table)
        self.timetable_lower_gbox.setLayout(self.mvbox)

    def _update_timetable_lower_table(self):
        self.cursor.execute(
            "select day, string_agg(table_column, '\n\n') as table_row from (select day, timetable_lower.subject ||' | "
            "'|| room_numb ||' | '|| start_time ||' | '|| full_name as table_column from timetable_lower, teacher where"
            " teacher.subject = timetable_lower.subject order by start_time)timetable_lower group by 1 order by case "
            "when day = 'Lower Monday' then 1 when day = 'Lower Tuesday' then 2 when day = 'Lower Wednesday' then 3 when "
            "day = 'Lower Thursday' then 4 else 5 end;")
        records = list(self.cursor.fetchall())

        self.timetable_lower_table.setRowCount(len(records))

        for i, r in enumerate(records):
            r = list(r)

            self.timetable_lower_table.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.timetable_lower_table.setItem(i, 1, QTableWidgetItem(str(r[1])))

        self.timetable_lower_table.resizeRowsToContents()

    def _update_timetable_lower(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_timetable_lower_table()

    def _create_shedule_tab(self):
        self.day = 'Upper Monday'
        self.schedule_tab = QWidget()
        self.tabs.addTab(self.schedule_tab, "Timetable")

        self.schedule_gbox = QGroupBox("{}".format(self.day))

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)

        self.shbox1.addWidget(self.schedule_gbox)

        self._create_schedule_table()

        self.svbox.addLayout(self.shbox2)
        self.update_schedule_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_schedule_button)
        self.update_schedule_button.clicked.connect(self._update_schedule)

        self.shboxm = QHBoxLayout()
        self.svbox.addLayout(self.shboxm)
        self.monday_schedule_button = QPushButton("Upper Monday")
        self.shboxm.addWidget(self.monday_schedule_button)
        self.monday_schedule_button.clicked.connect(lambda ch: self.btnstate('Upper Monday'))

        self.shboxt = QHBoxLayout()
        self.shboxm.addLayout(self.shboxt)
        self.tuesday_schedule_button = QPushButton("Upper Tuesday")
        self.shboxt.addWidget(self.tuesday_schedule_button)
        self.tuesday_schedule_button.clicked.connect(lambda ch: self.btnstate('Upper Tuesday'))

        self.shboxw = QHBoxLayout()
        self.shboxm.addLayout(self.shboxw)
        self.wednesday_schedule_button = QPushButton("Upper Wednesday")
        self.shboxw.addWidget(self.wednesday_schedule_button)
        self.wednesday_schedule_button.clicked.connect(lambda ch: self.btnstate('Upper Wednesday'))

        self.shboxth = QHBoxLayout()
        self.shboxm.addLayout(self.shboxth)
        self.thursday_schedule_button = QPushButton("Upper Thursday")
        self.shboxth.addWidget(self.thursday_schedule_button)
        self.thursday_schedule_button.clicked.connect(lambda ch: self.btnstate('Upper Thursday'))

        self.shboxf = QHBoxLayout()
        self.shboxm.addLayout(self.shboxf)
        self.friday_schedule_button = QPushButton("Upper Friday")
        self.shboxf.addWidget(self.friday_schedule_button)
        self.friday_schedule_button.clicked.connect(lambda ch: self.btnstate('Upper Friday'))

        self.shboxm2 = QHBoxLayout()
        self.svbox.addLayout(self.shboxm2)
        self.monday_schedule_button2 = QPushButton("Lower Monday")
        self.shboxm2.addWidget(self.monday_schedule_button2)
        self.monday_schedule_button2.clicked.connect(lambda ch: self.btnstate('Lower Monday'))

        self.shboxt2 = QHBoxLayout()
        self.shboxm2.addLayout(self.shboxt2)
        self.tuesday_schedule_button2 = QPushButton("Lower Tuesday")
        self.shboxt2.addWidget(self.tuesday_schedule_button2)
        self.tuesday_schedule_button2.clicked.connect(lambda ch: self.btnstate('Lower Tuesday'))

        self.shboxw2= QHBoxLayout()
        self.shboxm2.addLayout(self.shboxw2)
        self.wednesday_schedule_button2 = QPushButton("Lower Wednesday")
        self.shboxw2.addWidget(self.wednesday_schedule_button2)
        self.wednesday_schedule_button2.clicked.connect(lambda ch: self.btnstate('Lower Wednesday'))

        self.shboxth2 = QHBoxLayout()
        self.shboxm2.addLayout(self.shboxth2)
        self.thursday_schedule_button2 = QPushButton("Lower Thursday")
        self.shboxth2.addWidget(self.thursday_schedule_button2)
        self.thursday_schedule_button2.clicked.connect(lambda ch: self.btnstate('Lower Thursday'))

        self.shboxf2 = QHBoxLayout()
        self.shboxm2.addLayout(self.shboxf2)
        self.friday_schedule_button2 = QPushButton("Lower Friday")
        self.shboxf2.addWidget(self.friday_schedule_button2)
        self.friday_schedule_button2.clicked.connect(lambda ch: self.btnstate('Lower Friday'))

        self.shboxa = QHBoxLayout()
        self.shbox1.addLayout(self.shboxa)
        self.alter_lesson_button = QPushButton("Change")
        self.shboxa.addWidget(self.alter_lesson_button)
        self.alter_lesson_button.clicked.connect(lambda ch: self.update_lesson('Change'))

        self.shboxd = QHBoxLayout()
        self.shbox1.addLayout(self.shboxd)
        self.delete_lesson_button = QPushButton("Delete")
        self.shboxd.addWidget(self.delete_lesson_button)
        self.delete_lesson_button.clicked.connect(lambda ch: self.update_lesson('Delete'))

        self.shboxrow = QHBoxLayout()
        self.shbox1.addLayout(self.shboxrow)
        self.add_row_button = QPushButton("Add row")
        self.shboxrow.addWidget(self.add_row_button)
        self.add_row_button.clicked.connect(lambda ch: self.update_lesson('Add row'))

        self.schedule_tab.setLayout(self.svbox)

    def _create_schedule_table(self):
        self.schedule_table = QTableWidget()
        self.schedule_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["Subject", "Cabinet number", "Time", ""])

        self._update_schedule_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.schedule_table)
        self.schedule_gbox.setLayout(self.mvbox)

    def btnstate(self, wday):
        self.day = wday

    def _update_schedule_table(self):
        week = 'timetable_upper'
        if self.day == 'Upper Monday' or self.day == 'Upper Tuesday' or self.day == 'Upper Wednesday' or \
                self.day == 'Upper Thursday' or self.day == 'Upper Friday':
            week = 'timetable_upper'
        elif self.day == 'Lower Monday' or self.day == 'Lower Tuesday' or self.day == 'Lower Wednesday' or \
                self.day == 'Lower Thursday' or self.day == 'Lower Friday':
            week = 'timetable_lower'

        self.cursor.execute(
            "SELECT subject, room_numb, start_time, id FROM {} WHERE day = '{}'".format(week, self.day))
        records = list(self.cursor.fetchall())

        self.schedule_table.setRowCount(len(records) + 1)
        self.schedule_gbox.setTitle(self.day)
        for i, r in enumerate(records):
            r = list(r)
            selectRow = QPushButton("Choose")

            self.schedule_table.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.schedule_table.setItem(i, 1, QTableWidgetItem(str(r[1])))
            self.schedule_table.setItem(i, 2, QTableWidgetItem(str(r[2])))

            self.schedule_table.setItem(len(records), 0, QTableWidgetItem(str('')))
            self.schedule_table.setItem(len(records), 1, QTableWidgetItem(str('')))
            self.schedule_table.setItem(len(records), 2, QTableWidgetItem(str('')))

            self.schedule_table.setCellWidget(i, 3, selectRow)
            selectRow.clicked.connect(lambda ch, num=i, id=r[3]: self.select_row(num, id))

        selectRow = QPushButton("Choose")
        self.schedule_table.setCellWidget(len(records), 3, selectRow)
        selectRow.clicked.connect(lambda ch, num=len(records): self.select_row(num))

        self.schedule_table.resizeRowsToContents()

    def select_row(self, numRow, *numId):
        self.rowSelected = numRow
        if numId:
            self.idSelected = numId[0]
            print(self.idSelected)
        print(self.rowSelected)

    def update_lesson(self, query):
        week = 'timetable_upper'
        if self.day == 'Upper Monday' or self.day == 'Upper Tuesday' or self.day == 'Upper Wednesday' or \
                self.day == 'Upper Thursday' or self.day == 'Upper Friday':
            week = 'timetable_upper'
        elif self.day == 'Lower Monday' or self.day == 'Lower Tuesday' or self.day == 'Lower Wednesday' or \
                self.day == 'Lower Thursday' or self.day == 'Lower Friday':
            week = 'timetable_lower'
        if query == 'Change':
            print('Change')
            self.cursor.execute("select count(day) from {} where day = %s".format(week), (self.day,))
            records = self.cursor.fetchall()
            print(self.rowSelected)
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    new_values = []
                    self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                        "WHERE table_schema = 'public' AND table_name = '{}' ".format(week))
                    columns = self.cursor.fetchall()
                    for temp in columns[2:]:
                        text, ok = QInputDialog.getText(self, 'Change in timetable',
                                                        'Enter a value {}:'.format(temp[0]))
                        if ok and text != "":
                            new_values.append(text)
                    if len(new_values) == 3:
                        try:
                            print(new_values)
                            self.cursor.execute(
                                "update {} set subject = %s, room_numb= %s, start_time = %s where id= {}".format(
                                    week, self.idSelected), tuple(new_values))
                            self.conn.commit()
                        except:
                            self.conn.commit()
                            QMessageBox.about(self, "Error", "The given item does not exist in the table.")

            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Choose a non-empty row.")

        elif query == 'Delete':
            self.cursor.execute("select count(day) from {} where day = %s".format(week), (self.day,))
            records = self.cursor.fetchall()
            print(self.rowSelected)
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    self.cursor.execute("delete from {} where id={}".format(week, self.idSelected))
                    self.conn.commit()
            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Choose a non-empty row.")

        elif query == 'Add row':
            self.cursor.execute("select count(day) from {} where day = %s".format(week), (self.day,))
            records = self.cursor.fetchall()
            if records[0][0] == self.rowSelected:
                print('Can do')
                self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                    "WHERE table_schema = 'public' AND table_name = '{}' ".format(week))
                columns = self.cursor.fetchall()
                new_values = [self.day]
                for temp in columns[2:]:
                    text, ok = QInputDialog.getText(self, 'Add in timetable',
                                                    'Enter a value {}:'.format(temp[0]))
                    if ok and text != "":
                        new_values.append(text)
                if len(new_values) == 4:
                    try:
                        self.cursor.execute("insert into "
                                            "{}(day, subject, room_numb, start_time) "
                                            "values (%s, %s, %s, %s);".format(week), tuple(new_values))
                        self.conn.commit()
                    except:
                        self.conn.commit()
                        QMessageBox.about(self, "Error", "The given item does not exist in the table.")

                print(new_values)

            else:
                QMessageBox.about(self, "Error", "Choose a non-empty row.")

    def _update_schedule(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_schedule_table()



app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
