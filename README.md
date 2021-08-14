# Chocs - Parsed body middleware <br>[![CI](https://github.com/kodemore/chocs-parsed-body/actions/workflows/main.yaml/badge.svg)](https://github.com/kodemore/chocs-parsed-body/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chocs-parsed-body/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/chocs-parsed-body/actions/workflows/release.yml) [![codecov](https://codecov.io/gh/kodemore/chocs-parsed-body/branch/main/graph/badge.svg?token=Q5PL6W5DTB)](https://codecov.io/gh/kodemore/chocs-parsed-body) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Parsed body middleware for chocs package.

Parsed body middleware helps converting json/yaml data that comes with request into any dataclass. Please consider the following example:

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
    pet: Pet = request.parsed_body
    assert isinstance(pet, Pet)
    return HttpResponse(json.dumps(asdict(pet)))
```

In the above example we can see that `request.parsed_body` is no longer carrying `chocs.JsonHttpMessage` instead it was transformed into dataclass hinted inside the route definition (`Pet`).

## Strict mode

Strict mode is using initialiser defined in dataclass. Which means the request data
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

## Non-strict mode, aka: auto hydration

In non-strict mode `chocs` takes care of instantiating and hydrating your dataclasses. Complex and deeply
nested structures are supported as long as used types are supported by `chocs` hydration mechanism.
List of supported types can be found in [dataclass support library](/kodemore/chocs/wiki/dataclass-support#supported-data-types)

> Note: __post_init__ method is also called as a part of hydration process.
