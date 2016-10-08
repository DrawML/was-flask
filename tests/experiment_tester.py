import unittest
import requests


class ExperimentRunTestCase(unittest.TestCase):
    # Uncomment what you want
    #
    MODEL_PATH = 'input/linear_regression.xml'
    #MODEL_PATH = 'input/logistic_regression.xml'
    #MODEL_PATH = 'input/softmax.xml'
    #MODEL_PATH = 'input/neural_net.xml'
    #MODEL_PATH = 'input/convolution_net.xml'
    PROTOCOL = "http"
    HOSTNAME = "210.118.74.55:5000"
    url = PROTOCOL + "://" + HOSTNAME

    def test_experiment_run(self):
        tester = dict()
        tester['user_id'] = 'a'
        tester['pw'] = 'a'

        session = requests.Session()

        # try to register
        path = "/auth/register"
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        data = tester
        response = session.post(self.url + path, headers=headers, data=data)

        self.assertIn('Error: User id a is duplicated', response.text, "User is not duplicated")

        # try to sign in
        path = "/auth/signin"
        data = tester
        headers = {
            'Usier-Agent': 'Mozilla/5.0'
        }
        response = session.post(self.url + path, headers=headers, data=data)
        self.assertEqual(200, response.status_code, "Fail to sign in")

        # try to run
        path = "/experiments/1/run"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/xml'
        }
        with open(self.MODEL_PATH, 'r') as f:
            data = f.read()
        response = session.post(self.url + path, headers=headers, data=data)

        self.assertEqual(200, response.status_code, "Fail to request to run")
        self.assertEqual('run', response.text, "Fail to run")

        print("Successfully Run")


if __name__ == '__main__':
    unittest.main()
