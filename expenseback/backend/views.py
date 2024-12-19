from django.http.response import JsonResponse
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from expenseback.settings import sendMail, sendResponse ,disconnectDB, connectDB, resultMessages,generateStr

# Odoogiin tsagiig duuddag service
def dt_gettime(request):
    jsons = json.loads(request.body) # request body-g dictionary bolgon avch baina
    action = jsons["action"] #jsons-s action-g salgaj avch baina
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {"action":"gettime"}
    
    # response:
    # {
    #     "resultCode": 200,
    #     "resultMessage": "Success",
    #     "data": [
    #         {
    #             "time": "2024/11/06, 07:53:58"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "gettime",
    #     "curdate": "2024/11/06 07:53:58"
    # }
    d1 = datetime.now()
    respdata = [{'time':d1.strftime("%Y/%m/%d, %H:%M:%S")}]  # response-n data-g beldej baina. list turultei baih
    resp = sendResponse(request, 200, respdata, action)
    # response beldej baina. 6 keytei.
    return resp
# dt_gettime

#login service
def dt_login(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "login",
    #     "gmail": "ganzoo@mandakh.edu.mn",
    #     "password":"73y483h4bhu34buhrbq3uhbi3aefgiu"
    # }
    
    # response:
    # {
    #     "resultCode": 1002,
    #     "resultMessage": "Login Successful",
    #     "data": [
    #         {
    #             "gmail": "ganzoo@mandakh.edu.mn",
    #             "fname": "Ganzo",
    #             "lname": "U",
    #             "last_login": "2024-11-06T15:57:52.996+08:00"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "login",
    #     "curdate": "2024/11/06 07:58:10"
    # }
    try:
        gmail = jsons['gmail'].lower() # get gmail key from jsons
        password = jsons['password'] # get password key from jsons
    except: # gmail, password key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3006, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        
        # Hereglegchiin ner, password-r nevtreh erhtei (is_verified=True) hereglegch login hiij baigaag toolj baina.
        query = F"""SELECT COUNT(*) AS usercount, MIN(fname) AS fname, MAX(lname) AS lname, MIN(username) AS username 
                FROM t_user
                WHERE gmail = '{gmail}' 
                AND is_verified = True 
                AND password = '{password}' 
                AND is_banned = False """ 
        #print(query)
        cursor.execute(query) # executing query
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        print(respRow)
        cursor.close() # close the cursor. ALWAYS

        if respRow[0]['usercount'] == 1: # verified user oldson uyd login hiine
            cursor1 = myConn.cursor() # creating cursor1
            
            # get logged user information
            query = F"""SELECT uid, gmail, fname, lname, last_login, username
                    FROM t_user 
                    WHERE gmail = '{gmail}' AND is_verified = True AND password = '{password}'"""
            
            cursor1.execute(query) # executing cursor1
            columns = cursor1.description # 
            # print(columns, "tuples")
            respRow = [{columns[index][0]:column for index, 
                column in enumerate(value)} for value in cursor1.fetchall()] # respRow is list. elements are dictionary. dictionary structure is columnName : value
            # print(respRow)
            
            uid = respRow[0]['uid'] #
            gmail = respRow[0]['gmail'] # 
            fname = respRow[0]['fname'] #
            lname = respRow[0]['lname'] #
            last_login = respRow[0]['last_login'] #

            respdata = [{'uid': uid,'gmail':gmail, 'fname':fname, 'lname':lname, 'last_login':last_login}] # creating response logged user information
            resp = sendResponse(request, 1002, respdata, action) # response beldej baina. 6 keytei.

            query = F"""UPDATE t_user 
                    SET last_login = NOW()
                    WHERE gmail = '{gmail}' AND is_verified = True AND password = '{password}'"""
            
            cursor1.execute(query) # executing query cursor1
            myConn.commit() # save update query database
            cursor1.close() # closing cursor1
            
        else: # if user name or password wrong 
            data = [{'gmail':gmail}] # he/she wrong username, password. just return username
            resp = sendResponse(request, 1004, data, action) # response beldej baina. 6 keytei.
    except:
        # login service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [] # hooson data bustaana.
        resp = sendResponse(request, 5001, respdata, action) # standartiin daguu 6 key-tei response butsaana
        
    finally:
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
#dt_login

def dt_register(request):
    jsons = json.loads(request.body) # get request body
    action = jsons["action"] # get action key from jsons
    # print(action)
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "register",
    #     "gmail": "ganzoo@mandakh.edu.mn",
    #     "password":"a9b7ba70783b617e9998dc4dd82eb3c5",
    #     "lname":"Ganzo",
    #     "fname":"U"
    # }
    
    # response:
    # {
    #     "resultCode": 200,
    #     "resultMessage": "Success",
    #     "data": [
    #         {
    #             "gmail": "ganzoo@mandakh.edu.mn",
    #             "lname": "U",
    #             "fname": "Ganzo"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "register",
    #     "curdate": "2024/11/06 07:59:23"
    # }
    try :
        gmail = jsons["gmail"].lower() # get gmail key from jsons and lower
        lname = jsons["lname"].capitalize() # get lname key from jsons and capitalize
        fname = jsons["fname"].capitalize() # get fname key from jsons and capitalize
        password = jsons["password"] # get password key from jsons
    except:
        # gmail, password, fname, lname key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3007, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try:
        conn = connectDB() # database holbolt uusgej baina
        cursor = conn.cursor() # cursor uusgej baina
        # Shineer burtguulj baigaa hereglegch burtguuleh bolomjtoi esehiig shalgaj baina
        query = F"SELECT COUNT(*) AS usercount FROM t_user WHERE gmail = '{gmail}' AND is_verified = True"
        # print (query)
        cursor.execute(query) # executing query
        # print(cursor.description)
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        print(respRow)
        cursor.close() # close the cursor. ALWAYS

        if respRow[0]["usercount"] == 0: # verified user oldoogui uyd ajillana
            cursor1 = conn.cursor() # creating cursor1
            # Insert user to t_user
            query = F"""INSERT INTO t_user(gmail, lname, fname, password, is_verified, is_banned, create_date, last_login) 
                        VALUES('{gmail}','{lname}','{fname}', '{password}',
                        False, False, NOW(), '1970-01-01') 
            RETURNING uid"""
            print(query)
            
            cursor1.execute(query) # executing cursor1
            uid = cursor1.fetchone()[0] # Returning newly inserted (uid)
            print(uid, "uid")
            conn.commit() # updating database
            
            token = generateStr(20) # generating token 20 urttai
            query = F"""INSERT INTO t_token(uid, token, token_type, end_date, create_date) VALUES({uid}, '{token}', 'register', NOW() + interval \'1 day\', NOW() )""" # Inserting t_token
            print(query)
            cursor1.execute(query) # executing cursor1
            conn.commit() # updating database
            cursor1.close() # closing cursor1
            
            subject = "User burtgel batalgaajuulah mail"
            bodyHTML = F"""<a target='_blank' href='http://localhost:3000/verified/?token={token}'>CLICK ME to acivate your account</a>"""
            # bodyHTML = F""""""
            sendMail(gmail,subject,bodyHTML)
            
            action = jsons['action']
            # register service success response with data
            respdata = [{"gmail":gmail,"lname":lname,"fname":fname}]
            resp = sendResponse(request, 200, respdata, action) # response beldej baina. 6 keytei.
        else:
            action = jsons['action']
            respdata = [{"gmail":gmail, "lname":lname, "fname":fname}]
            resp = sendResponse(request, 3008, respdata, action) # response beldej baina. 6 keytei.
    except (Exception) as e:
        # register service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"aldaa":str(e)}] # hooson data bustaana.
        resp = sendResponse(request, 5002, respdata, action) # standartiin daguu 6 key-tei response butsaana
        
    finally:
        disconnectDB(conn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
# dt_register

def dt_activate(request):
    try:
        jsons = json.loads(request.body)
        uid = jsons.get("uid")
        token = jsons.get("token")

        if not all([uid, token]):
            return sendResponse(request, 4000, [], "activate")

        conn = connectDB()
        cursor = conn.cursor()

        # Verify token
        query = f"""
        SELECT token, end_date FROM t_token 
        WHERE uid = {uid} AND token = '{token}' AND token_type = 'register'
        """
        cursor.execute(query)
        token_data = cursor.fetchone()
        cursor.close()

        if not token_data or token_data[1] < datetime.now():
            return sendResponse(request, 4001, [], "activate")

        # Activate user
        cursor1 = conn.cursor()
        query = f"UPDATE t_user SET is_verified = True WHERE uid = {uid}"
        cursor1.execute(query)
        conn.commit()

        # Invalidate token
        query = f"DELETE FROM t_token WHERE uid = {uid} AND token = '{token}'"
        cursor1.execute(query)
        conn.commit()
        cursor1.close()

        return sendResponse(request, 200, [], "activate")
    except Exception as e:
        return sendResponse(request, 5002, [{"error": str(e)}], "activate")
    finally:
        disconnectDB(conn)


# Nuuts ugee martsan bol duudah service
def dt_forgot(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    resp = {}
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "forgot",
    #     "gmail": "ganzoo@mandakh.edu.mn"
    # }
    
    # response: 
    # {
    #     "resultCode": 3012,
    #     "resultMessage": "Forgot password huselt ilgeelee",
    #     "data": [
    #         {
    #             "gmail": "ganzoo@mandakh.edu.mn"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "forgot",
    #     "curdate": "2024/11/06 08:00:32"
    # }
    try:
        gmail = jsons['gmail'].lower() # get gmail key from jsons
    except: # gmail key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3016, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        # hereglegch burtgeltei esehiig shalgaj baina. Burtgelgui, verified hiigeegui hereglegch bol forgot password ajillahgui.
        query = f"""SELECT COUNT(*) AS usercount, MIN(gmail) AS gmail , MIN(uid) AS uid
                    FROM t_user
                    WHERE gmail = '{gmail}' AND is_verified = True"""
        cursor.execute(query) # executing query
        cursor.description
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        # print(respRow)
        
        
        if respRow[0]['usercount'] == 1: # verified hereglegch oldson bol nuuts ugiig sergeehiig zuvshuurnu. 
            uid = respRow[0]['uid']
            gmail = respRow[0]['gmail']
            token = generateStr(25) # forgot password-iin token uusgej baina. 25 urttai
            query = F"""INSERT INTO t_token(uid, token, token_type, end_date, create_date) 
            VALUES({uid}, '{token}', 'forgot', NOW() + interval \'1 day\', NOW() )""" # Inserting forgot token in t_token
            cursor.execute(query) # executing query
            myConn.commit() # saving DB
            
            # forgot password verify hiih mail
            subject = "Nuuts ug shinechleh"
            body = f"<a href='http://localhost:3000/verified/user?token={token}'>Martsan nuuts ugee shinechleh link</a>"
            sendMail(gmail, subject, body)
            
            # sending Response
            action = jsons['action']
            respdata = [{"gmail":gmail}]
            resp = sendResponse(request,3012,respdata,action )
            
        else: # verified user not found 
            action = jsons['action']
            respdata = [{"gmail":gmail}]
            resp = sendResponse(request,3013,respdata,action )
            
    except Exception as e: # forgot service deer dotood aldaa garsan bol ajillana.
        # forgot service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"error":str(e)}] # hooson data bustaana.
        resp = sendResponse(request, 5003, respdata, action) # standartiin daguu 6 key-tei response butsaana
    finally:
        cursor.close() # close the cursor. ALWAYS
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
# dt_forgot

# Nuuts ugee martsan uyd resetpassword service-r nuuts ugee shinechilne
def dt_resetpassword(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    resp = {}
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    #  {
    #     "action": "resetpassword",
    #     "token":"145v2n080t0lqh3i1dvpt3tgkrmn3kygqf5sqwnw",
    #     "newpass":"MandakhSchool"
    # }
    
    # response:
    # {
    #     "resultCode": 3019,
    #     "resultMessage": "martsan nuuts ugiig shinchille",
    #     "data": [
    #         {
    #             "gmail": "ganzoo@mandakh.edu.mn"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "resetpassword",
    #     "curdate": "2024/11/06 08:03:25"
    # }
    try:
        newpass = jsons['newpass'] # get newpass key from jsons
        token = jsons['token'] # get token key from jsons
    except: # newpass, token key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3018, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        
        # Tuhain token deer burtgeltei batalgaajsan hereglegch baigaa esehiig shalgana. Neg l hereglegch songogdono esvel songogdohgui. Token buruu, hugatsaa duussan bol resetpassword service ajillahgui.
        query = f"""SELECT COUNT (t_user.uid) AS usercount
                , MIN(gmail) AS gmail
                , MAX(t_user.uid) AS uid
                , MAX(t_token.tid) AS tid
                FROM t_user INNER JOIN t_token
                ON t_user.uid = t_token.uid
                WHERE t_token.token = '{token}'
                AND t_user.is_verified = True
                AND t_token.end_date > NOW()"""
        cursor.execute(query) # executing query
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        # print(respRow)
        if respRow[0]['usercount'] == 1: # token idevhtei, verified hereglegch oldson bol nuuts ugiig shinechlehiig zuvshuurnu.
            uid = respRow[0]['uid']
            gmail = respRow[0]['gmail']
            tid = respRow[0] ['tid'] 
            token = generateStr(40) # shine ajilladaggui token uusgej baina. 40 urttai. 
            query = F"""UPDATE t_user SET password = '{newpass}'
                        WHERE t_user.uid = {uid}""" # Updating user's new password in t_user
            cursor.execute(query) # executing query
            myConn.commit() # saving DB
            
            query = F"""UPDATE t_token 
                SET token = '{token}'
                , end_date = '1970-01-01' 
                WHERE tid = {tid}""" # Updating token and end_date in t_token. Token-iig idevhgui bolgoj baina
            cursor.execute(query) # executing query
            myConn.commit() # saving DB             
            
            # sending Response
            action = jsons['action']
            respdata = [{"gmail":gmail}]
            resp = sendResponse(request,3019,respdata,action )
            
        else: # token not found 
            action = jsons['action']
            respdata = []
            resp = sendResponse(request,3020,respdata,action )
            
    except Exception as e: # reset password service deer dotood aldaa garsan bol ajillana.
        # reset service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"error":str(e)}] # aldaanii medeelel bustaana.
        resp = sendResponse(request, 5005, respdata, action) # standartiin daguu 6 key-tei response butsaana
    finally:
        cursor.close() # close the cursor. ALWAYS
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
#dt_resetpassword

# Huuchin nuuts ugee ashiglan Shine nuuts ugeer shinechleh service
def dt_changepassword(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    resp = {}
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "changepassword",
    #     "gmail": "ganzoo@mandakh.edu.mn",
    #     "oldpass":"a1b2c3d4",
    #     "newpass":"a1b2"
    # }
    
    # response: 
    # {
    #     "resultCode": 3022,
    #     "resultMessage": "nuuts ug amjilttai soligdloo ",
    #     "data": [
    #         {
    #             "gmail": "ganzoo@mandakh.edu.mn",
    #             "lname": "U",
    #             "fname": "Ganzo"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "changepassword",
    #     "curdate": "2024/11/06 08:04:18"
    # }
    try:
        gmail = jsons['gmail'].lower() # get gmail key from jsons
        newpass = jsons['newpass'] # get newpass key from jsons
        oldpass = jsons['oldpass'] # get oldpass key from jsons
    except: # gmail, newpass, oldpass key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3021, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        # burtgeltei batalgaajsan hereglegchiin nuuts ug zuv esehiig shalgaj baina. Burtgelgui, verified hiigeegui, huuchin nuuts ug taarahgui hereglegch bol change password ajillahgui.
        query = f"""SELECT COUNT(uid) AS usercount ,MAX(uid) AS uid
                    ,MIN(gmail) AS gmail
                    ,MIN (lname) AS lname
                    ,MAX (fname) AS fname
                    FROM t_user
                    WHERE gmail='{gmail}'  
                    AND is_verified=true
                    AND password='{oldpass}'"""
        cursor.execute(query) # executing query
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        # print(respRow)
        if respRow[0]['usercount'] == 1: # Burtgeltei, batalgaajsan, huuchin nuuts ug taarsan hereglegch oldson bol nuuts ugiig shineer solihiig zuvshuurnu.
            uid = respRow[0]['uid']
            gmail = respRow[0]['gmail']
            lname = respRow[0]['lname']
            fname = respRow[0]['fname']
            
            query = F"""UPDATE t_user SET password='{newpass}'
                        WHERE uid={uid}""" # Updating user's new password using uid in t_user
            cursor.execute(query) # executing query
            myConn.commit() # saving DB
            
            # sending Response
            action = jsons['action']
            respdata = [{"gmail":gmail, "lname": lname, "fname":fname}]
            resp = sendResponse(request, 3022, respdata, action )
            
        else: # old password not match
            action = jsons['action']
            respdata = [{"gmail":gmail}]
            resp = sendResponse(request, 3023, respdata, action )
            
    except Exception as e: # change password service deer dotood aldaa garsan bol ajillana.
        # change service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"error":str(e)}] # hooson data bustaana.
        resp = sendResponse(request, 5006, respdata, action) # standartiin daguu 6 key-tei response butsaana
    finally:
        cursor.close() # close the cursor. ALWAYS
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
# dt_changepassword
def dt_income(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    resp = {}

    # Example request:
    # {
    #     "action": "logincome",
    #     "uid": 1,
    #     "income": 150,
    #     "incometype": "Freelance project",
    # }

    # Example response:
    # {
    #     "resultCode": 200,
    #     "resultMessage": "success",
    #     "data": [
    #         {
    #             "uid": 2,
    #             "amount": 150.75,
    #             "description": "Freelance project",
    #         }
    #     ],
    #     "size": 1,
    #     "action": "logincome",
    #     "curdate": "2024-12-10 08:15:00"
    # }

    try:
        uid = jsons['uid']
        income = jsons['amount']
        incometype = jsons['description']

    except KeyError as e:
        action = jsons.get('action')
        respdata = []
        resp = sendResponse(request, 4001, respdata, action)
        return resp

    try:
        # Connect to the database
        myConn = connectDB()
        cursor = myConn.cursor()

        # Insert income record
        query = f"""
            INSERT INTO t_income (uid, income, ic_type, ic_date)
            VALUES ('{uid}', {income}, '{incometype}', NOW())
        """
        cursor.execute(query)
        myConn.commit()

        # Prepare response
        respdata = [{
            "uid": uid,
            "income": income,
            "ic_type": incometype,
        }]
        resp = sendResponse(request, 200, respdata, action)

    except Exception as e:
        # Internal error
        action = jsons["action"]
        respdata = [{"error": str(e)}]
        resp = sendResponse(request, 5006, respdata, action)

    finally:
        cursor.close()
        disconnectDB(myConn)
        return resp
        

def dt_all_income(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    resp = {}
    try:
        uid = jsons['uid']
    except: # gmail, newpass, oldpass key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3001, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    # start editing from here
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        query = f"""
        SELECT t_income.ic_type, t_income.income, t_income.ic_date
        FROM t_income
        INNER JOIN t_user ON t_user.uid = t_income.uid
        WHERE t_user.uid = {uid}
                """
        cursor.execute(query)
        myConn.commit()

        # Prepare response
        columns = cursor.description
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        # uid = respRow[0][]
        cursor.close()
        respdata = respRow
        resp = sendResponse(request, 200, respdata, action)

    except Exception as e:
        # Internal error
        action = jsons["action"]
        respdata = [{"error": str(e)}]
        resp = sendResponse(request, 5006, respdata, action)

    finally:
        cursor.close()
        disconnectDB(myConn)
        return resp
        
def expense(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    resp = {}
    # {
    #     "action":"addexpense",
    #     "uid": 1,
    #     "expense":2500,
    #     "expensetype":"buuz"
    # }

#     {
#     "resultCode": 200,
#     "resultMessage": "Success",
#     "data": [
#         {
#             "uid": 1,
#             "expense": 520,
#             "expensetype": "coffee"
#         }
#     ],
#     "size": 1,
#     "action": "addexpense",
#     "curdate": "2024-12-10 15:45:00"
# }

    try:
        # Extract required fields
        uid = jsons['uid']
        expensez = jsons['amount']
        expensetype = jsons['description']

        # Connect to the database
        myConn = connectDB()
        cursor = myConn.cursor()

        # Insert expense record
        query = f"""
            INSERT INTO t_expense (uid, expense, ex_type, ex_date)
            VALUES ('{uid}', -{expensez}, '{expensetype}', NOW())
        """
        cursor.execute(query)
        myConn.commit()

        # Prepare response
        respdata = [{
            "uid": uid,
            "expense": expensez,
            "expensetype": expensetype,
        }]
        return sendResponse(request, 200, respdata, action)

    except KeyError as e:
        # Missing field in JSON
        return sendResponse(request, 4001, [{"error": f"Missing field: {str(e)}"}], "addexpense")

    except Exception as e:
        # Database or other errors
        return sendResponse(request, 5006, [{"error": str(e)}], "addexpense")

    finally:
        # Cleanup resources
        try:
            cursor.close()
            disconnectDB(myConn)
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")


def dt_all_expense(request):
    # return JsonResponse({"message": "Test response"})

    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    resp = {}
    try:
        uid = jsons['uid']
    except: # gmail, newpass, oldpass key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3001, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    # start editing from here
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        query = f"""
        SELECT t.ex_type, t.expense, t.ex_date, t.uid
        FROM t_expense AS t
        WHERE t.uid = '{uid}'
        """
        cursor.execute(query)
        myConn.commit()

        # Prepare response
        columns = cursor.description
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        cursor.close()
        respdata = respRow
        resp = sendResponse(request, 200, respdata, action)

    except Exception as e:
        # Internal error
        action = jsons["action"]
        respdata = [{"error": str(e)}]
        resp = sendResponse(request, 5006, respdata, action)

    finally:
        cursor.close()
        disconnectDB(myConn)
        return resp
        
def totala(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    resp = {}
# {
    # "action":"total",
    # "uid":1
# }
    try:
        uid = jsons['uid']
    except:
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3001, respdata, action) # response beldej baina. 6 keytei.
        return resp
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        query = f"""
        SELECT (t.total_expense + i.total_income) AS total
        FROM (SELECT uid, SUM(expense) AS total_expense FROM t_expense WHERE uid = {uid}
        GROUP BY uid) AS t
        JOIN (SELECT uid, SUM(income) AS total_income FROM t_income WHERE uid = {uid}
        GROUP BY uid) AS i
        ON t.uid = i.uid;

        """
        cursor.execute(query)
        myConn.commit()

        # Prepare response
        result = cursor.fetchone()
        cursor.close()
        if result:
            sun = result[0]
        else: 
            sun = 0
        respdata = [{
            "total": sun,
        }]
        resp = sendResponse(request, 200, respdata, action)

    except Exception as e:
        # Internal error
        action = jsons["action"]
        respdata = [{"error": str(e)}]
        resp = sendResponse(request, 5006, respdata, action)

    finally:
        cursor.close()
        disconnectDB(myConn)
        return resp
        

def history(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    resp = {}
    try:
        uid = jsons['uid']
    except: # gmail, newpass, oldpass key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3001, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    # start editing from here
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        query = f"""
        SELECT 'Expense' AS type, expense, ex_date as date, ex_type as Desc
        FROM t_expense
        WHERE t_expense.uid = {uid}
        UNION ALL
        SELECT 'Income' AS type, income, ic_date as date, ic_type as Desc
        FROM t_income
        WHERE t_income.uid = {uid}
        ORDER BY date DESC;
        """
        cursor.execute(query)
        myConn.commit()

        # Prepare response
        columns = cursor.description
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        cursor.close()
        respdata = respRow
        resp = sendResponse(request, 200, respdata, action)

    except Exception as e:
        # Internal error
        action = jsons["action"]
        respdata = [{"error": str(e)}]
        resp = sendResponse(request, 5006, respdata, action)

    finally:
        cursor.close()
        disconnectDB(myConn)
        return resp
    
def dt_expense_sum(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    resp = {}
    try:
         uid = jsons['uid']
    except: # gmail, newpass, oldpass key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3001, respdata, action) # response beldej baina. 6 keytei.
        return resp
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        query = f"""
        SELECT SUM(t.expense) as Sum
        FROM t_expense as t
        WHERE t.uid = {uid}
        """
        cursor.execute(query)
        myConn.commit()
        result = cursor.fetchone()
        cursor.close()
        if result:
            sun = result[0]
        else: 
            sun = 0
        respdata = [{
            "totalExpense": sun,
        }]
        resp = sendResponse(request, 200, respdata, action)

    except Exception as e:
        # Internal error
        action = jsons["action"]
        respdata = [{"error": str(e)}]
        resp = sendResponse(request, 5006, respdata, action)

    finally:
        cursor.close()
        disconnectDB(myConn)
        return resp
        
def dt_income_sum(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    resp = {}
    try:
         uid = jsons['uid']
    except: # gmail, newpass, oldpass key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3001, respdata, action) # response beldej baina. 6 keytei.
        return resp
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        query = f"""
        SELECT SUM(t.income) as incomesume
        FROM t_income as t
        WHERE t.uid = {uid}
        """
        cursor.execute(query)
        myConn.commit()
        result = cursor.fetchone()
        cursor.close()
        if result:
            sun = result[0]
        else: 
            sun = 0
        respdata = [{
            "totalIncome": sun,
        }]
        resp = sendResponse(request, 200, respdata, action)

    except Exception as e:
        # Internal error
        action = jsons["action"]
        respdata = [{"error": str(e)}]
        resp = sendResponse(request, 5006, respdata, action)

    finally:
        cursor.close()
        disconnectDB(myConn)
        return resp
  


@csrf_exempt # method POST uyd ajilluulah csrf
def checkService(request): # hamgiin ehend duudagdah request shalgah service
    if request.method == "POST": # Method ni POST esehiig shalgaj baina
        try:
            # request body-g dictionary bolgon avch baina
            jsons = json.loads(request.body)
        except:
            # request body json bish bol aldaanii medeelel butsaana. 
            action = "no action"
            respdata = [] # hooson data bustaana.
            resp = sendResponse(request, 3003, respdata) # standartiin daguu 6 key-tei response butsaana
            return JsonResponse(resp) # response bustaaj baina
            
        try: 
            #jsons-s action-g salgaj avch baina
            action = jsons["action"]
        except:
            # request body-d action key baihgui bol aldaanii medeelel butsaana. 
            action = "no action"
            respdata = [] # hooson data bustaana.
            resp = sendResponse(request, 3005, respdata,action) # standartiin daguu 6 key-tei response butsaana
            return JsonResponse(resp)# response bustaaj baina
        
        # request-n action ni gettime
        if action == "gettime":
            result = dt_gettime(request)
            return JsonResponse(result)
        # request-n action ni login bol ajillana
        elif action == "login":
            result = dt_login(request)
            return JsonResponse(result)
        # request-n action ni register bol ajillana
        elif action == "register":
            result = dt_register(request)
            return JsonResponse(result)
        # request-n action ni forgot bol ajillana
        elif action == "forgot":
            result = dt_forgot(request)
            return JsonResponse(result)
        #requestiin action resetpassword-r ajillna
        elif action == "resetpassword":
            result = dt_resetpassword(request)
            return JsonResponse(result)
        #requestiin action changepassword-r ajillna
        elif action == "changepassword":
            result = dt_changepassword(request)
            return JsonResponse(result)
        # request orlog
        elif action == "logincome":
            result = dt_income(request)
            return JsonResponse(result)
        elif action == "allincome":
            result = dt_all_income(request)
            return JsonResponse(result)
        # request tolboruud
        elif action == "addexpense":
            result = expense(request)
            return JsonResponse(result)
        
        elif action == "allexpense":
            result = dt_all_expense(request)
            return JsonResponse(result)
        # request niit mongon dung
        elif action == "total":
            result = totala(request)
            return JsonResponse(result)
        elif action == "history":
            result = history(request)
            return JsonResponse(result)
        elif action == "incomesum":
            result = dt_income_sum(request)
            return JsonResponse(result)
        elif action == "expensesum":
            result = dt_expense_sum(request)
            return JsonResponse(result)
        # request-n action ni burtgegdeegui action bol else ajillana.
        else:
            action = "no action"
            respdata = []
            resp = sendResponse(request, 3001, respdata, action)
            return JsonResponse(resp)
    
    # Method ni GET esehiig shalgaj baina. register service, forgot password service deer mail yavuulna. Ene uyd link deer darahad GET method-r url duudagdana.
    elif request.method == "GET":
        # url: http://localhost:8000/users?token=erjhfbuegrshjwiefnqier
        # Method: GET
        # Body: NONE
        
        # request body: NONE
        
        # response:
        # {
        #     "resultCode": 3011,
        #     "resultMessage": "Forgot password verified",
        #     "data": [
        #         {
        #             "uid": 33,
        #             "gmail": "ganzoo@mandakh.edu.mn",
        #             "token_type": "forgot",
        #             "create_date": "2024-10-16T11:21:57.455+08:00"
        #         }
        #     ],
        #     "size": 1,
        #     "action": "forgot user verify",
        #     "curdate": "2024/11/06 08:06:25"
        # }
        
        token = request.GET.get('token') # token parameteriin utgiig avch baina.
        
        if (token is None):
            action = "no action" 
            respdata = []  # response-n data-g beldej baina. list turultei baih
            resp = sendResponse(request, 3015, respdata, action)
            return JsonResponse(resp)
            # response beldej baina. 6 keytei.
            
            
        try: 
            conn = connectDB() # database holbolt uusgej baina
            cursor = conn.cursor() # cursor uusgej baina
            
            # gadnaas orj irsen token-r mur songoj toolj baina. Tuhain token ni idevhtei baigaag mun shalgaj baina.
            query = F"""
                    SELECT COUNT(*) AS tokencount
                        , MIN(tid) AS tid
                        , MAX(uid) AS uid
                        , MIN(token) token
                        , MAX(token_type) token_type
                    FROM t_token 
                    WHERE token = '{token}' 
                            AND end_date > NOW()"""
            # print (query)
            cursor.execute(query) # executing query
            # print(cursor.description)
            columns = cursor.description #
            respRow = [{columns[index][0]:column for index, 
                column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
            # print(respRow)
            uid = respRow[0]["uid"]
            token_type = respRow[0]["token_type"]
            tid = respRow[0]["tid"]
            
            if respRow[0]["tokencount"] == 1: # Hervee hargalzah token oldson baival ajillana.
                #token_type ni 3 turultei. (register, forgot, login) 
                # End register, forgot hoyriig shagaj uzehed hangalttai. Uchir ni login type ni GET method-r hezee ch orj irehgui.
                if token_type == "register": # Hervee token_type ni register bol ajillana.
                    query = f"""SELECT gmail, lname, fname, create_date 
                            FROM t_user
                            WHERE uid = {uid}""" # Tuhain neg hunii medeelliig avch baina.
                    cursor.execute(query) # executing query
                    
                    columns = cursor.description #
                    respRow = [{columns[index][0]:column for index, 
                        column in enumerate(value)} for value in cursor.fetchall()]
                    gmail = respRow[0]['gmail']
                    lname = respRow[0]['lname']
                    fname = respRow[0]['fname']
                    create_date = respRow[0]['create_date']
                    
                    # Umnu gmail-r verified bolson hereglegch baival tuhain gmail-r dahin verified bolgoj bolohgui. Iimees umnu verified hereglegch oldoh yosgui. 
                    query  = f"""SELECT COUNT(*) AS verifiedusercount 
                                , MIN(gmail) AS gmail
                            FROM t_user 
                            WHERE gmail = '{gmail}' AND is_verified = True"""
                    cursor.execute(query) # executing query
                    columns = cursor.description #
                    respRow = [{columns[index][0]:column for index, 
                        column in enumerate(value)} for value in cursor.fetchall()]
                    
                    if respRow[0]['verifiedusercount'] == 0:
                        
                        # verified user oldoogui tul hereglegchiin verified bolgono.
                        query = f"UPDATE t_user SET is_verified = true WHERE uid = {uid}"
                        cursor.execute(query) # executing query
                        conn.commit() # saving database
                        
                        token = generateStr(30) # huuchin token-oo uurchluh token uusgej baina
                        # huuchin token-g idevhgui bolgoj baina.
                        query = f"""UPDATE t_token SET token = '{token}', 
                                    end_date = '1970-01-01' WHERE tid = {tid}"""
                        cursor.execute(query) # executing query
                        conn.commit() # saving database
                        
                        # token verified service-n response
                        action = "userverified"
                        respdata = [{"uid":uid,"gmail":gmail, "lname":lname,
                                    "fname":fname,"token_type":token_type
                                    , "create_date":create_date}]
                        resp = sendResponse(request, 3010, respdata, action) # response beldej baina. 6 keytei.
                    else: # user verified already. User verify his or her mail verifying again. send Response. No change in Database.
                        action = "user verified already"
                        respdata = [{"gmail":gmail,"token_type":token_type}]
                        resp = sendResponse(request, 3014, respdata, action) # response beldej baina. 6 keytei.
                elif token_type == "forgot": # Hervee token_type ni forgot password bol ajillana.
                    
                    query = f"""SELECT gmail, lname, fname, create_date FROM t_user
                            WHERE uid = {uid} AND is_verified = True""" # Tuhain neg hunii medeelliig avch baina.
                    cursor.execute(query) # executing query
                    columns = cursor.description #
                    respRow = [{columns[index][0]:column for index, 
                        column in enumerate(value)} for value in cursor.fetchall()]
                    
                    gmail = respRow[0]['gmail']
                    lname = respRow[0]['lname']
                    fname = respRow[0]['fname']
                    create_date = respRow[0]['create_date']
                    
                    # forgot password check token response
                    action = "forgot user verify"
                    respdata = [{"uid":uid,"gmail":gmail,  "token_type":token_type
                                , "create_date":create_date}]
                    resp = sendResponse(request, 3011, respdata, action) # response beldej baina. 6 keytei.
                else:
                    # token-ii turul ni forgot, register ali ali ni bish bol buruu duudagdsan gej uzne.
                    # login-ii token GET-r duudagdahgui. 
                    action = "no action"
                    respdata = []
                    resp = sendResponse(request, 3017, respdata, action) # response beldej baina. 6 keytei.
                
            else: # Hervee hargalzah token oldoogui bol ajillana.
                # token buruu esvel hugatsaa duussan . Send Response
                action = "notoken" 
                respdata = []
                resp = sendResponse(request, 3009, respdata, action) # response beldej baina. 6 keytei.
                
        except:
            # GET method dotood aldaa
            action = "no action" 
            respdata = []  # response-n data-g beldej baina. list turultei baih
            resp = sendResponse(request, 5004, respdata, action)
            # response beldej baina. 6 keytei.
        finally:
            cursor.close()
            disconnectDB(conn)
            return JsonResponse(resp)
    
    # Method ni POST, GET ali ali ni bish bol ajillana
    else:
        #GET, POST-s busad uyd ajillana
        action = "no action"
        respdata = []
        resp = sendResponse(request, 3002, respdata, action)
        return JsonResponse(resp)
