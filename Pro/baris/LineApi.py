# -*- coding: utf-8 -*-
from .Api import Poll, Talk, channel, call
from akad.ttypes import *
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from wikiapi import WikiApi
import time,random,sys,codecs,urllib,urllib3,base64,requests,threading,glob,os,subprocess,multiprocessing,re,ast,shutil,calendar,tempfile,string,six,timeago
import json, ntpath,unicodedata
def def_callback(str):
    print(str)

class LINE:

    mid = None
    authToken = None
    cert = None
    channel_access_token = None
    token = None
    _messageReq = {}
    obs_token = None
    refresh_token = None
    _session        = requests.session()
    Headers         = {}

    def __init__(self):
        self.Talk = Talk()
        self.Headers = {}
        self._session = requests.session()

    def login(self, mail=None, passwd=None, cert=None, token=None, qr=False, callback=None, www=False):
        if callback is None:
          callback = def_callback
        resp = self.__validate(mail,passwd,cert,token,qr,www)
        if resp == 1:
          self.Talk.login(mail, passwd, callback=callback)
        elif resp == 2:
          self.Talk.login(mail,passwd,cert, callback=callback)
        elif resp == 3:
          self.Talk.TokenLogin(token)
        elif resp == 4:
          self.Talk.qrLogin()
        elif resp == 5:
          self.Talk.qrLogin2(callback)
        else:
          raise Exception("invalid arguments")

        self.authToken = self.Talk.authToken
        self.cert = self.Talk.cert
        self.headers = self.Talk.headers
        self.Poll = Poll(self.authToken)
        self.mid = self.Talk.client.getProfile().mid
        self.channel = channel.Channel(self.authToken,self.mid)
        self.channel.login()

        self.channel_access_token = self.channel.channel_access_token
        self.token = self.channel.token
        self.obs_token = self.channel.obs_token
        self.refresh_token = self.channel.refresh_token

        self.call = call.Call(self.authToken)


#  """User"""

    def getProfile(self):
        return self.Talk.client.getProfile()

    def getSettings(self):
        return self.Talk.client.getSettings()

    def getUserTicket(self):
        return self.Talk.client.getUserTicket()
  
    def reissueUserTicket(self, expirationTime, maxUseCount):
        return self.Talk.client.reissueUserTicket(expirationTime, maxUseCount)

    def updateProfile(self, profileObject):
        return self.Talk.client.updateProfile(0, profileObject)

    def updateSettings(self, settingObject):
        return self.Talk.client.updateSettings(0, settingObject)


#  """Announcements"""
    def getChatRoomAnnouncementsBulk(self, chatRoomMids):
      return self.Talk.client.getChatRoomAnnouncementsBulk(chatRoomMids)

    def getChatRoomAnnouncements(self, chatRoomMids):
      return self.Talk.client.getChatRoomAnnouncements(chatRoomMids)

    def createChatRoomAnnouncement(self, chatRoomMid, _type, contents):
      return self.Talk.client.createChatRoomAnnouncement(0, chatRoomMid, _type, contents)

    def removeChatRoomAnnouncement(self, chatRoomMid, announcementSeq):
      return self.Talk.client.createChatRoomAnnouncement(0, chatRoomMid, announcementSeq)
  
    def getLastAnnouncementIndex(self):
      return self.Talk.client.getLastAnnouncementIndex()

 # """Operation"""

    def fetchOperation(self, revision, count):
        return self.Poll.client.fetchOperations(revision, count)

    def fetchOps(self, rev, count):
        return self.Poll.client.fetchOps(rev, count, 0, 0)

    def getLastOpRevision(self):
        return self.Talk.client.getLastOpRevision()

    def stream(self):
        return self.Poll.stream()


#  """CONTENT"""

    def post_content(self, url, data=None,files=None):
        return self._session.post(url,headers=self.headers,data=data,files=files)

    def get_content(self, url, headers=None):
        return self._session.get(url,headers=self.headers,stream=True)

    def downloadCOntent(self,url):
      path = '%s/Line-%i.data' % (tempfile.gettempdir(),random.randint(0,9))

      r = self.get_content(url)
      if r.status_code == 200:
          with open(path,'w') as f:
              shutil.copyfileobj(r.raw,f)    
          return path
      else:
          raise Exception('Download image failure.')

