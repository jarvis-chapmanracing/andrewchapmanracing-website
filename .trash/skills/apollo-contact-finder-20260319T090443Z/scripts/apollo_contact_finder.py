#!/usr/bin/env python3
"""Apollo contact finder helper.

Core workflows:
1. Company -> people
2. Company + person -> contact info

This script is designed to be dependency-free and uses the Apollo API key from
APOLLO_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE_URL = "https://api.apollo.io/api/v1"
DEFAULT_TIMEOUT = 45


class ApolloError(Exception):
    def __init__(self, message: str, *, status: int | None = None, payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.status = status
        self.payload = payload or {}


class ApolloClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _request(self, method: str, path: str, *, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = BASE_URL + path
        if params:
            filtered = {k: v for k, v in params.items() if v not in (None, "", [], {})}
            if filtered:
                url += "?" + urllib.parse.urlencode(filtered, doseq=True)

        payload = None
        headers = {
            "x-api-key": self.api_key,
            "accept": "application/json",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "User-Agent": "apollo-contact-finder/1.0",
        }
        if body is not None:
            payload = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = {"raw": raw}

            error_code = parsed.get("error_code")
            message = parsed.get("error") or parsed.get("message") or f"HTTP {exc.code}"
            if error_code == "API_INACCESSIBLE":
                message = (
                    f"{message} This Apollo key cannot access {path}. "
                    "The current plan appears to block this endpoint."
                )
            raise ApolloError(message, status=exc.code, payload=parsed) from exc
        except urllib.error.URLError as exc:
            raise ApolloError(f"Network error calling Apollo: {exc}") from exc

    def organization_enrich(self, *, domain: str | None = None) -> dict[str, Any]:
        if not domain:
            raise ApolloError("organization_enrich requires --domain")
        return self._request("GET", "/organizations/enrich", params={"domain": domain})

    def people_search(
        self,
        *,
        domain: str | None = None,
        company: str | None = None,
        titles: list[str] | None = None,
        seniorities: list[str] | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> dict[str, Any]:
        if not domain and not company:
            raise ApolloError("find-people requires --domain or --company")

        body: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if domain:
            body["q_organization_domains"] = domain
        if company:
            body["q_organization_name"] = company
        if titles:
            body["person_titles"] = titles
        if seniorities:
            body["person_seniorities"] = seniorities
        return self._request("POST", "/mixed_people/api_search", body=body)

    def people_match(
        self,
        *,
        name: str,
        domain: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        reveal_phone_number: bool = False,
        reveal_personal_emails: bool = False,
    ) -> dict[str, Any]:
        if not name and not (first_name and last_name):
            raise ApolloError("find-contact requires --name or both --first-name and --last-name")
        params: dict[str, Any] = {
            "reveal_personal_emails": str(reveal_personal_emails).lower(),
            "reveal_phone_number": str(reveal_phone_number).lower(),
        }
        if name:
            params["name"] = name
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if domain:
            params["domain"] = domain
        return self._request("POST", "/people/match", params=params)


def require_api_key() -> str:
    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key:
        raise ApolloError("APOLLO_API_KEY is not set")
    return api_key


def summarize_org(payload: dict[str, Any]) -> dict[str, Any]:
    org = payload.get("organization") or {}
    return {
        "id": org.get("id"),
        "name": org.get("name"),
        "website_url": org.get("website_url"),
        "linkedin_url": org.get("linkedin_url"),
        "twitter_url": org.get("twitter_url"),
        "primary_phone": org.get("primary_phone") or org.get("phone"),
        "industry": org.get("industry"),
        "estimated_num_employees": org.get("estimated_num_employees"),
        "estimated_annual_revenue": org.get("estimated_annual_revenue"),
        "founded_year": org.get("founded_year"),
        "city": org.get("city"),
        "state": org.get("state"),
        "country": org.get("country"),
        "raw": payload,
    }


def summarize_people_search(payload: dict[str, Any]) -> dict[str, Any]:
    people = []
    raw_people = payload.get("people") or payload.get("contacts") or []
    for person in raw_people:
        org = person.get("organization") or {}
        people.append(
            {
                "id": person.get("id"),
                "name": person.get("name") or " ".join(filter(None, [person.get("first_name"), person.get("last_name")])),
                "first_name": person.get("first_name"),
                "title": person.get("title"),
                "linkedin_url": person.get("linkedin_url"),
                "has_email": person.get("has_email"),
                "has_direct_phone": person.get("has_direct_phone"),
                "city": person.get("city"),
                "state": person.get("state"),
                "country": person.get("country"),
                "organization": {
                    "name": org.get("name"),
                    "website_url": org.get("website_url"),
                    "linkedin_url": org.get("linkedin_url"),
                },
            }
        )
    return {
        "total_entries": payload.get("total_entries") or payload.get("pagination", {}).get("total_entries"),
        "page": payload.get("page") or payload.get("pagination", {}).get("page"),
        "per_page": payload.get("per_page") or payload.get("pagination", {}).get("per_page"),
        "people": people,
        "raw": payload,
    }


def summarize_person_match(payload: dict[str, Any]) -> dict[str, Any]:
    person = payload.get("person") or {}
    contact = payload.get("contact") or person.get("contact") or {}
    organization = payload.get("organization") or person.get("organization") or {}
    return {
        "matched": bool(person),
        "person": {
            "id": person.get("id"),
            "name": person.get("name"),
            "first_name": person.get("first_name"),
            "last_name": person.get("last_name"),
            "title": person.get("title"),
            "headline": person.get("headline"),
            "linkedin_url": person.get("linkedin_url"),
            "twitter_url": person.get("twitter_url"),
            "email": person.get("email") or contact.get("email"),
            "email_status": person.get("email_status") or contact.get("email_status"),
            "email_source": contact.get("email_source"),
            "phone": contact.get("sanitized_phone") or person.get("sanitized_phone"),
            "city": person.get("city"),
            "state": person.get("state"),
            "country": person.get("country"),
        },
        "organization": {
            "id": organization.get("id") or person.get("organization_id") or contact.get("organization_id"),
            "name": organization.get("name") or contact.get("organization_name"),
            "website_url": organization.get("website_url"),
            "linkedin_url": organization.get("linkedin_url"),
            "primary_phone": organization.get("primary_phone") or organization.get("phone"),
        },
        "raw": payload,
    }


def cmd_access_check(client: ApolloClient, _args: argparse.Namespace) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    tests = {
        "organization_enrich": lambda: client.organization_enrich(domain="apollo.io"),
        "people_search": lambda: client.people_search(domain="apollo.io", per_page=1),
        "people_match": lambda: client.people_match(name="Tim Zheng", domain="apollo.io"),
    }
    for key, fn in tests.items():
        try:
            fn()
            checks[key] = {"ok": True}
        except ApolloError as exc:
            checks[key] = {
                "ok": False,
                "status": exc.status,
                "error": str(exc),
                "error_code": exc.payload.get("error_code"),
            }
    return checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apollo contact finder helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_access = sub.add_parser("access-check", help="Check which Apollo endpoints this key can access")
    p_access.add_argument("--pretty", action="store_true")

    p_company = sub.add_parser("company-lookup", help="Enrich one company by domain")
    p_company.add_argument("--domain", required=True)
    p_company.add_argument("--pretty", action="store_true")

    p_people = sub.add_parser("find-people", help="Find people at a company")
    p_people.add_argument("--domain")
    p_people.add_argument("--company")
    p_people.add_argument("--title", action="append", dest="titles")
    p_people.add_argument("--seniority", action="append", dest="seniorities")
    p_people.add_argument("--page", type=int, default=1)
    p_people.add_argument("--per-page", type=int, default=10)
    p_people.add_argument("--pretty", action="store_true")

    p_contact = sub.add_parser("find-contact", help="Find one person and their contact details")
    p_contact.add_argument("--domain")
    p_contact.add_argument("--name")
    p_contact.add_argument("--first-name")
    p_contact.add_argument("--last-name")
    p_contact.add_argument("--reveal-phone-number", action="store_true")
    p_contact.add_argument("--reveal-personal-emails", action="store_true")
    p_contact.add_argument("--pretty", action="store_true")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        client = ApolloClient(require_api_key())
        if args.command == "access-check":
            result = cmd_access_check(client, args)
        elif args.command == "company-lookup":
            result = summarize_org(client.organization_enrich(domain=args.domain))
        elif args.command == "find-people":
            result = summarize_people_search(
                client.people_search(
                    domain=args.domain,
                    company=args.company,
                    titles=args.titles,
                    seniorities=args.seniorities,
                    page=args.page,
                    per_page=args.per_page,
                )
            )
        elif args.command == "find-contact":
            result = summarize_person_match(
                client.people_match(
                    name=args.name or "",
                    first_name=args.first_name,
                    last_name=args.last_name,
                    domain=args.domain,
                    reveal_phone_number=args.reveal_phone_number,
                    reveal_personal_emails=args.reveal_personal_emails,
                )
            )
        else:
            parser.error(f"Unknown command: {args.command}")
            return 2
    except ApolloError as exc:
        error = {
            "ok": False,
            "error": str(exc),
            "status": exc.status,
            "error_code": exc.payload.get("error_code") if exc.payload else None,
            "details": exc.payload or None,
        }
        print(json.dumps(error, indent=2))
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps({"ok": True, "result": result}, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
