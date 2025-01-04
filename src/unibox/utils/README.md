# Utils

utility code that's often imported before everything else, so there wont't be a circular import:

- `constants`, `globals` are initialized at `__init__` before everything else

- `logger`: a pre-configured color logger with stack trace

- `s3_client`: s3 operations class used for s3 backend

- `utils`: other util functions

- `uni_peeker`: a "peeker" that provides previews for various datatypes, handy in notebooks