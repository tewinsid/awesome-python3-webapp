#!/usr/env/bin python
#! -*- coding=utf-8 -*-

'''
    为数据交换压力测试准备数
'''
import ibm_db
from uuid import uuid4
CONNSTR = 'DATABASE=SINOSP;HOSTNAME=10.24.1.20;PORT=50001;PROTOCOL=TCPIP;UID=SINO_ZGS;PWD=123456;'
def commonSql(conn, tableName, limitId, limitValue, idIndex,hthFlag):
    #conn = ibm_db.conneddct(CONNSTR, '', '')
    #插入合同 合同条款 合同明细 单据操作记录
    querySql = "select * from "+ tableName +" where "+limitId+" ='"+ limitValue+"'"
    print('querySql is : ' + querySql)
    result = ibm_db.exec_immediate(conn, querySql)
    resultList = list(ibm_db.fetch_tuple(result))
    tempsql = "insert into "+tableName+" values(%s)"
    tempString = ''
    for x in resultList:
        if type(x) == int:
            tempString += '%d, '
        elif type(x) == float:
            tempString += '%f, '
        else:
            tempString += "'%s', "
    tempString = tempString[0:-2]
    sql = tempsql % tempString
    for x in range(100,800):
        id = str(uuid4()).replace('-' ,'')
        resultList[idIndex] = id
        if hthFlag:
            resultList[3] = 'CG_HTSP201803300' + str(x)
        finalsql = sql % tuple(resultList)
        #ibm_db.exec_immediate(conn, finnalsql)
        print(finalsql)




if __name__ == '__main__':

    conn = ibm_db.connect(CONNSTR, '', '')
    sql = "select * from rc_ht where rc_ht_hth='CG_HTSP201803300004'"
    result = ibm_db.exec_immediate(conn ,sql)
    ht = ibm_db.fetch_assoc(result)
    htnm = ht['RC_HT_HTNM']
    
    #查询合同
    commonSql(conn, 'rc_ht', 'rc_ht_hth', 'CG_HTSP201803300004', 1, True)
    commonSql(conn, 'rc_htmx', 'rc_htmx_htnm', htnm, 1, False) 
    #插入rc_ht表
    #insert rc_htmx table
