from datetime import datetime as dt


class JimServerMessage:
    def probe(self, sender, status="Are you there?"):
        deta = {
            "action": "probe",
            "time": dt.now().timestamp(),
            "type": "status",
            "user": {
                "account_name": sender,
                "status": status
            }
        }
        return deta

    def response(self, code=None, error=None):
        _data = {
            "action": "response",
            "code": code,
            "time": dt.now().timestamp(),
            "error": error
        }
        return _data
