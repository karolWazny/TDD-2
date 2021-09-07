class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def run(self, result):
        result.testStarted()
        try:
            self.setUp()
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed(self.name)
        self.tearDown()
        return result

    def tearDown(self):
        pass


class TestSuite:
    def __init__(self, testCaseClass=TestCase):
        self.tests = []
        testNames = dir(testCaseClass)
        for testName in testNames:
            if testName.startswith("test"):
                self.add(testCaseClass(testName))

    def add(self, test):
        self.tests.append(test)

    def run(self, result):
        for test in self.tests:
            test.run(result)
        return result


class TestResult:

    def __init__(self):
        self.runCount = 0
        self.errorCount = 0
        self.failedTestNames = []

    def testStarted(self):
        self.runCount = self.runCount + 1

    def testFailed(self, testName):
        self.errorCount += 1
        self.failedTestNames.append(testName)

    def failedTests(self):
        return self.failedTestNames

    def summary(self):
        return "%d run, %d failed" % (self.runCount, self.errorCount)


class WasRun(TestCase):
    def __init__(self, name):
        self.wasRun = None
        self.wasSetUp = None
        self.log = None
        TestCase.__init__(self, name)

    def testMethod(self):
        self.wasRun = 1
        self.log = self.log + "testMethod "

    def testBrokenMethod(self):
        raise Exception

    def setUp(self):
        self.wasSetUp = 1
        self.log = "setUp "

    def tearDown(self):
        self.log = self.log + "tearDown "


class SetUpProblems(WasRun):
    def setUp(self):
        WasRun.setUp(self)
        raise Exception


class TestCaseTest(TestCase):

    def setUp(self):
        self.result = TestResult()

    def testTemplateMethod(self):
        test = WasRun("testMethod")
        test.run(TestResult())
        assert ("setUp testMethod tearDown " == test.log)

    def testResult(self):
        test = WasRun("testMethod")
        test.run(self.result)
        assert ("1 run, 0 failed" == self.result.summary())

    def testFailedResultFormatting(self):
        self.result.testStarted()
        self.result.testFailed("testBrokenMethod")
        assert ("1 run, 1 failed" == self.result.summary())

    def testFailedResult(self):
        test = WasRun("testBrokenMethod")
        test.run(self.result)
        assert ("1 run, 1 failed" == self.result.summary())

    def testSetUpProblem(self):
        test = SetUpProblems("testMethod")
        test.run(self.result)
        assert ("1 run, 1 failed" == self.result.summary())

    def testSuite(self):
        suite = TestSuite(WasRun)
        suite.run(self.result)
        assert ("2 run, 1 failed" == self.result.summary())

    def testResultKnowsNamesOfFailedTests(self):
        suite = TestSuite(WasRun)
        suite.run(self.result)
        assert (["testBrokenMethod"] == self.result.failedTests())


if __name__ == '__main__':
    suite = TestSuite(testCaseClass=TestCaseTest)
    result = TestResult()
    suite.run(result)
    print(result.summary())
    if len(result.failedTests()) > 0:
        print("Failed tests:")
        print(result.failedTests())
