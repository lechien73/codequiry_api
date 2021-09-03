# Codequiry SDK

We rewrote the Codequiry SDK because theirs was broken.

## Usage

You need to create an instance using the Codequiry API key:

```python
from codequiry import Codechecker

cq = Codechecker(API_KEY)
```

The methods are all documented with docstrings in the `codequiry.py` file, but to run a plagiarism check, use the following process:

1. Create the check: `cq.create_check(NAME, LANGUAGE)` where `NAME` is a descriptive label and `LANGUAGE` is a language code. This returns a `CHECK_ID`, which you'll need to use to refer to the check later on.
2. Upload files to the check: `cq.upload(CHECK_ID, FILE_PATH)` where `CHECK_ID` is the ID returned from step 1, and `FILE_PATH` is the path to a zip file.
3. After the file is uploaded, start the check `cq.run_check(CHECK_ID)`
4. Periodically monitor the status of the check with `cq.check_status(CHECK_ID)`

You can get the account details and number of pro-checks remaining with `cq.get_account_details()`

-----
Matt Rudge<br/>
3rd September, 2021