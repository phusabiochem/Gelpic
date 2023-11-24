#!/usr/bin/python3

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import os
import shutil
from picamera import PiCamera
from time import sleep, gmtime, strftime
from PIL import ImageTk, Image
import pyautogui
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import re
import dns.resolver
import socket
import tkinter.scrolledtext as st
from fractions import Fraction

if not os.path.exists('/home/pi/Gelpic100_Result'):
    f = os.path.join("/home/pi/", "Gelpic100_Result")
    os.mkdir(f)
if not os.path.exists('/home/pi/Gelpic100'):
    f = os.path.join("/home/pi/", "Gelpic100")
    os.mkdir(f)
if not os.path.exists('/home/pi/Gelpic100/.account.txt'):
    fw_account = open("/home/pi/Gelpic100/.account.txt", "x")
    fw_account.writelines('0\n')
    fw_account.close()
    fr_account = open("/home/pi/Gelpic100/.account.txt","r")
    account_active = int(fr_account.readline())
else:
    fr_account = open("/home/pi/Gelpic100/.account.txt","r")
    account_active = int(fr_account.readline())
    email_address = fr_account.readline().strip('\n')
    email_password = fr_account.readline().strip('\n')

BACKGROUND_COLOR = 'grey90'
MENU_BUTTON_ACTIVE_COLOR = "lawn green"
MENU_BUTTON_NONACTIVE_COLOR = "grey75"
CAPTURE_BUTTON_COLOR = "coral2"
CONTINUE_BUTTON_COLOR = 'SteelBlue1'

KEYBOARD_BUTTON_BACKGROUND_COLOR = 'black'
KEYBOARD_BUTTON_TEXT_COLOR = 'white'
KEYBOARD_MAIN_FRAME_BACKGROUND = "grey90"
KEYBOARD_BUTTON_LOOK = "flat"
KEYBOARD_TOPBAR_BACKGROUND = "black"
KEYBOARD_TRANSPARENCY = 0.7
KEYBOARD_FONT_COLOR = 'white'
KEYBOARD_TOP_BAR_TITLE = "Gelpic Keyboard"

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

