# rfhistorian

Robot Framework Historian - free tool for agregating robot framework test results

## Installation

```sh
pipenv install
```

## First run

```sh
pipenv shell
python manage.py migrate
python manage.py runserver
```

## Run tests

```sh
python test_coverage.py
```

## Usage

UI allows to create projects, by design it's designed only to present test results. Test results should be uploaded using REST API

Project - GET/POST

```
api/projects/

POST data = 
{
    "name": 
        "This field is required. - <string>"
    ,
    "description": 
        "This field is required. - <string>"
  
}

```

Suite Execution - POST/GET - each project can have multiple executions. This endpoint is responsible for adding new execution.

```
api/projects/<uuid:project_uuid>/execution/

POST data = 
{
    "version": 
        "This field is required. - <string>"
    ,
    "total_time": 
        "This field is required. - <float>"
    ,
    "test_total": 
        "This field is required. - <int>"
    ,
    "tests_passed": 
        "This field is required. - <int>"
    ,
    "tests_failed": [
        "This field is required. - <int>"
    ,
    "tests_skipped": [
        "This field is required. - <int>"
  
}

```

Suites - POST/GET - each execution contains test suites.

```
api/projects/<uuid:project_uuid>/execution/<uuid:execution_uuid>/suites

POST data = 

{
    "name": 
        "This field is required. - <string>"
    ,
    "test_status": 
        "This field is required. - <string:["PASS|FAIL|SKIP"]>"
    ,
    "total_time": 
        "This field is required. - <float>"
    ,
    "test_total": 
        "This field is required. - <int>"
    ,
    "tests_passed": 
        "This field is required. - <int>"
    ,
    "tests_failed": 
        "This field is required. - <int>"
    ,
    "tests_skipped": 
        "This field is required. - <int>"
  
}

```

Tests - POST/GET - single test execution

```
api/projects/<uuid:project_uuid>/execution/<uuid:execution_uuid>/tests

POST data = 

{
    "test_name": 
        "This field is required. - <string>"
    ,
    "test_status": 
        "This field is required. - <string:["PASS|FAIL|SKIP"]>"
    ,
    "test_time": 
        "This field is required. - <float>"
    ,
    "error_message": 
        "This field is not required. - <string>"
    
    "tag":  
        "This field is not required. - <list:stings>"
    }
}

```