# SciCat Landingpage Sidecar Container

This sidecar container allows resolving download links and other information through the SciCat landing page, using content negotiation for `ld+json` and `metalink4+xml`. In addition, it embeds the `ld+json` in the Angular HTML of the landing page, making the metadata available for crawlers.

## `ld+json` for Crawlers

To extract the `ld+json` metadata for crawlers, you can use the following command:

```bash
curl -s https://public-doi-dev.desy.de/detail/10.83065%2F9d290825-4df8-46e2-92aa-d74510f0858a```

The ld+json metadata can be found inside the <script type='application/ld+json'>...</script> tag.

## Content Negotiation

For content negotiation, you can request either ld+json or metalink4+xml metadata using the following commands:

Request ld+json:
```bash
curl -sH "Accept: application/ld+json" https://public-doi-dev.desy.de/detail/10.83065%2F9d290825-4df8-46e2-92aa-d74510f0858a | jq```

Request metalink4+xml:
```bash
curl -sH "Accept: application/metalink4+xml" https://public-doi-dev.desy.de/detail/10.83065%2F9d290825-4df8-46e2-92aa-d74510f0858a | xmllint -format -```

