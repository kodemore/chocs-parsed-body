# Chocs - Parsed body middleware <br>[![PyPI version](https://badge.fury.io/py/chocs-middleware.parsed-body.svg)](https://pypi.org/project/chocs-middleware.parsed-body/) [![CI](https://github.com/kodemore/chocs-parsed-body/actions/workflows/main.yaml/badge.svg)](https://github.com/kodemore/chocs-parsed-body/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chocs-parsed-body/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/chocs-parsed-body/actions/workflows/release.yml) [![codecov](https://codecov.io/gh/kodemore/chocs-parsed-body/branch/main/graph/badge.svg?token=Q5PL6W5DTB)](https://codecov.io/gh/kodemore/chocs-parsed-body) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Parsed body middleware for chocs package.

Parsed body middleware helps to convert json/yaml request payloads into dataclass. Parsed body middleware is build on
the top of [`chili`](https://github.com/kodemore/chili) package. It supports complex dataclass initialisation and extraction
and does not pollute your codebase as it is solely depends on built-in python dataclasses package.


## Installation

With pip,
```shell
pip install chocs-middleware.parsed_body
```
or through poetry
```shell
poetry add chocs-middleware.parsed_body
```

# Usage

Middleware can work in two ways:
- strict mode
- auto hydration

In `strict` mode middleware will only rely on defined initializer defined in your dataclasses. If arguments in request
payload are not exactly matching singnature of your initializer method it will fail.

In `auto hydration` mode middleware will ignore initializers defined in your dataclasses, but `__post_init__` is still 
called after data is hydrated into class. Auto hydration may fail in scenarios where property is defined as non-optional
and is missing in the request payload.

## Registering middleware

```python
from chocs_middleware.parsed_body import ParsedBodyMiddleware
from chocs import Application, HttpRequest, HttpResponse
from chili import asdict
from dataclasses import dataclass
import json

# You can define whether to use strict mode or not for all defined routes.
app = Application(ParsedBodyMiddleware(strict=False))


@dataclass
class Pet:
    id: str
    name: str


@app.post("/pets", parsed_body=Pet, strict=True)  # you can also override default strict mode inside the route
def create_pet(request: HttpRequest) -> HttpResponse:
    # You can try to catch exceptions while hydration happens
    try:
        pet: Pet = request.parsed_body
    except Exception:
        pet = None
    assert isinstance(pet, Pet)
    return HttpResponse(json.dumps(asdict(pet)))
```

In the above example we can see that `request.parsed_body` is no longer carrying `chocs.JsonHttpMessage` instead it was transformed into dataclass hinted inside the route definition (`Pet`).

### Strict mode

Strict mode is using initializer defined in a dataclass. Which means the request data
is simply unpacked and passed to your dataclass, so you have to manually transform 
nested data to dataclasses in order to conform your dataclass interface, for example:

```python
from chocs_middleware.parsed_body import ParsedBodyMiddleware
from chocs import Application, HttpRequest, HttpResponse
from dataclasses import dataclass
from typing import List

app = Application(ParsedBodyMiddleware())


@dataclass
class Tag:
    name: str
    id: str


@dataclass
class Pet:
    id: str
    name: str
    age: int
    tags: List[Tag]

    def __post_init__(self):  # post init might be used to reformat your data
        self.age = int(self.age)
        tmp_tags = self.tags
        self.tags = []
        for tag in tmp_tags:
            self.tags.append(Tag(**tag))


@app.post("/pets", parsed_body=Pet)
def create_pet(request: HttpRequest) -> HttpResponse:
    pet: Pet = request.parsed_body
    assert isinstance(pet.tags[0], Tag)
    assert isinstance(pet, Pet)
    return HttpResponse(pet.name)

```

### Auto hydration

In non-strict mode instantiating and hydrating your dataclasses happens automatically. Complex and deeply nested 
structures are supported as long as used types are supported by `chili` hydration mechanism.

List of supported types can be found in [chili's supported data types](https://github.com/kodemore/chili#supported-data-types)

> Note: __post_init__ method is also called as a part of hydration process.
