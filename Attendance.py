from PyQt5.QtWidgets import (
    QWidget, QApplication, QMenu, QFrame, QMainWindow, QAction,QMessageBox, QFontDialog,
    QVBoxLayout, QTextEdit, QColorDialog,QFileDialog, QGridLayout, QPushButton, QLabel,
    QLCDNumber, QButtonGroup,QDial, QLineEdit, QSplitter, QTabWidget, QDialog,
    QHBoxLayout, QStackedWidget,QFormLayout,QScrollArea,QGroupBox
)
from PyQt5.QtCore import (
    QFileInfo, Qt, QRect, QPoint, QPropertyAnimation, QRegExp, QThread, pyqtSignal
)
from PyQt5.QtGui import (
    QPixmap, QIcon, QFont, QRegExpValidator, QImage
)
from datetime import date
import mysql.connector
from PIL import Image
import numpy as np
import base64
import time
import sys
import cv2
import os

class ImageThread(QThread):
    cap = None
    changePixmap = pyqtSignal(QImage,bool)
    stop_flag=True
    def run(self):
        ImageThread.cap = cv2.VideoCapture(0)
        face=cv2.CascadeClassifier('face.xml')
        self.img_id=StudnetRegistration.s_ide.text()
        sample=0
        self.flag_stop=True
        while ImageThread.stop_flag:
            ret, img = ImageThread.cap.read()
            rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face.detectMultiScale(grey, 1.2, 5)
            for x, y, w, h in faces:
                sample += 1
                cv2.rectangle(rgbImage, (x, y), (x + w, y + h), (0, 255, 255), 2)
                cv2.imwrite('data/' + str(self.img_id) + '.' + str(sample) + '.jpg', grey[y:y + h, x:x + w])
                while sample>20:
                    ImageThread.stop_flag = False
                if sample==20:
                    self.flag_stop = False
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p,self.flag_stop)

