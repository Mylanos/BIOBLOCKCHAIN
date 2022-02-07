import unittest
import test_wallet
import test_transaction


loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_wallet))
suite.addTests(loader.loadTestsFromModule(test_transaction))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)