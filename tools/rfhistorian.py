import os
import argparse
from robot.api import ExecutionResult, ResultVisitor
import datetime
from datetime import timedelta
import requests

# python parserargs.py --projectname test foo bar project --version 0.0.1

def parse_options():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    general = parser.add_argument_group("Parser")
    general.add_argument(
        '-s', '--host',
        dest='host',
        default='localhost:8000',
        help="RFHistorian host address"
    )
    general.add_argument(
        '-u', '--username',
        dest='username',
        default='admin',
        help="RFHistorian username"
    )
    general.add_argument(
        '-p', '--password',
        dest='password',
        default='passw0rd',
        help="RFHistorian user password"
    )
    general.add_argument(
        '-n', '--project',
        dest='projectname',
        help="Project name"
    )
    general.add_argument(
        '-e', '--version',
        dest='version',
        help="Version, e.g.: 1.0.0 or sha"
    )
    general.add_argument(
        '-i', '--inputdir',
        dest='dir',
        default=os.path.curdir,
        help="Result directory"
    )
    general.add_argument(
        '-o', '--output',
        dest='output',
        default="output.xml",
        help="Output file name"
    )
    args = parser.parse_args()
    return args

def rfhistoric_parser(opts):
    dir = os.path.abspath(os.path.expanduser(opts.dir))
    rfh_host = opts.host
    rfh_username = opts.username
    rfh_password = opts.password
    output_names = []
    # support "*.xml" of output files
    if ( opts.output == "*.xml" ):
        for item in os.listdir(dir):
            if os.path.isfile(item) and item.endswith('.xml'):
                output_names.append(item)
    else:
        for curr_name in opts.output.split(","):
            curr_path = os.path.join(dir, curr_name)
            output_names.append(curr_path)

    required_files = list(output_names)
    missing_files = [filename for filename in required_files if not os.path.exists(filename)]
    if missing_files:
        # We have files missing.
        exit("output.xml file is missing: {}".format(", ".join(missing_files)))

    # Read output.xml file
    result = ExecutionResult(*output_names)
    result.configure(stat_config={'suite_stat_level': 2,
                                  'tag_stat_combine': 'tagANDanother'})

    print("Capturing execution results, This may take few minutes...")

    test_stats = ExecutionStats()
    result.visit(test_stats)
    try:
        test_stats = test_stats.all
    except:
        test_stats = test_stats
    suite_total = test_stats.total_suite
    suite_pass = test_stats.passed_suite
    suite_fail = test_stats.failed_suite
    try:
        suite_skip = test_stats.skipped_suite
    except:
        suite_skip = 0
    stats = result.statistics
    try:
        stats_obj = stats.total.all
    except:
        stats_obj = stats.total
    total = stats_obj.total
    passed = stats_obj.passed
    failed = stats_obj.failed
    try:
        skipped = stats_obj.skipped
    except:
        skipped = 0

    elapsedtime = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=result.suite.elapsedtime)
    elapsedtime = get_time_in_min(elapsedtime.strftime("%X"))
    elapsedtime = float("{0:.2f}".format(elapsedtime))

    session = requests.Session()
    session.auth = (rfh_username, rfh_password)
    print("Getting project list")
    project_list = session.get(f"http://{rfh_host}/api/projects/").json()
    project_uuid = [x['uuid'] for x in project_list if x["name"]==opts.projectname][0]

    if project_uuid:
        print(f"Project{opts.projectname} found on server")
    
    execution_uuid = add_execution(session, rfh_host, opts.version, project_uuid, total, passed, failed, elapsedtime, suite_total, suite_pass, suite_fail, skipped, suite_skip, opts.projectname)
    result.visit(SuiteResults(session, rfh_host, project_uuid,execution_uuid))
    result.visit(TestMetrics(session, rfh_host, project_uuid,execution_uuid))

    print(f'Results for project: "{opts.projectname}" were stored under version: {opts.version} ')