class RecogThread(QThread):
    cap=None
    stop_att=True
    changeRecImg=pyqtSignal(QImage,int)
    def run(self):
        RecogThread.cap=cv2.VideoCapture(0)
        face=cv2.CascadeClassifier('face.xml')
        recog=cv2.face.LBPHFaceRecognizer_create()
        self.fontface = FONT_HERSHEY_TRIPLEX = 4
        self.fontscale = 2
        self.fontcolor = (255, 255, 255)
        try:
            con = mysql.connector.connect(
                username='root',
                host='127.0.0.1',
                database='attendance',
                passwd="Pramod@24"
            )
            cur = con.cursor()
        except:
            pass
        recog.read('tr.yml')
        t1 = time.time()
        id=0
        while RecogThread.stop_att:
            ret,img=RecogThread.cap.read()
            temp_img = img.copy()
            rgbimage=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            grey=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces=face.detectMultiScale(grey,1.2,5)
            for x,y,w,h in faces:
                cv2.rectangle(rgbimage, (x, y), (x + w, y + h), (0, 255, 255), 2)
                id,conf=recog.predict(grey[y:y+h,x:x+w])
                id1 = "Anonymous"
                cur.execute("select fname from faculty_table where id_no=(%s)", (Login.login_ide.text(),))
                a = cur.fetchall()
                pro_name = a[0][0]
                cur.execute("select sub from faculty_table where id_no=(%s)", (Login.login_ide.text(),))
                a = cur.fetchall()
                subje = a[0][0]
                cur.execute("select date,prof_name,sid from attendance_list")
                taken_list = cur.fetchall()
                if conf < 60:
                    cur.execute("select sname from student_table where sid=(%s)", (id,))
                    name = cur.fetchall()
                    id1 = name[0][0]
                    cur.execute("select hall_ticket from student_table where sid=(%s)", (id,))
                    name = cur.fetchall()
                    stid = name[0][0]
                if not (id1 == 'Anonymous'):
                    if time.time() - t1 > 5 and not ((str(LoggedPage.today_date), pro_name, stid) in taken_list):
                        file = None
                        cv2.imwrite('temp/tempary.jpg', temp_img)
                        with open('temp/tempary.jpg', 'rb') as f:
                            file = f.read()
                        os.remove('temp/tempary.jpg')
                        byte = base64.b64encode(file)
                        cur.execute(
                            "insert into attendance_list(date,prof_name,sub_name,sid,att_status,image) values(%s,%s,%s,%s,%s,%s)",
                            (
                                str(LoggedPage.today_date), pro_name, subje, stid, 1, byte))
                        print(stid,'is taken')
                        con.commit()
                cv2.putText(img, str(id1), (x, y + h), self.fontface, self.fontscale, self.fontcolor)
            h,w,ch=rgbimage.shape
            bytesperline=ch*w
            convertToQtFormat=QImage(rgbimage.data,w,h,bytesperline,QImage.Format_RGB888)
            p=convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changeRecImg.emit(p,id)
        con.disconnect()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pramod")
        self.setStyleSheet('''
            QPushButton#btns{
                background-color:#55E6C1;
                border:0px;
                padding:24px;
                font-size:20px;
                color:white
            }
            QPushButton#btns:hover{
                background-color:green;
                border:0px;
            }
            QPushButton#btns:pressed{
                background-color:red;
                border:0px;
            }
            QWidget#pramod{
                background-color: #2C3A47;
            }
            QWidget#mainwid{
                background-color: aqua;
            }
        ''')
        self.setFixedSize(1400, 900)
        # self.setGeometry(50,50,1400,900)
        # flags=Qt.WindowFlags(Qt.FramelessWindowHint|Qt.DragMoveCursor)
        # self.setWindowFlags(flags)
        # slide
        slide = QWidget()
        slide.setObjectName('pramod')
        vbox = QVBoxLayout()
        btn1 = QPushButton("Home", self)
        btn2 = QPushButton("Registration", self)
        btn3 = QPushButton("Login", self)
        btn4 = QPushButton("Report", self)
        # btn5 = QPushButton("Exit", self)
        # btn5.clicked.connect(self.quit_app)
        val = 0
        for i in (btn1, btn2, btn3, btn4):
            vbox.addWidget(i)
            i.clicked.connect(self.btn_clicked_change)
            i.page = val
            val += 1
            i.setObjectName("btns")
        # vbox.addWidget(btn5)
        # btn5.setObjectName('btns')
        slide.setLayout(vbox)
        slide.setMaximumWidth(400)
        slide.setMinimumWidth(400)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addStretch(0)
        # main menu
        self.mainwidget = QWidget()
        self.mainwidget.setObjectName('mainwid')
        test = QVBoxLayout()
        self.stack = QStackedWidget()
        self.stack.addWidget(Home())
        self.stack.addWidget(Registration())
        self.stack.addWidget(Login())
        self.stack.addWidget(Report())
        test.addWidget(self.stack)
        test.setContentsMargins(0, 0, 0, 0)
        self.mainwidget.setLayout(test)
        widget = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(slide)
        hbox.addWidget(self.mainwidget)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(hbox)
        self.setCentralWidget(widget)
    def quit_app(self):
        dia = QDialog(self)
        dia.setFixedSize(300, 200)
        dia.setStyleSheet('''
            QDialog{
                background-color:#55E6C1;
                border-radius:20px
            }
            QPushButton{
                background-color:#25CCF7;
            }
        ''')
        flags = Qt.WindowFlags(Qt.WindowCloseButtonHint)
        dia.setWindowFlags(flags)
        vbox = QVBoxLayout()
        label = QLabel("Are U Sure to exit")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont('calibri', 12))
        vbox.addWidget(label)
        wid = QWidget()
        hbox = QHBoxLayout()
        btn = QPushButton("Yes")
        btn.setFont(QFont('calibri', 12))
        btn2 = QPushButton("No")
        btn2.setFont(QFont('calibri', 12))
        btn.clicked.connect(lambda: sys.exit())
        btn2.clicked.connect(lambda: dia.close())
        hbox.addWidget(btn)
        hbox.addWidget(btn2)
        wid.setLayout(hbox)
        vbox.addWidget(wid)
        dia.setLayout(vbox)
        dia.exec()
    def btn_clicked_change(self):
        btn = self.sender()
        self.stack.setCurrentIndex(btn.page)
    # def mousePressEvent(self,event):
    #     self.oldpos=event.globalPos()
    # def mouseMoveEvent(self,event):
    #     delta=QPoint(event.globalPos()-self.oldpos)
    #     self.move(self.x()+delta.x(),self.y()+delta.y())
    #     self.oldpos=event.globalPos()

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('''
                QLabel#title{
                    font-size:24px;
                    padding:0px;
                    margin:0px
                }
        ''')
        vbox2 = QVBoxLayout()
        label = QLabel("<h1>Attendance</h1>")
        label.setObjectName('title')
        label.setAlignment(Qt.AlignCenter)

        vbox2.addWidget(label)
        vbox2.setContentsMargins(0, 0, 0, 0)
        vbox2.addStretch(0)
        self.setLayout(vbox2)

