from Jumpscale import j
from base_test import BaseTest
import random, requests, uuid, unittest
from parameterized import parameterized


class TestStartupcmdServer(BaseTest):
    def setUp(self):
        pass

    @parameterized.expand(["background", "tmux", "foreground"])
    def test01_startupcmd_executor(self, executor):
        """
        - ​Get startupcmd server instance.
        - Define executer type.
        - Add process cmd_start.
        - Check that process running successfully in right executor.
        - Check that server connection  works successfully
        """
        self.info("Get startupcmd server instance.")
        startupcmd_server = j.servers.startupcmd.get()

        self.info("Define executer type.")
        startupcmd_server.executor = executor

        self.info("Add process cmd_start.")
        startupcmd_server.cmd_start = "python3 -m http.server"

        self.info("Check that process running successfully in right executor.")
        if executor == "foreground":
            self.skipTest("https://github.com/threefoldtech/jumpscaleX_core/issues/101")
            tmux_session_name = self.rand_string()
            output, error = self.os_command(
                "tmux  -d -s {} 'kosmos -p \"j.servers.startupcmd.get().start()\"'".format(tmux_session_name)
            )
            output, error = self.os_command("tmux ls")
            self.assertIn(tmux_session_name, output.decode())

        if executor == "background":
            startupcmd_server.start()

        if executor == "tmux":
            output, error = self.os_command("tmux ls")
            self.assertIn(startupcmd_server.name, output.decode())

        output, error = self.os_command(" ps -aux | grep -v grep | grep {} | awk '{print $2}'".format("http.server"))
        self.assertTrue(output.decode())

        self.info("Check that server connection  works successfully.")
        server_PID = output.decode()
        output, error = self.os_command("netstat -nltp | grep '{}' ".format(server_PID))
        self.assertTrue(output)

        self.info(" Stop server , check it stoped successfully.")
        startupcmd_server.stop()
        if executor == "tmux":
            output, error = self.os_command("tmux ls")
            self.assertIn(tmux_session_name, output.decode())
        output, error = self.os_command(" ps -aux | grep -v grep | grep {} ".format("http.server"))
        self.assertFalse(output.decode())
        startupcmd_server.delete()

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/101")
    def test02_startupcmd_executor_corex(self):
        """
        - ​Get startupcmd server instance.
        - Define executer type as corex.
        - Install, start corex server and get its client.
        - Pass process cleint to startcmd server.
        - Start startupcmd , check it works successfully in corex executor . 
        - Check that server connection  works successfully
        """
        self.info("Get startupcmd server instance.")
        startupcmd_server = j.servers.startupcmd.get()

        self.info("Define executer type as corex.")
        startupcmd_server.executor = "corex"

        self.info("Install, start corex server and get its client.")
        j.servers.corex.install()
        j.servers.corex.default.start()
        corex = j.servers.corex.default.client

        self.info("Pass process cleint to startcmd server.")
        startupcmd_server.executor = "corex"
        startupcmd_server.corex_client_name = corex.name
        startupcmd_server.cmd_start = "python3 -m http.server"

        self.info("Start startupcmd , check it works successfully in corex executor ")

        ## need to write step which make sure that it runs in corex when issue solved
        startupcmd_server.start()
        output, error = self.os_command(" ps -aux | grep -v grep | grep {} | awk '{print $2}'".format("http.server"))
        self.assertTrue(output.decode())

        self.info(" * Check that server connection  works successfully.")
        server_PID = output.decode()
        output, error = self.os_command("netstat -nltp | grep '{}' ".format(server_PID))
        self.assertTrue(output)

    @parameterized.expand(["JUMPSCALE", "PYTHON", "BASH"])
    @unittest.skip("https://github.com/threefoldtech/jumpscaleX_core/issues/101")
    def test03_startupcmd_interpreter(self, interpreter):
        """
        - ​Get startupcmd server instance.
        - Define interpreter type.
        - Add command in cmd_start .
        - Start startupcmd , check it works successfully . 
        """
        self.info("​Get startupcmd server instance")
        startupcmd_server = j.servers.startupcmd.get()
        self.info("Define interpreter type.")
        startupcmd_server.interpreter = interpreter

        self.info("Add {} command in cmd_start.".format(interpreter))
        file_name = self.rand_string()
        if interpreter == "JUMPSCALE":
            startupcmd_server.cmd_start = "j.sal.fs.createEmptyFile('/root/{}')".format(file_name)
        elif interpreter == "PYTHON":
            startupcmd_server.cmd_start = "open('/root/{}','w+')".format(file_name)

        elif interpreter == "BASH":
            startupcmd_server.cmd_start = "touch /root/{}".format(file_name)

        self.info("Start startupcmd , check it works successfully .")
        startupcmd_server.start()
        output, error = self.os_command("ls /root")
        self.assertIn(file_name, output.decode())

        startupcmd_server.stop()
        startupcmd_server.delete()

    def test04_startupcmd_jumpscale_gevent_interpreter(self):
        """
        - ​Get startupcmd server instance.
        - Define interpreter type as JUMPSCALE_GEVENT.
        - Use rack server as cmd start.
        - Start startupcmd ,should start rack server successfully.
        """
        self.info("​Get startupcmd server instance")
        startupcmd_server = j.servers.startupcmd.get()
        self.info("Define interpreter type.")
        startupcmd_server.interpreter = "JUMPSCALE_GEVENT"

        self.info("Use rack server as cmd start.")
        port = random.randint(100, 999)
        cmd_start = "j.servers.rack.get().bottle_server_add(port={})&j.servers.rack.get().start()".format(port)
        startupcmd_server.cmd_start = cmd_start

        self.info("Start startupcmd ,should start rack server successfully.")
        startupcmd_server.start()
        output, error = self.os_command("netstat -nltp | grep {}".format(port))
        self.assertTrue(output.decode())
        startupcmd_server.stop()
        output, error = self.os_command("netstat -nltp | grep {}".format(port))
        self.assertFalse(output.decode())
        startupcmd_server.delete()