from datetime import date
import mysql.connector as mycon
con = mycon.connect(host="localhost",user="root",password="64fbr",database="HMS")
def showmenu():
    while True:
        print('''Enter the Respective numbers to perform an Operation
              1)  Create a New Room
              2)  Show All Rooms
              3)  Show All Vacant Rooms
              4)  Show All Occupied Rooms
              5)  Book Room
              6)  Update Price
              7)  Checkout and Bill
              8)  Calculate Price
              9)  Entire Booking History
              10) Search Records
              11) Close Application''')
        choice=int(input("Enter Your Choice: "))
        if choice == 1:
            createRoom()
        elif choice == 2:
            showRooms()
        elif choice == 3:
            showVacantRooms()
        elif choice == 4:
            showOccupiedRooms()
        elif choice == 5:
            if bookRoom():
                print("Create new rooms to accomodate more people ")
        elif choice == 6:
            update()
        elif choice == 7:
            checkout()
        elif choice == 8:
            rtype = input("Enter Room Type (Simple or Delux) ")
            num = int(input("Enter Number of People "))
            days = int(input("Enter the number of Days "))
            calculate(rtype, num, days)
        elif choice == 9:
            history()
        elif choice == 10:
            searchRecord()
            while True:
                x = input("Enter (Y/N) Yes or No to continue search ").upper()
                if x == 'Y':
                    searchRecord()
                elif x == 'N':
                    break
                else:
                    print("WRONG INPUT!")

        elif choice == 11: 
            break 
        else:
            print("Wrong Input!")

def createRoom():
    print("----ENTER ROOM DETAILS----")
    rno = int(input("Enter the New Room No "))
    rtype = input("Enter the Room Type (Simple or Delux) ")
    rstr = int(input("Enter the strength of the room "))
    q = "insert into room(Rm_No,Room_Type,Room_Strength) value(%s,%s,%s)"
    data = (rno,rtype,rstr)
    cur = con.cursor()
    cur.execute(q,data)
    con.commit()
    print("---- ROOM CREATED SUCCESSFULLY ----")

def showRooms():
    q = "select * from room"
    cur = con.cursor()
    cur.execute(q)
    res = cur.fetchall()
    for row in res:
        print(row)

def showVacantRooms():
    q = "select * from room where Status='Empty'"
    cur = con.cursor()
    cur.execute(q)
    res = cur.fetchall()
    if res == []:
        print("All Rooms are Occupied")
        return True
    else:
        for row in res:
            print(row)
        return False

def showOccupiedRooms():
    q = "select Rm_No, Name, Phone from room r, history h where Status!='Empty' and r.gu_id=h.gu_id"
    cur = con.cursor()
    cur.execute(q)
    res = cur.fetchall()
    for row in res:
        print(row)

def bookRoom():
    while True:
        rno = input("Enter the room number: ")
        q = "select Status from room where Rm_No="+rno
        cr = con.cursor()
        cr.execute(q)
        r = cr.fetchone()
        if r[0]!='Empty':
            print("Room Already Occupied") 
            if showVacantRooms():
                return True
        else:
            break
    num = int(input("Enter number of People: "))    
    name = input("Enter Customer Name: ")
    idtype = input("Enter the ID submitted(PAN Card/License/Aadhar Card/Passport) : ")
    idno = input("Enter the ID number : ")
    address = input("Enter Address : ")
    phone = input("Enter Phone number : ")
    gender = input("Enter Gender : ")
    dcheckin = date.today()
    
    q = "SELECT COUNT(*) FROM history"
    cr.execute(q)
    res = cr.fetchone()

    # Check if there are any records in the "history" table
    if res:
        count = res[0]
        guestid = count + 1
        print(f"New guest ID: {guestid}")
    else:
        guestid = 1  # If there are no records, start with ID 1
        print("No history records found. Starting with guest ID 1.")

    q = "insert into history(Room_No,Name,ID,ID_NO,Address,No_of_People,Checkin,Gender,Phone,gu_id) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" 
    data = (rno,name,idtype,idno,address,num,dcheckin,gender,phone,guestid)
    cr.execute(q,data)
    con.commit()
    q = "update room set Status='Full',gu_id=%s where Rm_No=%s"
    data = (guestid,rno)
    cr.execute(q,data)
    con.commit()
    print("ROOM BOOKED")
    return False

def update(): #Update the price of rooms
    q = "select * from rent"
    cr = con.cursor()
    cr.execute(q)
    res = cr.fetchall()
    print("The Current Price is:")
    for row in res:
        print(row)
    s = int(input("Enter the New Price of Simple room "))
    d = int(input("Enter the New Price of Delux room "))
    q = "update rent set Price = CASE WHEN Room_Type = 'Simple' THEN %s WHEN Room_Type = 'Delux' THEN %s END;"
    data = (s,d)
    cr.execute(q,data)
    con.commit()
    print("PRICE UPDATED !!")