class Registration(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('''
        ''')
        main_vbox = QVBoxLayout()
        self.reg_stack = QStackedWidget()
        # main widget
        main_widget = QWidget()
        vbox = QVBoxLayout()
        label = QLabel("<h1>Registration Page</h1>")
        label.setObjectName("title")
        label.setAlignment(Qt.AlignCenter)
        f_btn = QPushButton("Faculty Registration")
        f_btn.clicked.connect(self.faculty_page)
        s_btn = QPushButton("Student Registration")
        s_btn.clicked.connect(self.student_page)
        vbox.addWidget(label)
        vbox.addWidget(f_btn)
        vbox.addWidget(s_btn)
        vbox.addStretch(0)
        vbox.addSpacing(0)
        vbox.setStretch(0, 0)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        f_btn.setFixedSize(200, 50)
        s_btn.setFixedSize(200, 50)
        vbox.setAlignment(Qt.AlignCenter)
        main_widget.setLayout(vbox)
        self.reg_stack.addWidget(Verification(self.reg_stack))
        self.reg_stack.addWidget(main_widget)
        self.reg_stack.addWidget(FacultyRegistration(self.reg_stack))
        self.reg_stack.addWidget(StudnetRegistration(self.reg_stack))
        main_vbox.addWidget(self.reg_stack)
        self.setLayout(main_vbox)
    def faculty_page(self):
        self.reg_stack.setCurrentIndex(2)
    def student_page(self):
        self.reg_stack.setCurrentIndex(3)
class Verification(QWidget):
    def __init__(self,reg_stack):
        super().__init__()
        self.reg_stack=reg_stack
        form_la=QFormLayout()

        pass_l=QLabel("Password")
        self.pass_ed=QLineEdit()
        self.pass_ed.setEchoMode(QLineEdit.Password)
        self.lgn_btn=QPushButton("Login")
        self.lgn_btn.clicked.connect(self.click_btn)

        form_la.addRow(pass_l,self.pass_ed)
        form_la.addWidget(self.lgn_btn)

        self.setLayout(form_la)

    def click_btn(self):
        if self.pass_ed.text()=="pramod":
            self.reg_stack.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", "Invalid Credentials!")


class FacultyRegistration(QWidget):
    def __init__(self, reg_stack):
        super().__init__()
        self.reg_stack = reg_stack
        form_f = QFormLayout()
        self.f_name = QLabel('Name:')
        self.f_namee = QLineEdit()
        self.f_id = QLabel("Id:")
        self.f_ide = QLineEdit()
        # reg=QRegExp('[0-9]*')
        # reg2=QRegExpValidator(reg,self.f_ide)
        # self.f_ide.setValidator(reg2)
        self.f_email = QLabel("Email:")
        self.f_emaile = QLineEdit()
        mail_reg=QRegExp('[a-z A-Z][a-z A-Z 0-9 . _]*@gmail.com')
        mail_reg2=QRegExpValidator(mail_reg,self.f_emaile)
        self.f_emaile.setValidator(mail_reg2)
        self.f_dept = QLabel("Department:")
        self.f_depte = QLineEdit()
        self.f_pass = QLabel("Password:")
        self.f_passe = QLineEdit()
        self.f_sub = QLabel("Subject:")
        self.f_sube = QLineEdit()
        self.reg_btn_f = QPushButton("Register")
        self.reg_btn_f.clicked.connect(self.f_registration)
        self.back = QPushButton("Back")
        self.back.clicked.connect(self.page_back)
        form_f.addRow(self.f_name, self.f_namee)
        form_f.addRow(self.f_id, self.f_ide)
        form_f.addRow(self.f_email, self.f_emaile)
        form_f.addRow(self.f_dept, self.f_depte)
        form_f.addRow(self.f_sub, self.f_sube)
        form_f.addRow(self.f_pass, self.f_passe)
        form_f.addWidget(self.reg_btn_f)
        form_f.addWidget(self.back)
        self.back.setStyleSheet('width:70px')
        self.setLayout(form_f)
    def page_back(self):
        for i in (self.f_namee, self.f_ide, self.f_emaile, self.f_depte, self.f_sube, self.f_passe):
            i.setText('')
        self.reg_stack.setCurrentIndex(1)
    def f_registration(self):
        if all((self.f_namee.text(), self.f_ide.text(), self.f_emaile.text(), self.f_depte.text(), self.f_sube.text(),
                self.f_passe.text())):
            try:
                con = mysql.connector.connect(
                    username='root',
                    host='127.0.0.1',
                    database='attendance',
                    passwd="Pramod@24"
                )
                cur = con.cursor()
                cur.execute("insert into faculty_table values(%s,%s,%s,%s,%s,%s)",
                            (self.f_namee.text(), self.f_ide.text(),
                             self.f_emaile.text(), self.f_depte.text(),
                             self.f_sube.text(), self.f_passe.text()))
                con.commit()
                con.disconnect()
                self.page_back()
            except Exception as e:
                print(e)
        else:
            msg = QMessageBox.warning(self, "Error", "Enter All Details")

class StudnetRegistration(QWidget):
    s_ide=None
    def __init__(self, reg_stack):
        super().__init__()
        self.img_trained=False
        self.reg_stack = reg_stack
        form_f = QFormLayout()
        self.s_name = QLabel("Name:")
        self.s_namee = QLineEdit()
        self.s_id = QLabel("Id:")
        StudnetRegistration.s_ide = QLineEdit()
        self.s_hall = QLabel("Hall Ticket:")
        self.s_halle = QLineEdit()
        self.s_email = QLabel("Email:")
        self.s_emaile = QLineEdit()
        self.s_dept = QLabel("Department:")
        self.s_depte = QLineEdit()
        self.train = QPushButton("Train Image")
        self.train.clicked.connect(self.cameraa)
        self.reg = QPushButton("Registration")
        self.reg.clicked.connect(self.register_student)
        self.back = QPushButton("Back")
        self.back.clicked.connect(self.page_back)
        self.img_label = QLabel()
        form_f.addRow(self.s_name, self.s_namee)
        form_f.addRow(self.s_hall, self.s_halle)
        form_f.addRow(self.s_email, self.s_emaile)
        form_f.addRow(self.s_dept, self.s_depte)
        form_f.addRow(self.s_id, StudnetRegistration.s_ide)
        form_f.addWidget(self.img_label)
        form_f.addWidget(self.train)
        form_f.addWidget(self.reg)
        form_f.addWidget(self.back)
        self.setLayout(form_f)
    def page_back(self):
        for i in (self.s_namee, StudnetRegistration.s_ide, self.s_emaile, self.s_depte, self.s_halle):
            i.setText('')
        self.reg_stack.setCurrentIndex(1)
        self.train.setEnabled(1)
    def cameraa(self):
        ImageThread.stop_flag = True
        self.img_label.setHidden(0)
        self.mythread = ImageThread(self)
        self.mythread.changePixmap.connect(self.setImage)
        self.mythread.start()
        self.train.setEnabled(0)
    def setImage(self, image,flag):
        if flag:
            self.img_label.setPixmap(QPixmap.fromImage(image))
        else:
            self.img_label.setHidden(1)
            ImageThread.cap.release()
            self.mythread.terminate()
            ImageThread.cap = None
            del self.mythread
            self.img_trained=True
            QMessageBox.about(self,"Registration","Your face is captured successfully")
    def register_student(self):
        if all((self.s_namee.text(), StudnetRegistration.s_ide.text(), self.s_emaile.text(), self.s_depte.text(), self.s_halle.text(),self.img_trained)):
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            path = 'data'
            def getImagesWithID(path):
                imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
                faces = []
                IDs = []
                for image in imagePaths:
                    faceimg = Image.open(image).convert('L')
                    faceNP = np.array(faceimg, 'uint8')
                    ID = int(os.path.split(image)[-1].split('.')[0])
                    faces.append(faceNP)
                    IDs.append(ID)
                return np.array(IDs), faces
            Ids, faces = getImagesWithID(path)
            recognizer.train(faces, Ids)
            recognizer.save('tr.yml')

            try:
                con = mysql.connector.connect(
                    username='root',
                    host='127.0.0.1',
                    database='attendance',
                    passwd="Pramod@24"
                )
                cur = con.cursor()
                cur.execute("insert into student_table values(%s,%s,%s,%s,%s)",
                            (self.s_ide.text(),self.s_namee.text(),
                             self.s_halle.text(), self.s_emaile.text(),
                             self.s_depte.text())
                            )
                con.commit()
                con.disconnect()

            except Exception as e:
                print(e)
            QMessageBox.about(self,"Success","Your face is trained and details are registered")
            self.img_trained=False
            self.page_back()
        else:
            QMessageBox.warning(self,'Error',"Please Enter All details")

class Login(QWidget):
    login_ide=None
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()
        self.stack_wid=QStackedWidget()
        login_wid=QWidget()
        form_layout=QFormLayout()
        self.login_id=QLabel("ID:")
        Login.login_ide=QLineEdit()
        self.pwd=QLabel("Password:")
        self.pwde=QLineEdit()
        self.pwde.setEchoMode(QLineEdit.Password)
        self.btn_login=QPushButton("Login")
        self.btn_login.clicked.connect(self.login_validation)
        form_layout.addRow(self.login_id,Login.login_ide)
        form_layout.addRow(self.pwd,self.pwde)
        form_layout.addWidget(self.btn_login)
        login_wid.setLayout(form_layout)
        self.stack_wid.addWidget(login_wid)
        self.stack_wid.addWidget(LoggedPage(self.stack_wid,self))
        vbox.addWidget(self.stack_wid)
        self.setLayout(vbox)
    def login_validation(self):
        if all((self.login_ide.text(),self.pwde.text())):
            try:
                con = mysql.connector.connect(
                    username='root',
                    passwd='Pramod@24',
                    database='attendance',
                    host='127.0.0.1'
                )
                cur=con.cursor()
                cur.execute("select passwd from faculty_table where id_no=(%s)",(self.login_ide.text(),))
                a=cur.fetchall()
                a=a[0][0]
                if self.pwde.text()==a:
                    self.stack_wid.setCurrentIndex(1)
                else:
                    QMessageBox.warning(self,"Error","Invalid Credentials!")
                con.disconnect()
            except Exception as e:
                print(e)
        else:
            QMessageBox.warning(self,"Error","Enter all details")

class LoggedPage(QWidget):
    today=None
    today_date=None
    def __init__(self,stack,master):
        super().__init__()
        self.list=[]
        self.parent=master
        self.stack_wid=stack
        vbox=QVBoxLayout()
        self.labe=QLabel("")
        self.labe.setHidden(1)
        self.take_att=QPushButton("Take Attendance")
        self.take_att.clicked.connect(self.take_attendane)
        self.stop_att=QPushButton("Stop Attendance")
        self.stop_att.clicked.connect(self.stop_attendance)
        self.rem_att=QPushButton("Absent Remaining")
        self.rem_att.clicked.connect(self.absent_remain)
        self.logout_btn=QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        vbox.addWidget(self.labe)
        vbox.addWidget(self.take_att)
        vbox.addWidget(self.stop_att)
        vbox.addWidget(self.rem_att)
        vbox.addWidget(self.logout_btn)
        self.setLayout(vbox)
    def setRecImage(self,image,id):
        if RecogThread.stop_att:
            self.labe.setPixmap(QPixmap.fromImage(image))
        else:
            self.labe.setHidden(1)
            RecogThread.cap.release()
            self.mythread.terminate()
            RecogThread.cap=None
            del self.mythread
            self.take_att.setEnabled(1)
    def take_attendane(self):
        LoggedPage.today=date.today()
        LoggedPage.today_date=LoggedPage.today.strftime('%Y-%m-%d')
        RecogThread.stop_att=True
        self.labe.setHidden(0)
        self.mythread=RecogThread(self)
        self.mythread.changeRecImg.connect(self.setRecImage)
        self.mythread.start()
        self.take_att.setEnabled(0)
    def absent_remain(self):
        con=mysql.connector.connect(
            username='root',
            host='127.0.0.1',
            passwd='Pramod@24',
            database='attendance'
        )
        cur=con.cursor()
        absent_list = []
        cur.execute('select hall_ticket from student_table')
        tot_str = cur.fetchall()
        tot_str = [i[0] for i in tot_str]
        cur.execute('select fname,sub from faculty_table where id_no=(%s)', (Login.login_ide.text(),))
        a = cur.fetchall()
        pro_name = a[0][0]
        subje = a[0][1]
        cur.execute('select sid from attendance_list where prof_name=(%s) and date=(%s) and att_status=(%s)',
                    (pro_name, str(LoggedPage.today_date), 1))

        pres_list = cur.fetchall()
        pres_list = [i[0] for i in pres_list]
        for i in tot_str:
            if not (i in pres_list):
                absent_list.append(i)
                cur.execute(
                    'insert into attendance_list(date,prof_name,sub_name,sid,att_status) values(%s,%s,%s,%s,%s)', (
                        str(LoggedPage.today_date), pro_name, subje, i, 0
                    ))

        con.commit()
        con.disconnect()
        QMessageBox.about(self,"Attendance","Total Present is:"+str(len(tot_str) - len(absent_list))+"\nTotal absent is:"+str(len(absent_list)))



    def stop_attendance(self):
        RecogThread.stop_att=False
    def logout(self):
        self.parent.login_ide.setText('')
        self.parent.pwde.setText('')
        self.stack_wid.setCurrentIndex(0)

class Report(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('''
                QLabel{
                    font-size:14px;
                    font-weight:700;
                }
        ''')
        con = mysql.connector.connect(username='root', host='127.0.0.1', database='pramod', passwd='Pramod@24')
        cur = con.cursor()

        cur.execute('select sub from faculty_table')
        subjects = cur.fetchall()
        cur.execute('select *from student order by hall_ticket')
        students=cur.fetchall()
        total = []
        for i in subjects:
            cur.execute("select sname,hall_ticket,sub_name,count(att_status) from student,attendance where \
            student.hall_ticket=attendance.sid and att_status='1' and attendance.sub_name='" + i[
                0] + "' group by hall_ticket order by student.hall_ticket")
            marks = cur.fetchall()
            total.append(marks)
        cur.execute('select count(date) from attendance group by sid')
        total_days=cur.fetchall()



        grid = QGridLayout()
        grid.addWidget(QLabel("HTNO"),0,0)
        grid.addWidget(QLabel("Name"),0,1)
        for i in range(len(subjects)):
            grid.addWidget(QLabel(subjects[i][0]),0,i+2)
        grid.addWidget(QLabel("Total"),0,5)
        grid.addWidget(QLabel("Percentage"),0,6)

        total2 = []
        for i in subjects:
            cur.execute("select hall_ticket,sname,sub_name,count(att_status) from student,attendance where \
                            student.hall_ticket=attendance.sid  and attendance.sub_name='" + i[
                0] + "' group by hall_ticket order by student.hall_ticket")

            total = cur.fetchall()

            cur.execute("select hall_ticket,sname,sub_name,count(att_status) from student,attendance where \
                            student.hall_ticket=attendance.sid and att_status='0' and attendance.sub_name='" + i[
                0] + "' group by hall_ticket order by student.hall_ticket")

            absent = cur.fetchall()
            total = [list(i) for i in total]
            absent = [list(i) for i in absent]
            for i in total:
                for j in absent:
                    if i[0] == j[0]:
                        i[3] = i[3] - j[3]
            total2.append(total)

        for i in range(len(students)):
            sum=0
            for j in range(len(subjects)):
                grid.addWidget(QLabel(str(total2[j][i][3])),i+1,j+2)
                sum+=total2[j][i][3]
            grid.addWidget(QLabel(str(total2[j][i][0])),i+1,0)
            grid.addWidget(QLabel(str(total2[j][i][1])), i + 1, 1)
            grid.addWidget(QLabel(str(sum)),i+1,len(subjects)+2)
            grid.addWidget(QLabel(str(format((sum/total_days[0][0])*100,'.2f'))),i+1,len(subjects)+3)

        wid=QWidget()
        wid.setStyleSheet('background-color:aqua')
        wid.setLayout(grid)
        sc=QScrollArea()
        sc.setWidgetResizable(1)
        sc.setWidget(wid)

        vbox=QVBoxLayout()
        vbox.addWidget(sc)
        grid.setAlignment(Qt.AlignTop)
        self.setLayout(vbox)

if __name__ == '__main__':
    con = mysql.connector.connect(
        username='root',
        host='127.0.0.1',
        database='attendance',
        passwd="Pramod@24"
    )
    cur = con.cursor()
    cur.execute(
        "create table if not exists faculty_table(fname text,id_no text not null,email text,dept text,sub text,passwd text,primary key(id_no(10)))"
    )
    cur.execute(
        'create table if not exists student_table(sid text,sname text,hall_ticket text not null,email text,dept text,primary key(hall_ticket(10),sid(10)))'
    )
    cur.execute(
        "create table if not exists attendance_list(date text,prof_name text,sub_name text,sid text,att_status bit,image longtext)"
    )
    con.disconnect()
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())