class ExecutionStats(ResultVisitor):
    total_suite = 0
    passed_suite = 0
    failed_suite = 0
    skipped_suite = 0

    def start_suite(self, suite):
        suite_test_list = suite.tests
        if not suite_test_list:
            pass
        else:
            self.total_suite += 1
            if suite.status == "PASS":
                self.passed_suite += 1
            elif suite.status == "FAIL":
                self.failed_suite += 1
            else:
                self.skipped_suite += 1

class SuiteResults(ResultVisitor):

    def __init__(self, session, host, project_uuid, execution):
        self.session = session
        self.project_uuid = project_uuid
        self.execution = execution
        self.host = host

    def start_suite(self,suite):

        suite_test_list = suite.tests
        if not suite_test_list:
            pass
        else:
            suite_name = suite
            try:
                stats = suite.statistics.all
            except:
                stats = suite.statistics
            time = float("{0:.2f}".format(suite.elapsedtime / float(60000)))
            # TODO: Update skipped when functionality implemented
            try:
                suite_skipped = stats.skipped
            except:
                suite_skipped = 0
            add_suite_results(self.session, self.host, self.project_uuid, self.execution, str(suite_name), str(suite.status), int(stats.total), int(stats.passed), int(stats.failed), float(time), int(suite_skipped))

class TestMetrics(ResultVisitor):

    def __init__(self, session, host, project_uuid, execution_uuid):
        self.session = session
        self.project_uuid = project_uuid
        self.execution_uuid = execution_uuid
        self.host = host

    def visit_test(self, test):
        name = str(test.parent) + " - " + str(test)
        time = float("{0:.2f}".format(test.elapsedtime / float(60000)))
        error = str(test.message)
        add_test_results(self.session, self.host, self.project_uuid, self.execution_uuid, str(name), str(test.status), time, test.tags, error )

def get_time_in_min(time_str):
    h, m, s = time_str.split(':')
    ctime = int(h) * 3600 + int(m) * 60 + int(s)
    crtime = float("{0:.2f}".format(ctime/60))
    return crtime

def add_execution(sesion, host, version, project_uuid, total, passed, failed, ctime, suite_total, suite_pass, suite_fail, skipped, suite_skipped, projectname):
    payload = {
    "version": version,
    "total_time": ctime,
    "test_total": total,
    "tests_passed": passed,
    "tests_failed": failed,
    "tests_skipped": skipped
    }
    res = sesion.post(f'http://{host}/api/projects/{project_uuid}/execution', json=payload)
    if res.status_code == 401:
        raise Exception(f"Status code: {res.status_code}, Wrong username or password")
    if res.status_code == 201:
        return res.json()['uuid']
    else:
        raise Exception(f"Unexpected error, server returned status code {res.status_code}", res.content)

def add_suite_results(session, host,project_uuid, execution_uuid, name, status, total, passed, failed, duration, skipped):
    payload = {
    "name": name,
    "test_status": status,
    "total_time": duration,
    "test_total": total,
    "tests_passed": passed,
    "tests_failed": failed,
    "tests_skipped": skipped
    }
    res = session.post(f'http://{host}/api/projects/{project_uuid}/execution/{execution_uuid}/suites', json=payload)
    if not res.status_code == 201:
        raise Exception(f"Unexpected error, server returned status code {res.status_code}", res.content)

def add_test_results(session, host, project_uuid, execution_uuid, test, status, duration, tags, msg=""):
    dict_tags = []
    for tag in tags:
        dict_tags.append({'name': tag})
    payload = {
    "test_name": test,
    "test_status": status,
    "test_time": duration,
    "error_message": msg,
    "tag": dict_tags
    }
    res = session.post(f'http://{host}/api/projects/{project_uuid}/execution/{execution_uuid}/tests', json=payload)
    if not res.status_code == 201:
        raise Exception(f"Unexpected error, server returned status code {res.status_code}", res.content)

def main():
    args = parse_options()
    print(args)
    rfhistoric_parser(args)

if __name__=="__main__":
    main()