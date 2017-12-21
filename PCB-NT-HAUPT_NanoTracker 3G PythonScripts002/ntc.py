import MDM
import MOD
import SER
import SER2
import GPIO
import GPS_RS
import MODEM_RS
import time

#You need to set these 6 parameters
CumulocityServer = 'xxxx.cumulocity.com'  #replace xxxx with your tenant at Cumulocity
Device_B64_Authentication = 'dGVuYW50X25hbWUvdXNlcm5hbWU6cGFzc3dvcmQ='  #this should be your your authentication string. It is created by doing Base64 encoding for tenant_name/username:password
                                                                        #you can use this webtool to create the authentication string: https://www.base64encode.org/
Cumulocity_Device_ID = '2141542'    #Device ID that is created at Cumulocity platform. If you need assistance creating devices there, please contact Round Solutoins
MOD_APN = 'surfo2'     #set the APN here based on your operator
MOD_Username = ''           #set the APN username here based on your operator
MOD_Password = ''           #set the APN password here based on your operator


m_gpsmanager = GPS_RS.Gps_RS()
m_modemmanager = MODEM_RS. Modem_RS()

def SendPositionProptery(DeviceID,GPSLongitude,GPSLatitude):
	#this function sends all mobile parameters to the cumulocity platform
	if(m_modemmanager.GetDCD()==0):
		PrintW('DCD is low')
		PrintW('Failed to send GPS position. No connection')
		return
	PostData = '{"c8y_Position": {"alt":0,"lng":'+GPSLongitude+',"lat":'+GPSLatitude+'}}'
	FullPostString = 'PUT /inventory/managedObjects/'+DeviceID+' HTTP/1.1\r\n'
	FullPostString = FullPostString + 'Host: '+CumulocityServer+'\r\n'
	FullPostString = FullPostString + 'Authorization: Basic '+Device_B64_Authentication+'\r\n'
	FullPostString = FullPostString + 'Content-Type: application/vnd.com.nsn.cumulocity.managedObject+json\r\n'
	FullPostString = FullPostString + 'Accept: application/vnd.com.nsn.cumulocity.managedObject+json\r\n'
	FullPostString = FullPostString + 'Cache-Control: no-cache\r\n'
	FullPostString = FullPostString + 'Connection: keep-alive\r\n'
	FullPostString = FullPostString + 'Content-Length: '+str(len(PostData))+'\r\n'
	FullPostString = FullPostString + '\r\n'
	FullPostString = FullPostString + PostData
	m_modemmanager.SendData(FullPostString)
	PrintW('Sending collected data to Data Server\r\n')
	PrintW('Post contents:\r\n'+FullPostString+'\r\n')
	time.sleep(0.2)
	
def SendPositionEvent(DeviceID,DateTimeStr,GPSLongitude,GPSLatitude):
	LocationC8YStr = '{"source": { "id": "'+DeviceID+'" },'
	LocationC8YStr = LocationC8YStr + '"text": "c8y_LocationUpdate",'
	LocationC8YStr = LocationC8YStr + '"time": "'+DateTimeStr
	LocationC8YStr = LocationC8YStr + '","type": "c8y_LocationUpdate",'
	LocationC8YStr = LocationC8YStr + '"c8y_Position": {"alt":0,"lng":'
	LocationC8YStr = LocationC8YStr + GPSLongitude
	LocationC8YStr = LocationC8YStr + ',"lat":'
	LocationC8YStr = LocationC8YStr + GPSLatitude
	LocationC8YStr = LocationC8YStr + '}'
	
	LocationC8YStr = LocationC8YStr + '}'
	PrintW('Sending Position to server now\r\n')
	FullPostString = 'POST /event/events HTTP/1.1\r\n'
	FullPostString = FullPostString + 'Host: '+CumulocityServer+'\r\n'
	FullPostString = FullPostString + 'Authorization: Basic ' + Device_B64_Authentication
	FullPostString = FullPostString + 'Content-Type: application/vnd.com.nsn.cumulocity.event+json\r\n'
	FullPostString = FullPostString + 'Cache-Control: no-cache\r\n'
	FullPostString = FullPostString + 'Connection: Close\r\n'
	FullPostString = FullPostString + 'Content-Length: '+str(len(LocationC8YStr))+'\r\n'
	FullPostString = FullPostString + '\r\n' 
	FullPostString = FullPostString + LocationC8YStr
	if(m_modemmanager.GetDCD()==0):
		PrintW('DCD is low')
		PrintW('Failed to send GPS position. No connection')
		return
	m_modemmanager.SendData(FullPostString)
	PrintW('Sending GPS postion to Server\r\n')
	PrintW('Post contents:\r\n'+FullPostString+'\r\n')
	time.sleep(0.2)
