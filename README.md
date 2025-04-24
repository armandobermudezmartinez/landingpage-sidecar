# DOI resolver for Scicat Landingpage

This sidecar container allows resolving download links and other information through the Scicat landingpage, using context negociation for ld+json and metalink4+xml. In addition it embeds the ld+json in the angular html of the landingpage, making the metadata available for crawlers.

ld+json for crawlers:

curl -s https://public-doi-dev.desy.de/detail/10.83065%2F9d290825-4df8-46e2-92aa-d74510f0858a
The ld+json can be now found in the <head><script type='application/ld+json'>    </head></script>.

Content negociation: 

curl -sH "Accept: application/ld+json" https://public-doi-dev.desy.de/detail/10.83065%2F9d290825-4df8-46e2-92aa-d74510f0858a | jq
curl -sH "Accept: application/metalink4+xml" https://public-doi-dev.desy.de/detail/10.83065%2F9d290825-4df8-46e2-92aa-d74510f0858a | xmllint -format -

