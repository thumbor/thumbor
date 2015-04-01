from thumbor.integration_tests import EngineCase


class PILTest(EngineCase):
    engine = 'thumbor.engines.pil'

    def test_single_params(self):
        self.exec_single_params()