#  """Message"""

    def downloadObjMsg(self,messageId):
      path = '%s/Line-%i.data' % (tempfile.gettempdir(),random.randint(0,9))
      url = "https://obs-sg.line-apps.com/talk/m/download.nhn?oid="+messageId
      r = self.get_content(url)
      if r.status_code == 200:
        with open(path,'w') as f:
           shutil.copyfileobj(r.raw,f)
        return path
      else:
        raise Exception('Download object failure.')
    def downloadObjectMsg(self, messageId, returnAs='path', saveAs=''):
        if saveAs == '':
            saveAs = self.genTempFile('path')
        if returnAs not in ['path','bool','bin']:
            raise Exception('Invalid returnAs value')
        url = "https://obs-sg.line-apps.com/talk/m/download.nhn?oid="+messageId
        r = self.get_content(url)
        if r.status_code == 200:
            self.saveFile(saveAs, r.raw)
            if returnAs == 'path':
                return saveAs
            elif returnAs == 'bool':
                return True
            elif returnAs == 'bin':
                return r.raw
        else:
            raise Exception('Download object failure.')
    def updateProfileAttribute(self, attrId, value):
        return self.Talk.updateProfileAttribute(0, attrId, value)
    def sendtag(self,to, text="", mids=[]):
      arrData = ""
      arr = []
      mention = "@mbahdon "
      if mids == []:
          raise Exception("Invalid mids")
      if "~" in text:
        if text.count("~") != len(mids):
            raise Exception("Invalid mids")
        texts = text.split("~")
        textx = ""
        for mid in mids:
            textx += str(texts[mids.index(mid)])
            slen = len(textx)
            elen = len(textx) + 15
            arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mid}
            arr.append(arrData)
            textx += mention
        textx += str(texts[len(mids)])
      else:
        textx = ""
        slen = len(textx)
        elen = len(textx) + 15
        arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mids[0]}
        arr.append(arrData)
        textx += mention + str(text)
      return self.sendMessage(to, textx, {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
    def cloneContactProfile(self, mid):
      contact = self.getContact(mid)
      profile = self.getProfile()
      profile.displayName = contact.displayName
      profile.statusMessage = contact.statusMessage
      profile.pictureStatus = contact.pictureStatus
      self.updateProfilePicture(profile.pictureStatus)
      return self.updateProfile(profile)
    def saveFile(self, path, raw):
        with open(path, 'wb') as f:
            shutil.copyfileobj(raw, f)

    def deleteFile(self, path):
        if os.path.exists(path):
            os.remove(path)
            return True
        else:
            return False

    def downloadFileURL(self, fileUrl, returnAs='path', saveAs='', headers=None):
        if returnAs not in ['path','bool','bin']:
            raise Exception('Invalid returnAs value')
        if saveAs == '':
            saveAs = self.genTempFile()
        r = self.get_content(fileUrl, headers=headers)
        if r.status_code != 404:
            self.saveFile(saveAs, r.raw)
            if returnAs == 'path':
                return saveAs
            elif returnAs == 'bool':
                return True
            elif returnAs == 'bin':
                return r.raw
        else:
            raise Exception('Download file failure.')
    def sendAudionew(self, to, path):
        objectId = self.sendMessage(to=to, text=None, contentType = 3).id
        return self.uploadObjTalk(path=path, type='audio', returnAs='bool', objId=objectId)
    def additionalHeaders(self, source, newSource):
        headerList={}
        headerList.update(source)
        headerList.update(newSource)
        return headerList
    def uploadObjTalk(self, path, type='image', returnAs='bool', objId=None, to=None):
        if returnAs not in ['objId','bool']:
            raise Exception('Invalid returnAs value')
        if type not in ['image','gif','video','audio','file']:
            raise Exception('Invalid type value')
        headers=None
        files = {'file': open(path, 'rb')}
        if type == 'image' or type == 'video' or type == 'audio' or type == 'file':
            e_p = 'https://obs-sg.line-apps.com/talk/m/upload.nhn'
            data = {'params': self.genOBSParams({'oid': objId,'size': len(open(path, 'rb').read()),'type': type})}
        elif type == 'gif':
            e_p = 'https://obs-sg.line-apps.com/r/talk/m/reqseq'
            files = None
            data = open(path, 'rb').read()
            params = {
                'oid': 'reqseq',
                'reqseq': '%s' % str(self.revision),
                'tomid': '%s' % str(to),
                'size': '%s' % str(len(data)),
                'range': len(data),
                'type': 'image'
            }
            headers = self.additionalHeaders(self.Talk.headers, {
                'Content-Type': 'image/gif',
                'Content-Length': str(len(data)),
                'x-obs-params': self.genOBSParams(params,'b64')
            })
        r = self.post_content(e_p, data=data, headers=headers, files=files)
        if r.status_code != 201:
            raise Exception('Upload %s failure.' % type)
        if returnAs == 'objId':
            return objId
        elif returnAs == 'bool':
            return True
    def sendAudio(self, to_, path):
        M = Message(to=to_, text=None, contentType = 3)
        M.contentMetadata = None
        M.contentPreview = None
        M2 = self.Talk.client.sendMessage(0,M)
        M_id = M2.id
        files = {
            'file': open(path, 'rb'),
        }
        params = {
            'name': 'media',
            'oid': M_id,
            'size': len(open(path, 'rb').read()),
            'type': 'audio',
            'ver': '1.0',
        }
        data = {
            'params': json.dumps(params)
        }
        r = self.post_content('https://os.line.naver.jp/talk/m/upload.nhn', data=data, files=files)
        if r.status_code != 201:
            raise Exception('Upload image failure.')
        #r.content
        return True
    def sendAudioWithURL(self, to_, url):
      path = '%s/pythonLine-%i.data' % (tempfile.gettempdir(),random.randint(0,9))
      r = requests.get(url, stream=True)
      if r.status_code == 200:
          with open(path,'wb') as f:
              shutil.copyfileobj(r.raw,f)
      else:
          raise Exception('Download audio failure.')
      try:
          self.sendAudio(to_,path)
      except Exception as e:
          raise e
    def sendVideo(self, to_, path):
        M = Message(to=to_, text=None, contentType = 2)
        M.contentMetadata = None
        M.contentPreview = None
        M2 = self.Talk.client.sendMessage(0,M)
        M_id = M2.id
        files = {
            'file': open(path, 'rb'),
        }
        params = {
            'name': 'media',
            'oid': M_id,
            'size': len(open(path, 'rb').read()),
            'type': 'video',
            'ver': '1.0',
        }
        data = {
            'params': json.dumps(params)
        }
        r = self.post_content('https://os.line.naver.jp/talk/m/upload.nhn', data=data, files=files)
        if r.status_code != 201:
            raise Exception('Upload image failure.')
        return True

    def changePG(self, to_, id_):
      path = '%s/pythonLine-%i.data' % (tempfile.gettempdir(),random.randint(0,9))
      url = 'https://obs.line-apps.com/talk/m/download.nhn?oid=' + id_
      r = requests.get(url, stream=True, headers = self.Talk.headers)
      if r.status_code == 200:
          with open(path,'wb') as f:
              shutil.copyfileobj(r.raw,f)
      else:        
          raise Exception('Download image failure.')          
      with open(path,'rb') as f:
          data = f.read()   
      purl = 'https://obs.line-apps.com/os/g/' + to_
      r = requests.post(purl, headers = self.Talk.headers, data=data)
      if r.status_code != 201:
          r = requests.post(purl, headers = self.Talk.headers, data=data)          
          raise Exception('Upload image failure.')         
      try:
          self.sendText(to_,"Success!")
      except Exception as e:
          raise e
    def changePP(self, to_, id_,from_):
      path = '%s/pythonLine-%i.data' % (tempfile.gettempdir(),random.randint(0,9))
      url = 'https://obs.line-apps.com/talk/m/download.nhn?oid=' + id_
      r = requests.get(url, stream=True, headers = self.Talk.headers)
      if r.status_code == 200:
          with open(path,'wb') as f:
              shutil.copyfileobj(r.raw,f)
      else:       
          raise Exception('Download image failure.')          
      with open(path,'rb') as f:
          data = f.read()         
      purl = 'https://obs.line-apps.com/os/p/' + from_
      r = requests.post(purl, headers = self.Talk.headers, data=data)
      if r.status_code != 201:
          r = requests.post(purl, headers = self.Talk.headers, data=data)         
          raise Exception('Upload image failure.')       
      try:
          self.sendText(to_,"Success!")
      except Exception as e:
          raise e
    def getHomeProfile(self, mid=None, postLimit=10, commentLimit=1, likeLimit=1):
        if mid is None:
            mid = self.client.getProfile().mid
        params = {'homeId': mid, 'postLimit': postLimit, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'sourceType': 'LINE_PROFILE_COVER'}
        url = self.urlEncode('https://t.line.naver.jp/mh/api', '/v27/post/list', params)
        r = self.get_content(url, headers=self.server.channelHeaders)
        return r.json()
    def urlEncode(self, url, path, params=[]):
        try:        # Works with python 2.x
            return url + path + '?' + urllib.urlencode(params)
        except:     # Works with python 3.x
            return url + path + '?' + urllib.parse.urlencode(params)

    def updateProfilePicture(self, path, type='p'):
        files = {'file': open(path, 'rb')}
        params = {'oid': self.getProfile().mid,'type': 'image'}
        if type == 'vp':
            params.update({'ver': '2.0', 'cat': 'vp.mp4'})
        data = {'params': self.genOBSParams(params)}
        r = self.post_content('https://obs-sg.line-apps.com/talk/p/upload.nhn', data=data, files=files)
        if r.status_code != 201:
            raise Exception('Update profile picture failure.')
        return True

    def genTempFile(self, returnAs='path'):
        try:
            if returnAs not in ['file','path']:
                raise Exception('Invalid returnAs value')
            fName, fPath = 'line-%s-%i.bin' % (int(time.time()), random.randint(0, 9)), tempfile.gettempdir()
            if returnAs == 'file':
                return fName
            elif returnAs == 'path':
                return os.path.join(fPath, fName)
        except Exception as e:
            print(e) #raise Exception('tempfile is required')

    def genOBSParams(self, newList, returnAs='json'):
        oldList = {'name': self.genTempFile('file'),'ver': '1.0'}
        if returnAs not in ['json','b64','default']:
            raise Exception('Invalid parameter returnAs')
        oldList.update(newList)
        if 'range' in oldList:
            new_range='bytes 0-%s\/%s' % ( str(oldList['range']-1), str(oldList['range']) )
            oldList.update({'range': new_range})
        if returnAs == 'json':
            oldList=json.dumps(oldList)
            return oldList
        elif returnAs == 'b64':
            oldList=json.dumps(oldList)
            return base64.b64encode(oldList.encode('utf-8'))
        elif returnAs == 'default':
            return oldList
    def unsendMessage(self, messageId):
        return self.Talk.client.unsendMessage(0,messageId)
    def sendMessage(self, to, text, contentMetadata={}, contentType=0):
        msg = Message()
        msg.to, msg._from = to, self.getProfile().mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.Talk.client.sendMessage(self._messageReq[to], msg)
    def sendMessage2(self, messageObject):
        return self.Talk.client.sendMessage(0,messageObject)
    def sendSticker(self, Tomid, packageId, stickerId):
        msg = Message()
        msg.contentMetadata = {
            'STKVER': '100',
            'STKPKGID': packageId,
            'STKID': stickerId
        }
        msg.contentType = 7
        msg.to = Tomid
        msg.text = ''
        return self.Talk.client.sendMessage(0, msg)

    def sendContact(self, Tomid, mid):
        msg = Message()
        msg.contentMetadata = {'mid': mid}
        msg.to = Tomid
        msg.text = ''
        msg.contentType = 13
        return self.Talk.client.sendMessage(0, msg)

    def sendText(self, Tomid, text):
        msg = Message()
        msg.to = Tomid
        msg.text = text

        return self.Talk.client.sendMessage(0, msg)

    def sendImage(self, to_, path):
        M = Message(to=to_, text=None, contentType = 1)
        M.contentMetadata = None
        M.contentPreview = None
        M2 = self.Talk.client.sendMessage(0,M)
        M_id = M2.id
        files = {
            'file': open(path, 'rb'),
        }
        params = {
            'name': 'media',
            'oid': M_id,
            'size': len(open(path, 'rb').read()),
            'type': 'image',
            'ver': '1.0',
        }
        data = {
            'params': json.dumps(params)
        }
        r = self.post_content('https://obs-sg.line-apps.com/talk/m/upload.nhn', data=data, files=files)
        if r.status_code != 201:
            raise Exception('Upload image failure.')
        #r.content
        return True

    def sendImageWithURL(self, to, url):
        path = self.downloadFileURL(url, 'path')
        self.sendImage(to, path)
        self.deleteFile(path)


    def sendVideoWithURL(self, to_, url):
      path = self.downloadCOntent(url)
      try:
          self.sendVideo(to_,path)
      except Exception as e:
          raise e

    def sendEvent(self, messageObject):
        return self._client.sendEvent(0, messageObject)

    def sendChatChecked(self, mid, lastMessageId):
        return self.Talk.client.sendChatChecked(0, mid, lastMessageId)

    def getMessageBoxCompactWrapUp(self, mid):
        return self.Talk.client.getMessageBoxCompactWrapUp(mid)

    def getMessageBoxCompactWrapUpList(self, start, messageBox):
        return self.Talk.client.getMessageBoxCompactWrapUpList(start, messageBox)

    def getRecentMessages(self, messageBox, count):
        return self.Talk.client.getRecentMessages(messageBox.id, count)

    def getMessageBox(self, channelId, messageboxId, lastMessagesCount):
        return self.Talk.client.getMessageBox(channelId, messageboxId, lastMessagesCount)

    def getMessageBoxList(self, channelId, lastMessagesCount):
        return self.Talk.client.getMessageBoxList(channelId, lastMessagesCount)

    def getMessageBoxListByStatus(self, channelId, lastMessagesCount, status):
        return self.Talk.client.getMessageBoxListByStatus(channelId, lastMessagesCount, status)

    def getMessageBoxWrapUp(self, mid):
        return self.Talk.client.getMessageBoxWrapUp(mid)

    def getMessageBoxWrapUpList(self, start, messageBoxCount):
        return self.Talk.client.getMessageBoxWrapUpList(start, messageBoxCount)

#  """Contact"""


    def blockContact(self, mid):
        return self.Talk.client.blockContact(0, mid)


    def unblockContact(self, mid):
        return self.Talk.client.unblockContact(0, mid)


    def findAndAddContactsByMid(self, mid):
        return self.Talk.client.findAndAddContactsByMid(0, mid)


    def findAndAddContactsByMids(self, midlist):
        for i in midlist:
            self.Talk.client.findAndAddContactsByMid(0, i)

    def findAndAddContactsByUserid(self, userid):
        return self.Talk.client.findAndAddContactsByUserid(0, userid)

    def findContactsByUserid(self, userid):
        return self.Talk.client.findContactByUserid(userid)

    def findContactByTicket(self, ticketId):
        return self.Talk.client.findContactByUserTicket(ticketId)

    def getAllContactIds(self):
        return self.Talk.client.getAllContactIds()

    def getBlockedContactIds(self):
        return self.Talk.client.getBlockedContactIds()

    def getContact(self, mid):
        return self.Talk.client.getContact(mid)

    def getContacts(self, midlist):
        return self.Talk.client.getContacts(midlist)

    def getFavoriteMids(self):
        return self.Talk.client.getFavoriteMids()

    def getHiddenContactMids(self):
        return self.Talk.client.getHiddenContactMids()


#  """Group"""

    def acceptGroupInvitation(self, groupId):
        return self.Talk.client.acceptGroupInvitation(0, groupId)

    def acceptGroupInvitationByTicket(self, groupId, ticketId):
        return self.Talk.client.acceptGroupInvitationByTicket(0, groupId, ticketId)

    def cancelGroupInvitation(self, groupId, contactIds):
        return self.Talk.client.cancelGroupInvitation(0, groupId, contactIds)

    def createGroup(self, name, midlist):
        return self.Talk.client.createGroup(0, name, midlist)

    def getGroupWithoutMembers(self, groupId):
        return self.Talk.client.getGroupWithoutMembers(groupId)

    def getGroup(self, groupId):
        return self.Talk.client.getGroup(groupId)

    def getGroups(self, groupIds):
        return self.Talk.client.getGroups(groupIds)
 
    def getGroupsV2(self, groupIds):
        return self.Talk.client.getGroupsV2(groupIds)

    def getGroupIdsInvited(self):
        return self.Talk.client.getGroupIdsInvited()

    def getGroupIdsJoined(self):
        return self.Talk.client.getGroupIdsJoined()

    def inviteIntoGroup(self, groupId, midlist):
        return self.Talk.client.inviteIntoGroup(0, groupId, midlist)

    def kickoutFromGroup(self, groupId, midlist):
        return self.Talk.client.kickoutFromGroup(0, groupId, midlist)

    def leaveGroup(self, groupId):
        return self.Talk.client.leaveGroup(0, groupId)

    def rejectGroupInvitation(self, groupId):
        return self.Talk.client.rejectGroupInvitation(0, groupId)

    def reissueGroupTicket(self, groupId):
        return self.Talk.client.reissueGroupTicket(groupId)

    def updateGroup(self, groupObject):
        return self.Talk.client.updateGroup(0, groupObject)
    def findGroupByTicket(self,ticketId):
        return self.Talk.client.findGroupByTicket(ticketId)

#  """Room"""

    def createRoom(self, midlist):
        return self.Talk.client.createRoom(0, midlist)

    def getRoom(self, roomId):
        return self.Talk.client.getRoom(roomId)

    def inviteIntoRoom(self, roomId, midlist):
        return self.Talk.client.inviteIntoRoom(0, roomId, midlist)

    def leaveRoom(self, roomId):
        return self.Talk.client.leaveRoom(0, roomId)

#  """TIMELINE"""

    def new_post(self, text):
        return self.channel.new_post(text)

    def like(self, mid, postid, likeType=1001):
        return self.channel.like(mid, postid, likeType)

    def comment(self, mid, postid, text):
        return self.channel.comment(mid, postid, text)

    def activity(self, limit=20):
        return self.channel.activity(limit)

    def getAlbum(self, gid):

      return self.channel.getAlbum(gid)
    def changeAlbumName(self, gid, name, albumId):
      return self.channel.changeAlbumName(gid, name, albumId)

    def deleteAlbum(self, gid, albumId):
      return self.channel.deleteAlbum(gid,albumId)

    def getNote(self,gid, commentLimit, likeLimit):
      return self.channel.getNote(gid, commentLimit, likeLimit)

    def getDetail(self,mid):
      return self.channel.getDetail(mid)

    def getHome(self,mid):
      return self.channel.getHome(mid)

    def createAlbum(self, gid, name):
      return self.channel.createAlbum(gid,name)

    def createAlbum2(self, gid, name, path):
      return self.channel.createAlbum(gid, name, path, oid)

#  """Callservice"""

    def acquireCallRoute(self,to):
        return self.call.acquireCallRoute(to)

    def acquireGroupCallRoute(self, groupId, mediaType=GroupCallMediaType.AUDIO):
        return self.call.acquireGroupCallRoute(groupId, GroupCallMediaType)

    def getGroupCall(self, ChatMid):
        return self.call.getGroupCall(ChatMid)

    def inviteIntoGroupCall(self, chatId, contactIds=[], mediaType=GroupCallMediaType.AUDIO):
        return self.call.inviteIntoGroupCall(chatId, contactIds, GroupCallMediaType)

    def __validate(self, mail, passwd, cert, token, qr, www):
      if mail is not None and passwd is not None and cert is None:
        return 1
      elif mail is not None and passwd is not None and cert is not None:
        return 2
      elif token is not None:
        return 3
      elif qr is True:
        return 4
      elif www is True:
        return 6
      else:
        return 5

    def loginResult(self, callback=None):
      if callback is None:
        callback = def_callback

        prof = self.getProfile()
        print("MID : " + prof.mid)
        print("NAME : " + prof.displayName)
        print("AuthToken :  " + self.authToken)
        print("Channel Token :  " + self.channel_access_token)
