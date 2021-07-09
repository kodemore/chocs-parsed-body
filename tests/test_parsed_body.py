import json
from dataclasses import dataclass

import pytest
from chocs import Application, HttpMethod, HttpRequest, HttpResponse

from chocs_middleware.parsed_body import ParsedBodyMiddleware


@dataclass
class Pet:
    name: str
    tag: str
    id: str


def _mockup_pet_endpoint(app: Application) -> None:
    @app.post("/pets", parsed_body=Pet)
    def create_pet(request: HttpRequest) -> HttpResponse:
        pet = request.parsed_body  # type: Pet
        assert isinstance(pet, Pet)
        return HttpResponse(pet.name)


def test_successfully_map_parsed_body_in_strict_mode() -> None:
    # given
    app = Application(ParsedBodyMiddleware(strict=True))
    _mockup_pet_endpoint(app)
    valid_body = json.dumps(
        {
            "name": "Bobek",
            "tag": "test",
            "id": 1,
        }
    )

    # when
    response = app(
        HttpRequest(
            HttpMethod.POST,
            "/pets",
            body=valid_body,
            headers={"content-type": "application/json"},
        )
    )

    # then
    assert str(response) == "Bobek"


def test_fail_map_parsed_body_in_strict_mode() -> None:
    # given
    app = Application(ParsedBodyMiddleware(strict=True))
    _mockup_pet_endpoint(app)
    invalid_body = json.dumps(
        {"name": "Bobek", "tag": "test", "id": 1, "unknown_property": "unknown_value"}
    )

    # then
    with pytest.raises(TypeError):
        app(
            HttpRequest(
                HttpMethod.POST,
                "/pets",
                body=invalid_body,
                headers={"content-type": "application/json"},
            )
        )


@pytest.mark.parametrize("body, expected", [
    [
        # invalid body - too many properties
        {"name": "Bobek", "tag": "test", "id": 1, "unknown_property": "unknown_value"},
        "Bobek",
    ],
    [
        # valid body
        {"name": "Bobek", "tag": "test", "id": 1},
        "Bobek",
    ]
])
def test_successfully_map_parsed_body_in_non_strict_mode(body: dict, expected: str) -> None:
    # given
    app = Application(ParsedBodyMiddleware(strict=False))
    _mockup_pet_endpoint(app)

    # when
    response = app(
        HttpRequest(
            HttpMethod.POST,
            "/pets",
            body=json.dumps(body),
            headers={"content-type": "application/json"},
        )
    )

    # then
    assert str(response) == expected


def test_fail_when_non_dataclass_selected_as_target() -> None:
    # given
    app = Application(ParsedBodyMiddleware(strict=False))

    @app.post("/pets", parsed_body=int)
    def create_pet(request: HttpRequest) -> HttpResponse:
        pet = request.parsed_body
        assert isinstance(pet, int)
        return HttpResponse(pet)

    body = {
        "name": "Bobek",
        "tag": "test",
        "id": 1,
    }

    # then
    with pytest.raises(ValueError):
        app(
            HttpRequest(
                HttpMethod.POST,
                "/pets",
                body=json.dumps(body),
                headers={"content-type": "application/json"},
            )
        )
