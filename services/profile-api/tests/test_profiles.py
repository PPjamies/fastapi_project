def create(client, payload):
    resp = client.post("/v1/profiles", json=payload)
    assert resp.status_code == 201, resp.json()
    return resp.json()


def error_fields(resp):
    return {err["loc"][-1] for err in resp.json()["detail"]}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "database": "ok"}


def test_create_and_get(client, new_profile):
    created = create(client, new_profile)
    assert created["email"] == "ada@example.com"  # normalized to lowercase
    assert created["id"]
    assert created["created_at"] and created["updated_at"]

    resp = client.get(f"/v1/profiles/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Ada"


def test_create_requires_fields(client):
    resp = client.post("/v1/profiles", json={"first_name": "Ada"})
    assert resp.status_code == 422
    assert {"last_name", "date_of_birth", "email"} <= error_fields(resp)


def test_create_rejects_bad_values(client, new_profile):
    bad = dict(new_profile, phone="555-1234", country="gb", date_of_birth="2999-01-01")
    resp = client.post("/v1/profiles", json=bad)
    assert resp.status_code == 422
    assert {"phone", "country", "date_of_birth"} <= error_fields(resp)


def test_create_rejects_unknown_fields(client, new_profile):
    resp = client.post("/v1/profiles", json=dict(new_profile, nickname="Countess"))
    assert resp.status_code == 422


def test_duplicate_email_is_case_insensitive(client, new_profile):
    create(client, new_profile)
    resp = client.post("/v1/profiles", json=dict(new_profile, email="ADA@example.com"))
    assert resp.status_code == 409


def test_get_missing_returns_404(client):
    resp = client.get("/v1/profiles/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Profile not found."}


def test_patch_updates_only_given_fields(client, new_profile):
    created = create(client, new_profile)
    resp = client.patch(f"/v1/profiles/{created['id']}", json={"city": "Paris", "country": "FR"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["city"] == "Paris" and body["country"] == "FR"
    assert body["last_name"] == "Lovelace"


def test_patch_can_clear_optional_field(client, new_profile):
    created = create(client, new_profile)
    resp = client.patch(f"/v1/profiles/{created['id']}", json={"phone": None})
    assert resp.status_code == 200
    assert resp.json()["phone"] is None


def test_patch_cannot_clear_required_field(client, new_profile):
    created = create(client, new_profile)
    resp = client.patch(f"/v1/profiles/{created['id']}", json={"email": None})
    assert resp.status_code == 422


def test_patch_email_conflict(client, new_profile):
    create(client, new_profile)
    other = create(client, dict(new_profile, email="grace@example.com"))
    resp = client.patch(f"/v1/profiles/{other['id']}", json={"email": "ada@example.com"})
    assert resp.status_code == 409


def test_delete(client, new_profile):
    created = create(client, new_profile)
    assert client.delete(f"/v1/profiles/{created['id']}").status_code == 204
    assert client.get(f"/v1/profiles/{created['id']}").status_code == 404
    assert client.delete(f"/v1/profiles/{created['id']}").status_code == 404


def test_list_pagination_and_filters(client, new_profile):
    for i in range(25):
        create(client, dict(new_profile, email=f"user{i}@example.com",
                            last_name="Hopper" if i < 3 else "Lovelace"))

    first = client.get("/v1/profiles").json()
    assert first["total"] == 25 and first["page"] == 1
    assert first["page_size"] == 20 and len(first["items"]) == 20

    second = client.get("/v1/profiles", params={"page": 2}).json()
    assert len(second["items"]) == 5

    assert client.get("/v1/profiles", params={"last_name": "hopper"}).json()["total"] == 3
    assert client.get("/v1/profiles", params={"email": "USER7@example.com"}).json()["total"] == 1


def test_list_rejects_page_size_over_max(client):
    assert client.get("/v1/profiles", params={"page_size": 101}).status_code == 422


def test_openapi_spec_lists_endpoints(client):
    spec = client.get("/openapi.json").json()
    assert spec["info"]["version"] == "1.0.0"
    assert {"/v1/profiles", "/v1/profiles/{profile_id}", "/health"} <= set(spec["paths"])
