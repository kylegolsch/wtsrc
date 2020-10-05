# Contents

Copy <u>wtsrc.yml</u> into your project's tsrc manifest repo next to <u>manifest.yml</u>

Example scripts are in the folder <u>scripts</u>.  The scripts folder can be copied next to the wtsrc.yml to run the example file.


## Failures
```sh
wtsrc show           
Running pre-action: python scripts/exampleFail.py
Running Command: python scripts/exampleFail.py
OK: some fake operation
NG: something didn't work right... exitting with status code 1
Fatal Error: python scripts/exampleFail.py exited unsuccessfully (1)
```

## Actions

```sh
wtsrc run-action sample-action
Action:  python scripts/sampleAction.py
Running Command: python scripts/sampleAction.py
OK: Sample Action Run
```