def PrintW(arg):
	#prints debug messages over the USB interface
	SER.send(arg+'\r\n')

def ConvertLongitude(GPSLongitude):
	#convert Longitude to from degrees 
	GPSLongtiudeH2 = GPSLongitude[3:]
	DeciLoc = len(GPSLongtiudeH2) - GPSLongtiudeH2.find('.')
	GPSLongtiudeH2 = GPSLongtiudeH2.replace('.','')
	GPSLongitudeH2Int = int(GPSLongtiudeH2)/60
	GPSLongitudeH2 = str(GPSLongitudeH2Int)
	if(DeciLoc>len(GPSLongitudeH2)):
		GPSLongitudeH1 = "0."
		DeciLoc = DeciLoc - 1
		while(DeciLoc>len(GPSLongitudeH2)):
			DeciLoc = DeciLoc - 1
			GPSLongitudeH1 = GPSLongitudeH1 + "0"
		GPSLongitudeH1 = GPSLongitudeH1 + GPSLongitudeH2
	else:
		GPSLongitudeH1 = GPSLongitudeH2[0:len(GPSLongitudeH2)-DeciLoc]
	GPSLongitude = GPSLongitude[0:3] + GPSLongitudeH1[1:]
	return GPSLongitude
def ConvertLatitude(GPSLatitude):
	GPSLatitudeH2 = GPSLatitude[2:]
	DeciLoc = len(GPSLatitudeH2) - GPSLatitudeH2.find('.')
	GPSLatitudeH2 = GPSLatitudeH2.replace('.','')
	GPSLatitudeH2Int = int(GPSLatitudeH2)/60
	GPSLatitudeH2 = str(GPSLatitudeH2Int)
	if(DeciLoc>len(GPSLatitudeH2)):
		GPSLatitudeH1 = "0."
		DeciLoc = DeciLoc - 1
		while(DeciLoc>len(GPSLatitudeH2)):
			DeciLoc = DeciLoc - 1
			GPSLatitudeH1 = GPSLatitudeH1 + "0"
		GPSLatitudeH1 = GPSLatitudeH1 + GPSLatitudeH2
	else:
		GPSLatitudeH1 = GPSLatitudeH2[0:len(GPSLatitudeH2)-DeciLoc]
	GPSLatitude = GPSLatitude[0:2] + GPSLatitudeH1[1:]
	return GPSLatitude

def AdjustDate(OldDateTime):
	OldDateTime  =OldDateTime.replace('.','-')
	OldDateTime  =OldDateTime.replace(' ','T')
	OldDateTime  =OldDateTime + '+00:00'
	return OldDateTime

SER.set_speed('115200','8N1')
PrintW('script is executing...')

#initialize GPS
m_gpsmanager.initGPS()
#initialize modem
m_modemmanager.InitSMSSettings() #call once at the beginning of the script
PrintW('APN is: '+MOD_APN)
m_modemmanager.SetAPN(MOD_APN)
PrintW(m_modemmanager.ExecuteATCommand('AT#SCFG=1,1,300,90,600,50\r',5))

while(1):
	PrintW('Send aaa to exit the script')
	time.sleep(1)
	aa = SER.read()
	if(aa.find('aa')!=-1):
		sys.exit()
	m_gpsmanager.FlushGPSBuffer()
	m_gpsmanager.UpdateGPSParameters()
	if(m_gpsmanager.GPSHasFix()==1):
		PrintW('GPS has a fix')
		GPSLong = ConvertLongitude(m_gpsmanager.GetLongtitude())
		PrintW('GPS Long:'+GPSLong)
		GPSLat = ConvertLatitude(m_gpsmanager.GetLatitude())
		PrintW('GPS Lat:'+GPSLat)
		LastDateTime = m_gpsmanager.GetDateTime()
		PrintW('Old Date Time: '+LastDateTime )
		m_modemmanager.ActivateContext(MOD_USERNAME,MOD_PASSWORD)
		if(m_modemmanager.ConnectToServer('rs2.cumulocity.com',80)==1):
			PrintW('Sending Position update to Cumulocity')
			LastDateTime = AdjustDate(LastDateTime)
			PrintW('new Date Time:'+LastDateTime)
			
			SendPositionProptery(Cumulocity_Device_ID,GPSLong,GPSLat)
			SendPositionEvent(Cumulocity_Device_ID,LastDateTime,GPSLong,GPSLat)
		else:
			PrintW('Connection was not successful')
		time.sleep(60)
	else:
		PrintW('Waiting for GPS fix')
	time.sleep(10)