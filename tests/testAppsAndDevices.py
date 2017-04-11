import json

from tests.util.servertestcase import ServerTestCase
from server import flaskserver as server


class TestAppsAndDevices(ServerTestCase):
    def setUp(self):
        self.name = "testDevice"

        self.username = "testUsername"
        self.password = "testPassword"
        self.ip = "127.0.0.1"
        self.port = 6000

        self.extraFields = {"extraFieldOne": "extraNameOne", "extraFieldTwo": "extraNameTwo"}

    def tearDown(self):
        with server.running_context.flask_app.app_context():
            server.running_context.Device.query.filter_by(name=self.name).delete()
            server.running_context.Device.query.filter_by(name="testDeviceTwo").delete()
            server.database.db.session.commit()

    def test_add_device(self):
        data = {"name": self.name, "username": self.username, "pw": self.password, "ipaddr": self.ip, "port": self.port,
                "extraFields": json.dumps(self.extraFields)}
        self.post_with_status_check('/configuration/HelloWorld/devices/add', 'device successfully added',
                                    data=data, headers=self.headers)
        self.post_with_status_check('/configuration/HelloWorld/devices/add', 'device could not be added',
                                    data=data, headers=self.headers)

    def test_display_device(self):
        data = {"name": self.name, "username": self.username, "pw": self.password, "ipaddr": self.ip, "port": self.port,
                "extraFields": str(self.extraFields)}
        json.loads(
            self.app.post('/configuration/HelloWorld/devices/add', data=data, headers=self.headers).get_data(
                as_text=True))

        response = json.loads(
            self.app.get('/configuration/HelloWorld/devices/testDevice/display', headers=self.headers).get_data(
                as_text=True))
        self.assertEqual(response["username"], self.username)
        self.assertEqual(response["name"], self.name)
        self.assertEqual(response["ip"], self.ip)
        self.assertEqual(response["port"], str(self.port))
        self.assertEqual(response["extraFieldOne"], "extraNameOne")
        self.assertEqual(response["extraFieldTwo"], "extraNameTwo")

    def test_edit_device(self):
        data = {"name": self.name, "username": self.username, "pw": self.password, "ipaddr": self.ip, "port": self.port,
                "extraFields": str(self.extraFields)}
        json.loads(
            self.app.post('/configuration/HelloWorld/devices/add', data=data, headers=self.headers).get_data(
                as_text=True))

        data = {"ipaddr": "192.168.196.1"}
        self.get_with_status_check('/configuration/HelloWorld/devices/testDevice/edit', 'device successfully edited',
                                   data=data, headers=self.headers)

        data = {"port": 6001}
        self.get_with_status_check('/configuration/HelloWorld/devices/testDevice/edit', 'device successfully edited',
                                   data=data, headers=self.headers)

        data = {"extraFields": json.dumps({"extraFieldOne": "extraNameOneOne"})}
        self.get_with_status_check('/configuration/HelloWorld/devices/testDevice/edit', 'device successfully edited',
                                   data=data, headers=self.headers)

        response = json.loads(
            self.app.get('/configuration/HelloWorld/devices/testDevice/display', headers=self.headers).get_data(
                as_text=True))
        self.assertEqual(response["extraFieldOne"], "extraNameOne")

    def test_add_and_display_multiple_devices(self):
        data = {"name": self.name, "username": self.username, "pw": self.password, "ipaddr": self.ip, "port": self.port,
                "extraFields": json.dumps(self.extraFields)}
        self.post_with_status_check('/configuration/HelloWorld/devices/add', 'device successfully added',
                                    data=data, headers=self.headers)

        data = {"name": "testDeviceTwo", "username": self.username, "pw": self.password, "ipaddr": self.ip,
                "port": self.port,
                "extraFields": json.dumps(self.extraFields)}
        self.post_with_status_check('/configuration/HelloWorld/devices/add', 'device successfully added',
                                    data=data, headers=self.headers)

        response = json.loads(
            self.app.post('/configuration/HelloWorld/devices/all', headers=self.headers).get_data(
                as_text=True))
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0]["name"], self.name)
        self.assertEqual(response[1]["name"], "testDeviceTwo")
        self.assertEqual(response[0]["app"]["name"], response[1]["app"]["name"])
