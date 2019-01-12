import os, sys, time
path = os.path.join(os.path.dirname(__file__), '../lib/')
sys.path.insert(0, path)
from src.transport import TTransport,TSocket,THttpClient,TTransport,TZlibTransport
from src.protocol import TCompactProtocol,TMultiplexedProtocol,TProtocol
from src.server import THttpServer,TServer,TProcessPoolServer
from curve import LineService
from curve.ttypes import *
class Poll:
  client = None
  auth_query_path = "/api/v4/TalkService.do";
  http_query_path = "/S4";
  polling_path = "/P4";
  host = "gd2.line.naver.jp";
  port = 443;
  UA = "Line/1.4.17"
  LA = "CHROMEOS\t1.4.17\tChrome_OS\t1"
  rev = 0
  def __init__(self, authToken):
    self.transport = THttpClient.THttpClient('https://gd2.line.naver.jp:443'+ self.http_query_path)
    self.transport.setCustomHeaders({
      "User-Agent" : self.UA,
      "X-Line-Application" : self.LA,
      "X-Line-Access": authToken
    });
    self.protocol = TCompactProtocol.TCompactProtocol(self.transport);
    self.client = LineService.Client(self.protocol)
    self.rev = self.client.getLastOpRevision()
    self.transport.path = self.polling_path
    self.transport.open()
  def stream(self, sleep=50000):
    while True:
      try:
        Ops = self.client.fetchOperation(self.rev, 5)
      except EOFError:
        raise Exception("It might be wrong revision\n" + str(self.rev))
      for Op in Ops:
        if (Op.type != OpType.END_OF_OPERATION):
          self.rev = max(self.rev, Op.revision)
          return Op
