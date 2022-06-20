import scapy.all as scapy
import pandas as pd
import argparse as ag
import subprocess as sub
import re
import time 
import threading
import sys

class getting():
    
    def __init__(self):
        ipmac_obj =ag.ArgumentParser()
        ipmac_obj.add_argument("--info","-in",dest="info",help="[+]{Information}A program which finds the All the IP and MAC Address of an Network.")
        ipmac_obj.add_argument("--ip","-p",dest="ip",help="[+]{Compulsory}==> Enter the IP Range to send ARP Packet of op-'who has' to those IP's.\n==>\tIn Linux Distros By Default, it is system LAN IP Range.")
        ipmac_obj.add_argument("--mac","-m",dest="mac",help="[+]{Compulsory}==> Enter the MAC to send Ether\ARP Packet of op-'who has' to the specified MAC.\n==>\tBy Default, it is broadcast MAC.")
        ipmac_obj.add_argument("--interface","-i",dest="iface",help="[+]{Optional}==>  Enter the INTERFACE which automatically gets the IP Range of that specified LAN to send Ether\ARP Packet of op-'who has' to the specified IP's.\n==>\tIf IP and INTERFACE should not be entered together, if done, then IP Value will be taken as Valid.")
        ipmac_obj.add_argument("--timeout","-t",dest="timeout",help="[+]{Compulsory}==> Enter the timeout to receive the broadcasted Ether\ARP Packet in seconds. \n==>\tBy Default, the Timeout is 1 second.")
        ipmac_obj.add_argument("--outfile","-o",dest="outfile",help="[+]{Optional}==> Enter the  \n==>\t It is always a CSV File. ==> If an existing file is given, it would just append the information.")
        args=ipmac_obj.parse_args()
        ip,mac,iface,timeout,outfile=args.ip,args.mac,args.iface,args.timeout,args.outfile
        self.ip,self.mac,self.iface,self.timeout,self.outfile=ip,mac,iface,timeout,outfile
        

    def MAC(self):
        if self.mac==None:
            print("\033[96m\n1.Get Default Values for MAC.")
            print("2.Get User-Defined Values for MAC")
            choice=(input("\nEnter Your Choice ==> "))
            if choice=="1":
                self.mac="ff:ff:ff:ff:ff:ff"
            elif choice=="2":
                self.mac=input("\nEnter MAC Address ==> ")
                try:
                    temp_mac=self.mac.split(":")
                    assert(sum([ len(i)==2 and i.isalnum() for i in temp_mac if len(temp_mac)==6])==6)
                except Exception as e:
                       print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m")
                       print("\033[92m"+"Invalid MAC Address,Try Again"+"\033[91m"+"..."+"\033[0m")
                       getting().MAC()
            else:
                print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[94m"+"Invalid Choice,Try Again"+"\033[91m"+"..."+"\033[0m")
                getting().MAC()
        else:
            try:
                temp_mac=self.mac.split(":")
                assert(sum([ len(i)==2 and i.isalnum() for i in temp_mac if len(temp_mac)==6])==6)
            except Exception as e:
                print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m",end=" ")
                print(e,end=" ")
                raise Exception
        print("\n\033[1m"+"\033[92m"+"["+"+"+"]"+"\033[94m"+" Setting MAC"+"\033[91m"+"  ==>  "+"\033[92m"+"\033[4m"+self.mac+"\033[0m")
        return self.mac
      
    def IP(self):
        ip_iface_list=[]
        if self.ip==None:
            if self.iface==None:
                print("\n\033[96m1.Get Default Values for IP.")
                print("2.Get User-Defined Values for IP.")
                choice=(input("\nEnter Your Choice ==> "))
                if choice=="1":
                    iface_op= (sub.check_output(["route","-n"])).decode()                 
                    ip_iface_name = re.findall(r"0\.0\.0\.0\s+((\d{1,3}\.){3})+\d{1,3}.+0\.0\.0\.0\s.+\s(\w+)\s", iface_op) 
                    self.ip=ip_iface_name[0][0]+"0/24"
                elif choice=="2":
                    print("\n\033[96m1.IP Address of this System on the Network")
                    print("2.Interface Name(Available for linux only)")
                    choice=(input("\nEnter Your Choice ==> "))
                    if choice=="1":
                        try:
                            temp_ip=input("\n\033[96mEnter IP Range ==>").split(".")
                            if "/" in temp_ip[3]:
                                assert((sum([ (1<=len(str(int(i))) and len(str(int(i)))<=3 and 0<=int(i)<=255)  for i in temp_ip if i!=temp_ip[3] ])==3 and len(temp_ip)==4) and (len(temp_ip[0])==3 and len(temp_ip[1])==3))                                
                            else:
                                assert((sum([ (1<=len(str(int(i))) and len(str(int(i)))<=3 and 0<=int(i)<=255)  for i in temp_ip ])==4 and len(temp_ip)==4) and (len(temp_ip[0])==3 and len(temp_ip[1])==3))
                            self.ip=temp_ip[0]+"."+temp_ip[1]+"."+temp_ip[2]+"."+"0/24"
                        except Exception as e:
                            print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m")
                            print(e)
                            print("\033[92m"+"Invalid IP Address,Try Again"+"\033[91m"+"..."+"\033[0m")
                            getting().IP()
                    elif choice=="2":
                        iface_op= (sub.check_output(["route","-n"])).decode()                
                        ip_iface_name = re.findall(r"0\.0\.0\.0\s+((\d{1,3}\.){3})+\d{1,3}.+0\.0\.0\.0\s.+\s(\w+)\s", iface_op) 
                        for i in ip_iface_name:
                            ip_iface_dict={"IP":i[0]+"0/24","Iface":i[2]}
                            ip_iface_list.append(ip_iface_dict)
                        ip_iface_DF=pd.DataFrame(ip_iface_list,columns=["IP","Iface"])
                        print("\n","\033[1m","\033[92m",ip_iface_DF,"\033[0m")
                        try:
                            choice=int(input("\n\033[96mEnter your Choice ==> "))
                            self.iface=ip_iface_list[choice]["Iface"]
                            self.ip=ip_iface_list[choice]["IP"]
                            print("\n\033[1m"+"\033[92m"+"["+"+"+"]"+"\033[94m"+" Setting Interface"+"\033[91m"+"  ==>  "+"\033[92m"+"\033[93m"+"\033[4m"+ self.iface+"\033[0m")
                        except Exception as e:
                            print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m")
                            print(e)
                            print("\033[92m"+"Invalid Choice,Try Again"+"\033[91m"+"..."+"\033[0m")
                            getting().IP()
                    else:
                        print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[94m"+"Invalid Choice,Try Again"+"\033[91m"+"..."+"\033[0m")
                        getting().IP()
                else:
                    print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[94m"+"Invalid Choice,Try Again"+"\033[91m"+"..."+"\033[0m")
                    getting().IP()
            elif self.iface:
                    iface_op=(sub.check_output(["route","-n"])).decode()                 #check_output function prints on screen and returns as bytes type but re module accepts only str format, so converting bytes into str using .decode(
                    ip_iface_name = re.findall(r"0\.0\.0\.0\s+((\d{1,3}\.){3})+\d{1,3}.+0\.0\.0\.0\s.+\s(\w+)\s", iface_op) 
                    for i in ip_iface_name:
                        if self.iface in i:
                            self.ip=i[0]+"0/24"
                            print("\n\033[1m"+"\033[92m"+"["+"+"+"]"+"\033[94m"+" Setting Interface"+"\033[91m"+"  ==>  "+"\033[92m"+"\033[93m"+ "\033[4m"+self.iface+"\033[0m")
        else:
            temp_ip=self.ip.split(".")
            try:
                if "/" in temp_ip[3]:
                    assert((sum([ (1<=len(str(int(i))) and len(str(int(i)))<=3 and 0<=int(i)<=255)  for i in temp_ip if i!=temp_ip[3] ])==3 and len(temp_ip)==4) and (len(temp_ip[0])==3 and len(temp_ip[1])==3))                                
                else:
                    assert((sum([ (1<=len(str(int(i))) and len(str(int(i)))<=3 and 0<=int(i)<=255)  for i in temp_ip ])==4 and len(temp_ip)==4) and (len(temp_ip[0])==3 and len(temp_ip[1])==3))
            except Exception as e:
                self.ip=None
                print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m")
                print(e,end=" ")
                raise Exception            
            else:
                self.ip=temp_ip[0]+"."+temp_ip[1]+"."+temp_ip[2]+"."+"0/24"
        print("\n\033[1m"+"\033[92m"+"["+"+"+"]"+"\033[94m"+" Setting IP Address"+"\033[91m"+"  ==>  "+"\033[92m"+"\033[4m"+self.ip+"\033[0m")
        return ip_iface_list,self.ip,self.mac
        
    def TIME(self):
        if self.timeout==None:
            print("\n\033[96m1.Get Default Values for TimeOut.")
            print("2.Get User-Defined Values for TimeOut.")
            choice=(input("\nEnter Your Choice ==> "))
            if choice=="1":
                self.timeout=1                
            elif choice=="2":
                self.timeout=int(input("\n\033[96mEnter the Timeout ==>"))
            else:
                print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[94m"+"Invalid Choice,Try Again"+"\033[91m"+"..."+"\033[0m")
                getting().TIME()
        print("\n\033[1m"+"\033[92m"+"["+"+"+"]"+"\033[94m"+" Setting Timeout"+"\033[91m"+"  ==>  "+"\033[92m"+"\033[4m"+str(self.timeout)+"s"+"\033[0m")
        return self.timeout

    def csv_file(self):
        if self.outfile==None:
            print("\n\033[96mWould you like to save the results in a csv File?")
            print("1.YES")
            print("2.NO")
            choice=(input("\nEnter Your Choice ==> "))
            if choice=="1":
                print("\n\033[96mFile Name Type :")
                print("1.Default Name")
                print("2.Custom Name")
                choice=(input("\nEnter Your Choice ==> "))
                if choice=="1":
                    t = time.localtime(time.time())
                    cur_time="==>"+str(t.tm_hour)+":"+str(t.tm_min)+":"+str(t.tm_sec)+"_"+str(t.tm_mday)+"-"+str(t.tm_mon)+"-"+str(t.tm_year)
                    file_name="Ip_Mac"+cur_time
                    self.outfile=file_name+".csv"
                elif choice=="2":
                    file_name=input("Enter the File Name: ")
                    self.outfile=file_name+".csv"
                else:
                    print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[94m"+"Invalid Choice,Try Again"+"\033[91m"+"..."+"\033[0m")
                    getting().csv_file()
            elif choice=="2":
                pass
            else:
                print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[94m"+"Invalid Choice,Try Again"+"\033[91m"+"..."+"\033[0m")
                getting().csv_file()
        else:
            self.outfile=self.outfile+".csv"
        print("\n\033[1m"+"\033[92m"+"["+"+"+"]"+"\033[94m"+" Setting FileName"+"\033[91m"+"  ==>  "+"\033[92m"+"\033[4m"+str(self.outfile)+"\033[0m")
        return self.outfile

    
class scanning(getting,threading.Thread):        
    
    def __init__(self):
        getting.__init__(self)
        threading.Thread.__init__(self)

    def scan(self):
        print("\n\n\033[93m")
        t = time.localtime(time.time())
        cur_time=str(t.tm_hour)+":"+str(t.tm_min)+":"+str(t.tm_sec)+"-"+str(t.tm_mday)+"/"+str(t.tm_mon)+"/"+str(t.tm_year)
        arg_details=[cur_time,self.ip,self.mac,str(self.timeout)+"s",self.iface]
        broadcast_arpreq=scapy.Ether(dst=self.mac)/scapy.ARP(pdst=self.ip)
        clients,client_list=scapy.srp(broadcast_arpreq,timeout=int(self.timeout))[0],[]
        for client in clients:
            client_dict={"------IP------":client[1].psrc,"--------MAC--------":client[1].hwsrc}
            client_list.append(client_dict)
        for details in arg_details:
            details_dict={"----Details_Info----":details}
            client_list.append(details_dict)
        self.client_list=client_list
        return self.client_list,clients
    
    def print_clients(self):
        client_DF=pd.DataFrame(self.client_list)  
        self.client_DF=client_DF
        print("\n\033[92m",self.client_DF,"\033[0m")
        return self.client_DF

    def csv_file_out(self):
        if self.outfile==None:
            pass
        else:
            (self.client_DF).to_csv(self.outfile,mode="a")
        
class timing(getting,threading.Thread):
    	
    def __init__(self):
        getting.__init__(self)
        threading.Thread.__init__(self)
        
    def my_timer(self):
        time.sleep(1)
        for i in range(int(self.timeout)-1,-1,-1):
            print("\r\033[1m"+"\033[92m"+"["+"+"+"]"+"\033[94m"+" Timer "+"\033[91m"+"  ==>  "+"\u001b[38;5;"+str(i+150) + "m"+"\033[4m"+str(i)+"s"+"\033[0m . . . . . .",end=" ")
            time.sleep(1)

class Executor(scanning,timing,getting,threading.Thread):

    def __init__(self):
        getting.__init__(self)
        scanning.__init__(self)
        timing.__init__(self)
        threading.Thread.__init__(self)
        
def main():
    ipmac=Executor()
    try:
        ipmac.MAC()
    except Exception as e:
        ipmac.mac=None
        print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m")
        print("\033[92m"+"Invalid MAC Address,Try Again"+"\033[91m"+"..."+"\033[0m")
        ipmac.MAC()
    try:
        ipmac.IP()
    except Exception as e:
        ipmac.ip=None
        print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m")
        print("\033[92m"+"Invalid IP Address,Try Again"+"\033[91m"+"..."+"\033[0m")
        ipmac.IP()
    ipmac.TIME()
    ipmac.csv_file()
    t1=threading.Thread(target=ipmac.scan)
    t2=threading.Thread(target=ipmac.my_timer)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    ipmac.print_clients()
    try:
        ipmac.csv_file_out()
    except Exception as e:
        print("\n\033[1m"+"\033[91m"+"["+"-"+"]"+"\033[93m",type(e).__name__,"\033[96m")
        print("\033[92m"+"Invalid File,Try Again"+"\033[91m"+"..."+"\033[0m")
        ipmac.csv_file_out()
    print("\nAll Done...")


if __name__=="__main__":
    main()