def checkout():
    guestid = input("Enter the Guest id for Checkout ")
    q = "select * from room where gu_id="+guestid
    cr = con.cursor()
    cr.execute(q)
    res = cr.fetchall()
    if res == []:
        print("THE GUEST ID IS INVALID!")
    else:
        q = "select Room_Type from room where gu_id="+guestid
        cr.execute(q)
        rtype = cr.fetchone()
        chkout = input("Enter Date of Check out (yyyy-mm-dd) :")
        q = "select No_of_People from history where gu_id="+guestid
        cr.execute(q)
        num = cr.fetchone()
        q = "select day(Checkin) from history where gu_id="+guestid
        cr.execute(q)
        d = cr.fetchone()
        #print(rtype)
        #print(num)
        #print(type(d[0]))
        #days = chkout.day()-d
        print("------ BILL-------")
        price = calculate(rtype[0],num[0],1)
        q = "update history set Checkout=%s,Price=%s where gu_id="+guestid
        data = (chkout,price)
        cr.execute(q,data)
        con.commit()
        
        q = "update room set Status='Empty', gu_id = NULL where gu_id="+guestid
        cr.execute(q)
        con.commit()
        q = "select * from history where gu_id="+guestid
        cr.execute(q)
        res = cr.fetchall()
        for row in res:
            print(row)
        print("--HISTORY UPDATED--")
        print("-- CHECKOUT SUCCESSFUL --")

def calculate(x,y,z):
    print("The price is: ")
    q =  "select Price from rent where Room_Type=%s"
    cr = con.cursor()
    cr.execute(q,(x,))
    rate = cr.fetchone()
    rate = rate[0]*y*z
    print(f"THE TOTAL AMOUNT FOR {y} PEOPLE FOR {z} DAYS IN A {x} ROOM IS: Rs{rate}")
    return rate

def history():
    print("--- ENTIRE BOOKING HISTORY ---")
    q="select * from history"
    cur = con.cursor()
    cur.execute(q)
    res = cur.fetchall()
    for row in res:
        print(row)

def searchRecord():
    print("Search By the following choices")
    print('''
          1) Name
          2) ID-NO
          3) Address
          4) Sort By Checkin Date
          5) Sort By Checkout Date
          6) Phone Number
          7) Sort By Gender''')
    cr = con.cursor()
    choice = int(input("Enter the choice: "))
    #Name 
    if choice == 1:
        name = input("Enter the Name: ")
        q = "select * from history where Name="+name
        cr.execute(q)
        res = cr.fetchall()
        if res:
            for row in res:
                print(row)
        else:
            print("There is no record by the name: "+name)
    #ID-NO
    elif choice == 2:
        id_no = input("Enter the ID-NO: ")
        q = "select * from history where ID_NO="+id_no
        cr.execute(q)
        res = cr.fetchall()
        if res:
            for row in res:
                print(row)
        else:
            print(f"The ID-NO - {id_no} does not exist in our records")
    #Address
    elif choice == 3:
        address = input("Enter the Address: ")
        q = "select * from history where Address like %s"
        cr.execute(q,('%'+address+'%',))
        res = cr.fetchall()
        if res:
            for row in res:
                print(row)
        else:
            print("No records found by the address: "+address)

    #Sort by Checkin
    elif choice == 4:
        date = input("Enter the Checkin Date: ")
        q = "select * from history where Checkin="+date
        cr.execute(q)
        res = cr.fetchall()
        if res:
            for row in res:
                print(row)
        else:
            print("No records for Checkin on "+date)
    #Sort by Checkout
    elif choice == 5:
        date = input("Enter the Checkout Date: ")
        q = "select * from history where Checkout="+date
        cr.execute(q)
        res = cr.fetchall()
        if res:
            for row in res:
                print(row)
        else:
            print("No records for Checkout on "+date)
    #Phone number
    elif choice == 6:
        ph = input("Enter the phone number: ")
        q = "select * from history where Phone="+ph
        cr.execute(q)
        res = cr.fetchall()
        for row in res:
            print(row)
    #Sort by gender
    elif choice == 7:
        gen = input("Enter the Gender: ")
        q = "select * from history where Gender=%s"
        cr.execute(q,(gen,))
        res = cr.fetchall()
        for row in res:
            print(row)
    else:
        print("WRONG CHOICE!")
if con.is_connected():
    showmenu()
else:
    print("ERROR ESTABLISHING MYSQL CONNECTION!")   