class LongPressButton(Button):
    def __init__(self, master=None, command=None, repeat_time=250, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.repeat_time = repeat_time
        self.command_trigger = ' '
        self.bind('<ButtonPress-1>', self.on_press)
        self.bind('<ButtonRelease-1>',self.on_release)
    def on_press(self, event=None):
        if self.command is not None:
            self.command()
        self.command_trigger = self.after(self.repeat_time, self.on_press)
    def on_release(self, event=None):
        self.after_cancel(self.command_trigger)

keys =[
        [
            [
                ("Character_Keys"),
                ({'side':'top','expand':'yes','fill':'both'}),
                [
                    ('1','2','3','4','5','6','7','8','9','0'),
                    ('Q','W','E','R','T','Y','U','I','O','P'),
                    ('A','S','D','F','G','H','J','K','L',' '),
                    (' ','Z','X','C','V','B','N','M','←','→'),
                    (' ', 'Space','Backspace'),
                ]
            ]
        ],

        [
            [
                ("Symbol_Keys"),
                ({'side':'top','expand':'yes','fill':'both'}),
                [
                    ('~','`','!','@','#','$','%','^'),
                    ('&','*','(',')','_','-','+','='),
                    ('{','}','[',']','|','\\',':',';'),
                    ('"',"'",'<','>',',','.','?','/'),
                ]
            ]
        ],
]

class Keyboard(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        # Function For Creating Buttons
        self.create_frames_and_buttons()

    # Function For Extracting Data From KeyBoard Table
    # and then provide us a well looking
    # keyboard gui
    def create_frames_and_buttons(self):
    # take section one by one
        for key_section in keys:
            # create Sperate Frame For Every Section
            store_section = Frame(self)
            store_section.pack(side='left',expand='yes',fill='both',padx=6,pady=6,ipadx=6,ipady=6)

            for layer_name, layer_properties, layer_keys in key_section:
                store_layer = LabelFrame(store_section)#, text=layer_name)
                #store_layer.pack(side='top',expand='yes',fill='both')
                store_layer.pack(layer_properties)
                for key_bunch in layer_keys:
                    store_key_frame = Frame(store_layer)
                    store_key_frame.pack(side='top',expand='yes',fill='both')
                    for k in key_bunch:

                        if len(k)<=3:
                            store_button = LongPressButton(store_key_frame, text=k, width=1, height=1)
                        else:
                            store_button = LongPressButton(store_key_frame, text=k.center(5,' '), height=1)
                        if " " in k:
                            store_button['state']='disable'
                        #flat, groove, raised, ridge, solid, or sunken
                        store_button['relief']="solid"
                        store_button['bg']= KEYBOARD_BUTTON_BACKGROUND_COLOR
                        store_button['fg']= KEYBOARD_BUTTON_TEXT_COLOR
                        store_button['command']=lambda q=k: self.button_command(q)
                        store_button.pack(side='left',fill='both',expand='yes')

        global capslock_button
        def capslock_clicked():
            if(capslock_button['fg']==KEYBOARD_BUTTON_TEXT_COLOR):
                capslock_button['fg'] = 'lawn green'
            else:
                capslock_button['fg'] = KEYBOARD_BUTTON_TEXT_COLOR

        capslock_button = Button(self, bg=KEYBOARD_BUTTON_BACKGROUND_COLOR, fg=KEYBOARD_BUTTON_TEXT_COLOR,text="Capslock", borderwidth=2, width=8, height=1, command=capslock_clicked)
        capslock_button.place(x=8,y=141)
        return

    # Function For Detecting Pressed Keyword.
    def button_command(self, event):
        if(capslock_button['fg']==KEYBOARD_BUTTON_TEXT_COLOR):
            event = event.lower()
        else:
            event = event.capitalize()
        if(event=='←'):
            entry = root.focus_get()
            position = entry.index(INSERT)
            entry.icursor(position - 1)
            entry.xview_moveto(1)
        elif (event=='→'):
            entry = root.focus_get()
            position = entry.index(INSERT)
            entry.icursor(position + 1)
            entry.xview_moveto(1)
        elif(event=="Space" or event=="space"):
            entry = root.focus_get()
            position = entry.index(INSERT)
            entry.insert(position,' ')
            entry.xview_moveto(1)
        elif(event=='Backspace' or event=='backspace'):
            entry = root.focus_get()
            position = entry.index(INSERT)
            entry.delete(position-1)
            entry.xview_moveto(1)
        else:
            entry = root.focus_get()
            position = entry.index(INSERT)
            entry.insert(position,event)
            entry.xview_moveto(1)
        print(event)
        return

class top_moving_mechanism:
    def __init__(self, root, label):
        self.root = root
        self.label = label
    def motion_activate(self, kwargs):
        w,h = (self.root.winfo_reqwidth(), self.root.winfo_reqheight())
        (x,y) = (kwargs.x_root, kwargs.y_root)
        self.root.geometry("%dx%d+%d+%d" % (w,h,x,y))
        return

def sendmail(recipient, subject, content, files_path):
    global email_password, email_address
    print("user: ", email_address)
    print("password: ", email_password)
    emailData = MIMEMultipart()
    emailData['Subject'] = subject
    emailData['To'] = recipient
    emailData['From'] = email_address

    emailData.attach(MIMEText(content))

#     imageData = MIMEImage(open(image, 'rb').read(), 'jpg')
#     imageData.add_header('Content-Disposition', 'attachment; filename="image.jpg"')
#     emailData.attach(imageData)

   #  with open(zip_file,'rb') as file:
#         emailData.attach(MIMEApplication(file.read(), Name= folder_name + '.zip'))

    for file_path in files_path or []:
        with open(file_path, "rb") as fp:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((fp).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(file_path))
            emailData.attach(part)

    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo()

    #session.login(mail_address, password)
    session.login(email_address, email_password)

    session.sendmail(email_address, recipient.split(','), emailData.as_string())
    session.quit

# camera = PiCamera(framerate = Fraction(1,2), sensor_mode = 3)
# camera.resolution = (1024,768)
# camera.rotation = 180
# camera.iso = 200
# camera.shutter_speed = 6000000
# camera.exposure_mode = 'off'
# def camera_capture(output):
#     global camera
#     camera.capture(output)
#     camera.stop_preview()

# def camera_preview():
#     global camera
#     try:
#         camera = PiCamera(framerate = Fraction(1,2), sensor_mode = 3)
#         camera.resolution = (1024,768)
#         camera.rotation = 180
#         camera.iso = 200
#         camera.shutter_speed = 6000000
#         camera.exposure_mode = 'off'
#     except:
#         pass
#     camera.start_preview(alpha=255, fullscreen=False, window=(110,14, 570, 450))


class custom_camera(PiCamera):
    def __init__(self):
        self.framerate = Fraction(1,2)
        self.sensor_mode = 3
        self.rotation = 180
        self.iso = 200
        self.shutter_speed = 6000000
        self.exposure_mode = 'off'
        
    def custom_start_preview():
        self.start_preview(alpha=255, fullscreen=False, window=(110,14, 570, 450))
    def custom_stop_preview():
        self.stop_preview()
    def custom_capture(output):
        self.capture(output)

def main():
    global root
    root = Tk()
    root.geometry('800x480')
    root.configure(background = BACKGROUND_COLOR)
    root.attributes('-fullscreen', True)
    root.resizable(False,False)
    # root.overrideredirect(True)
    # root.wait_visibility(root)
    # root.wm_attributes('-alpha', TRANSPARENCY)
    
    def camera_preview():
        global camera
        try:
            camera.close()
        except:
            pass
            
        camera = PiCamera()
        try:
            camera.framerate = Fraction(3,1)
            camera.resolution = (1024,768)
            camera.sensor_mode = 3
            camera.rotation = 180
            camera.iso = 200
            sleep(2)
            camera.shutter_speed = 6000000
            camera.exposure_mode = 'off'
        except:
            try:
                camera.framerate = Fraction(3,1)
                camera.resolution = (1024,768)
                camera.sensor_mode = 3
                camera.rotation = 180
                camera.iso = 200
                sleep(2)
                camera.shutter_speed = 6000000
                camera.exposure_mode = 'off'
            except:
                pass
                
        camera.start_preview(fullscreen=False, window=(110,14, 570, 450))
     
    def camera_capture(output):
        global camera
        camera.capture(output)
        camera.stop_preview()
        camera.close()

    menu_labelframe =  LabelFrame(root, bg=BACKGROUND_COLOR, width=90, height=479)
    menu_labelframe.place(x=1,y=1)
    gelpic_label = Label(menu_labelframe, bg='dodger blue', text='GELPIC', font=("Courier",16,'bold'), width=6, height=1 )
    gelpic_label.place(x=2,y=1)

    def camera_clicked():
        global display_labelframe

        camera_button['bg'] = MENU_BUTTON_ACTIVE_COLOR
        files_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR
        email_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR

        display_labelframe = LabelFrame(root, bg=BACKGROUND_COLOR, width=709, height=479)
        display_labelframe.place(x=91,y=1)
        control_labelframe = LabelFrame(display_labelframe, bg=BACKGROUND_COLOR, width=100, height=450)
        control_labelframe.place(x=592,y=11)

        display_canvas = Canvas(display_labelframe, bg='grey15', width=580, height=450)
        display_canvas.place(x=11, y=10)
        mode_labelframe = LabelFrame(control_labelframe,text="Mode", bg=BACKGROUND_COLOR, width=91, height=130)
        mode_labelframe.place(x=2,y=312)
  #       brightness_labelframe = LabelFrame(control_labelframe,text="Brightness", bg=BACKGROUND_COLOR, width=91, height=130)
#         brightness_labelframe.place(x=2,y=178)

        def normal_clicked():
            normal_button['bg'] = MENU_BUTTON_ACTIVE_COLOR
            blackwhite_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR
            camera.color_effects  = None
        def blackwhite_clicked():
            blackwhite_button['bg'] = MENU_BUTTON_ACTIVE_COLOR
            normal_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR
            camera.color_effects = (128,128)
        def capture_clicked():
            global camera, a1_label
            if(capture_button['text']=='CAPTURE'):
                try:
                    a1_label.destroy()
                except:
                    pass
                try:
                    path_name = "/home/pi/Gelpic100_Result/"
                    image_name  = strftime("%y-%m-%d-%H-%M-%S.jpg")
                    camera.stop_preview()
                    camera_capture(path_name + image_name)

                    msgbox = messagebox.showinfo('Capture Done','The picture have been saved !')
                    if(msgbox=='ok'):
                        a1 = Image.open(path_name + image_name)
                        crop_width, crop_height = a1.size
                        scale_percent = 53
                        width = int(crop_width * scale_percent / 100)
                        height = int(crop_height * scale_percent / 100)
                        display_img = a1.resize((width,height))
                        a1_display = ImageTk.PhotoImage(display_img)
                        a1_label = Label(display_labelframe, image=a1_display)
                        a1_label.image = a1_display
                        a1_label.place(x=30,y=31)
                        capture_button['text'] = 'CONTINUE'
                        capture_button['bg'] = CONTINUE_BUTTON_COLOR
                        normal_button['state'] = 'disable'
                        blackwhite_button['state'] = 'disable'
    #                     camera_preview()

                except Exception as e:
                        error = messagebox.showerror(str(e), "Err 03", icon = "error")
                        if(error=='ok'):
                            pass
            else:
                try:
                    a1_label.place_forget()
                except:
                    pass
                capture_button['text'] = 'CAPTURE'
                capture_button['bg'] = CAPTURE_BUTTON_COLOR
                normal_button['state'] = 'normal'
                blackwhite_button['state'] = 'normal'

                camera_preview()

        def open_clicked():
            capture_button['text'] = 'CONTINUE'
            capture_button['bg'] = CONTINUE_BUTTON_COLOR
            normal_button['state'] = 'disable'
            blackwhite_button['state'] = 'disable'
            camera.stop_preview()

            file_name = filedialog .askopenfilename(initialdir="/home/pi/Gelpic100_Result", filetypes=[('jpg file','*jpg')])
            if file_name is not None:
                if(file_name[len(file_name)-3:]=='jpg'):
                    a1 = Image.open(file_name)
                    crop_width, crop_height = a1.size
                    scale_percent = 53
                    width = int(crop_width * scale_percent / 100)
                    height = int(crop_height * scale_percent / 100)
                    display_img = a1.resize((width,height))
                    a1_display = ImageTk.PhotoImage(display_img)
                    a1_label = Label(display_labelframe, image=a1_display)
                    a1_label.image = a1_display
                    a1_label.place(x=30,y=31)

        normal_button = Button(mode_labelframe, bg=MENU_BUTTON_ACTIVE_COLOR, text="NORMAL", borderwidth=0, width=7, height=2, command=normal_clicked)
        normal_button.place(x=2, y=10)
        blackwhite_button = Button(mode_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="B&W", borderwidth=0, width=7, height=2, command=blackwhite_clicked)
        blackwhite_button.place(x=2, y=59)
        capture_button = Button(control_labelframe, bg=CAPTURE_BUTTON_COLOR, text="CAPTURE", borderwidth=0, width=8, height=4, command=capture_clicked)
        capture_button.place(x=3, y=80)
        open_button = Button(control_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="OPEN", borderwidth=0, width=8, height=3, command=open_clicked)
        open_button.place(x=3, y=10)
        def bright_cong_clicked():
            global camera
            if(camera.shutter_speed < 6000000):
                camera.shutter_speed = camera.shutter_speed + 500000
            else:
                camera.shutter_speed = 6000000
                camera.stop_preview()
                msg = messagebox.showinfo("","Brightness is at maximum value !")
                camera_preview()
        def bright_tru_clicked():
            global camera
            if(camera.shutter_speed > 1000000):
                camera.shutter_speed = camera.shutter_speed - 500000
            else:
                camera.shutter_speed = 1000000
                camera.stop_preview()
                msg = messagebox.showinfo("","Brightness is at minimum value !")
                camera_preview()

#         bright_cong_button = Button(brightness_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="+", borderwidth=0, width=7, height=2, command=bright_cong_clicked)
#         bright_cong_button.place(x=2, y=10)
#         bright_tru_button = Button(brightness_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="-", borderwidth=0, width=7, height=2, command=bright_tru_clicked)
#         bright_tru_button.place(x=2, y=59)

        camera_preview()

    def files_clicked():
        global display_labelframe
        try:
            camera.stop_preview()
            display_labelframe.place_forget()
        except:
            pass

        display_labelframe = LabelFrame(root, bg=BACKGROUND_COLOR, width=709, height=479)
        display_labelframe.place(x=91,y=1)

        camera_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR
        files_button['bg'] = MENU_BUTTON_ACTIVE_COLOR
        email_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR

        files_text1 = st.ScrolledText(display_labelframe,state='disable',width=70, height=19)
        files_text1.place(x=62,y=4)

        button_labelframe = LabelFrame(display_labelframe, width=578,height=157)
        button_labelframe.place(x=63,y=315)
        button1_labelframe = LabelFrame(button_labelframe, width=459,height=146)
        button1_labelframe.place(x=112,y=3)

        files_list1 = []
        def choosefile_clicked():
            file_name1 = filedialog .askopenfilename(initialdir="/home/pi/Gelpic100_Result", filetypes=[('jpg file','*jpg')])
            if file_name1 is not None:
                err = 0
                for i in files_list1:
                    if(file_name1 == i):
                        err=1
                if(err==0):
                    if(file_name1[len(file_name1)-3:]=='jpg'):
                        files_list1.append(file_name1)
                        files_text1.config(state='normal')
                        files_text1.insert(END, file_name1+"\n")
                        files_text1.config(state='disable')
                else:
                    messagebox.showwarning("","The file has been selected.")

        def removefile_clicked():
            files_text1.config(state='normal')
            files_text1.delete("end-49c","end")
            files_text1.config(state='disable')
            files_list1.pop()

        def clearfile_clicked():
            msg = messagebox.askquestion("","Do you want to delete the entire result file ?")
            if(msg=="yes"):
                files_text1.config(state='normal')
                files_text1.delete("1.0","end")
                files_text1.config(state='disable')
                files_list1.clear()
                shutil.rmtree("/home/pi/Gelpic100_Result")
                f = os.path.join("/home/pi/", "Gelpic100_Result")
                os.mkdir(f)
                messagebox.showinfo("","Deleted")
            else:
                pass

        def deletefile_clicked():
            if(len(files_list1)!=0):
                ask = messagebox.askquestion("","Do you want to delete selected files ?")
                if(ask=='yes'):
                    for i in files_list1:
                        os.system('rm ' + i)
                    files_text1.config(state='normal')
                    files_text1.delete("1.0","end")
                    files_text1.config(state='disable')
                    files_list1.clear()
                    messagebox.showinfo("","Deleted")
            else:
                messagebox.showwarning("","No file chosen")

        def copyfile_clicked():
            if(len(files_list1)!=0):
                dir = filedialog.askdirectory()
                if dir is not None:
                    for i in files_list1:
                        for j in range(len(i)):
                            if(i[j]=='/'):
                                a=j+1
                        name = i[a:]
                        shutil.copyfile(i,dir +"/"+name)

                    messagebox.showinfo("","Completed")
            else:
                messagebox.showwarning("","No file chosen")

        def movefile_clicked():
            if(len(files_list1)!=0):
                dir = filedialog.askdirectory()
                if dir is not None:
                    for i in files_list1:
                        for j in range(len(i)):
                            if(i[j]=='/'):
                                a=j+1
                        name = i[a:]
                        shutil.move(i,dir +"/"+name)
                    files_text1.config(state='normal')
                    files_text1.delete("1.0","end")
                    files_text1.config(state='disable')
                    files_list1.clear()
                messagebox.showinfo("","Completed")
            else:
                messagebox.showwarning("","No file chosen")


        choosefile_button = Button(button_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Choose File", borderwidth=0, width=10, height=2, command=choosefile_clicked)
        choosefile_button.place(x=2, y=2)
        removefile_button = Button(button_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Undo", borderwidth=0, width=10, height=2, command=removefile_clicked)
        removefile_button.place(x=2, y=53)
        clearfile_button = Button(button_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Delete All", borderwidth=0, width=10, height=2, command=clearfile_clicked)
        clearfile_button.place(x=2, y=104)
        deletefile_button = Button(button1_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Delete", borderwidth=0, width=10, height=2, command=deletefile_clicked)
        deletefile_button.place(x=50, y=48)
        copyfile_button = Button(button1_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Copy", borderwidth=0, width=10, height=2, command=copyfile_clicked)
        copyfile_button.place(x=173, y=48)
        movefile_button = Button(button1_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Move", borderwidth=0, width=10, height=2, command=movefile_clicked)
        movefile_button.place(x=296, y=48)

    def email_clicked():
        global display_labelframe
        try:
            camera.stop_preview()
            display_labelframe.place_forget()
        except:
            pass

        camera_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR
        files_button['bg'] = MENU_BUTTON_NONACTIVE_COLOR
        email_button['bg'] = MENU_BUTTON_ACTIVE_COLOR

        display_labelframe = LabelFrame(root, bg=BACKGROUND_COLOR, width=709, height=479)
        display_labelframe.place(x=91,y=1)

       #  global account_active, email_address, email_password
#         fr1 = open("/home/pi/Gelpic_100/.account.txt","r")
#         account_active = int(fr1.readline())
#         email_address = fr1.readline().strip('\n')
#         email_password = fr1.readline().strip('\n')

        if(account_active!=0):
            mail_labelframe = LabelFrame(display_labelframe, text='Information', bg=BACKGROUND_COLOR, width=600, height=100)
            mail_labelframe.place(x=3,y=3)
            file_labelframe = LabelFrame(display_labelframe, text='Attach', bg=BACKGROUND_COLOR, width=600, height=180)
            file_labelframe.place(x=3,y=105)
            send_labelframe = LabelFrame(display_labelframe, bg=BACKGROUND_COLOR, width=94, height=170)
            send_labelframe.place(x=608,y=114)

            recipient_label = Label(mail_labelframe, bg=BACKGROUND_COLOR, text="To    :")
            recipient_label.place(x=10,y=7)
            title_label = Label(mail_labelframe, bg=BACKGROUND_COLOR, text="Title :")
            title_label.place(x=10,y=42)

            global title_entry
            title_entry = Entry(mail_labelframe, width=47, font=('Courier',14))
            title_entry.place(x=60,y=40)
            global user_entry
            recipient_entry = Entry(mail_labelframe, width=47, font=('Courier',14))
            recipient_entry.place(x=60,y=5)

            def logout_clicked():
                fw1= open("/home/pi/Gelpic100/.account.txt", "w")
                fw1.writelines('0\n')
                global account_active
                account_active = 0
                email_clicked()

            logoutfile_button = Button(display_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Logout", borderwidth=0, width=8, height=3, command=logout_clicked)
            logoutfile_button.place(x=608, y=12)

            files_text = st.ScrolledText(file_labelframe,state='disable',width=65, height=9)
            files_text.place(x=54,y=2)

            files_list=[]
            def attach_clicked():
                file_name = filedialog .askopenfilename(initialdir="/home/pi/Gelpic100_Result", filetypes=[('jpg file','*jpg')])
                if file_name is not None:
                    err = 0
                    for i in files_list:
                        if(file_name == i):
                            err=1
                    if(err==0):
                        if(file_name[len(file_name)-3:]=='jpg'):
                            files_list.append(file_name)
                            files_text.config(state='normal')
                            files_text.insert(END, "\n" + file_name)
                            files_text.config(state='disable')
                    else:
                        messagebox.showwarning("","The file has been selected.")

            def remove_clicked():
                files_text.config(state='normal')
                files_text.delete("end-49c","end")
                files_text.config(state='disable')
                files_list.pop()
            attach_button = Button(file_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Add", borderwidth=0, width=3, height=3, command=attach_clicked)
            attach_button.place(x=2, y=3)
            removefile_button = Button(file_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Undo", borderwidth=0, width=3, height=3, command=remove_clicked)
            removefile_button.place(x=2, y=88)


            def send_clicked():
                if(recipient_entry.get()==""):
                    messagebox.showwarning("","Please enter the recipient's email !")
                elif(title_entry.get()==""):
                    messagebox.showwarning("","Please enter the email title !")
                elif(files_text.get("1.0", END)==""):
                    messagebox.showwarning("","There is no file attached")
                else:
                    try:
                        sendmail(recipient_entry.get(), title_entry.get(), "This is an email from Gelpic Device.", files_list)
                        messagebox.showinfo("","Email has been sent successfully.")
                        print(files_list)
                    except Exception as e:
                        error = messagebox.showerror("ERROR", str(e), icon='error')
                        if(error=='ok'):
                            pass

            send_button = Button(send_labelframe, bg=CONTINUE_BUTTON_COLOR, text="Send", borderwidth=0, width=6, height=7, command=send_clicked)
            send_button.place(x=8, y=18)
        else:
            login_labelframe = LabelFrame(display_labelframe,text ="EMAIL LOGIN", bg=BACKGROUND_COLOR, width=703, height=287)
            login_labelframe.place(x=1,y=1)

            user_label = Label(display_labelframe, bg=BACKGROUND_COLOR, text="Email                   :")
            user_label.place(x=111,y=73)
            pass_label = Label(display_labelframe, bg=BACKGROUND_COLOR, text="Device Password :")
            pass_label.place(x=109,y=118)

            user_entry = Entry(login_labelframe, width=30, justify='right', font=('Courier',14))
            user_entry.place(x=240,y=50)
            pass_entry = Entry(login_labelframe, width=30, show='◼', justify='right', font=('Courier',14))
            pass_entry.place(x=240,y=95)

            def login_clicked():
                global email_address, email_password, account_active

                if(user_entry.get()==''):
                    messagebox.showwarning("","Please enter the email address!")
                elif(pass_entry.get()==''):
                    messagebox.showwarning("","Please enter the password !")
                else:
                    email_address = user_entry.get()
                    email_password = pass_entry.get()

                    addressToVerify = email_address
                    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)
                    if(match == None):
                        messagebox.showerror("","Email syntax error")
                    else:
                        domain_name = email_address.split('@')[1]
                        records = dns.resolver.query(domain_name, 'MX')
                        mxRecord = records[0].exchange
                        mxRecord = str(mxRecord)

                        host = socket.gethostname()

                        server = smtplib.SMTP()
                        server.set_debuglevel(0)

                        server.connect(mxRecord)
                        server.helo(host)
                        server.mail('me@domain.com')
                        code, message = server.rcpt(str(addressToVerify))
                        server.quit()

                        if(code==250):
                            server=smtplib.SMTP('smtp.gmail.com:587')
                            server.starttls()
                            try:
                                server.login(email_address,email_password)
                                save_file = open("/home/pi/Gelpic100/.account.txt","w")
                                save_file.writelines('1' + "\n")
                                save_file.writelines(email_address + "\n")
                                save_file.writelines(email_password + "\n")
                                messagebox.showinfo("", "Login Success!")
                                account_active = 1
                                email_clicked()
                            except:
                                messagebox.showerror("","Your password was incorrect\rPlease try again !")
                            server.quit()
                        else:
                            messagebox.showerror("","Your email address was incorrect\rPlease try again !")

            login_button = Button(login_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="Login", borderwidth=0, width=9, height=3, command=login_clicked)
            login_button.place(x=285, y=145)

        keyboard_labelframe = LabelFrame(display_labelframe, bg=BACKGROUND_COLOR, width=709, height=479)
        keyboard_labelframe.place(x=-1,y=290)

        k = Keyboard(keyboard_labelframe, bg=KEYBOARD_MAIN_FRAME_BACKGROUND)
        k.pack(side='top')


    def exit_clicked():
        global camera
        try:
            camera.stop_preview()
        except:
            pass
        msg = messagebox.askquestion("","Do you want to exit ?")
        if(msg=='yes'):
            root.destroy()
        else:
            camera_preview()

    camera_button = Button(menu_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="CAMERA", borderwidth=0, width=7, height=7, command=camera_clicked)
    camera_button.place(x=2, y=31)
    files_button = Button(menu_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="FILES", borderwidth=0, width=7, height=7, command=files_clicked)
    files_button.place(x=2, y=162)
    email_button = Button(menu_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="EMAIL", borderwidth=0, width=7, height=7, command=email_clicked)
    email_button.place(x=2, y=293)
    exit_button = Button(menu_labelframe, bg=MENU_BUTTON_NONACTIVE_COLOR, text="EXIT", borderwidth=0, width=7, height=2, command=exit_clicked)
    exit_button.place(x=2, y=426)

    camera_clicked()

    root.mainloop()
    return

if __name__=='__main__':
    main()
