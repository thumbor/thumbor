from os.path import join

from tornado.testing import gen_test

from . import EngineCase
from .urls_helpers import MAX_DATASET_SIZE, UrlsTester, single_dataset


class PILTest(EngineCase):
    engine = "thumbor.engines.pil"

    @gen_test(timeout=MAX_DATASET_SIZE * 5)
    async def test_single_params(self):
        if not self._app:
            return True
        group = list(single_dataset())
        count = len(group)
        tester = UrlsTester(self.http_client)

        print("Requests count: %d" % count)
        for options in group:
            joined_parts = join(*options)
            url = "unsafe/%s" % joined_parts
            await tester.try_url(self.get_url(f"/{url}"))

        tester.report()

    # def test_combined_params__with_pil(self):
    #     if not self._app:
    #         return True
    #     combined_dataset(self.retrieve)
